#!/usr/bin/env python3
import os, json, argparse, requests, binascii
from bech32 import bech32_encode, convertbits
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder
from decimal import Decimal as D

CONFIG_PATH = os.path.expanduser("~/.bunc_wallet.json")
DEFAULT_SERVER = os.environ.get("NOVA_SERVER", "http://mainnet.nova-chain.org")

# -------------------------
# Storage helpers
# -------------------------
def save_wallet(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f)
    print("✅ Wallet saved:", CONFIG_PATH)

def load_wallet():
    if not os.path.exists(CONFIG_PATH):
        print("❌ No wallet found. Run `nova keygen` first.")
        raise SystemExit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

# -------------------------
# Utils & crypto
# -------------------------
def to_hex(b: bytes) -> str:
    return binascii.hexlify(b).decode()

def bech32_addr_from_pubkey(pubkey_hex: str) -> str:
    pk = bytes.fromhex(pubkey_hex)
    five = convertbits(pk, 8, 5, True)
    return bech32_encode("nova", five)

def sign(sk_hex: str, msg: str) -> str:
    sk = SigningKey(bytes.fromhex(sk_hex))
    sig = sk.sign(msg.encode()).signature  # 64 bytes
    return to_hex(sig)

def canon_amount(amount: float | str) -> str:
    # match server: 9 dp
    return f"{float(amount):.9f}"

def to_base_units(amount_human: float | str, decimals: int = 9) -> int:
    d = D(str(amount_human))
    scale = D(10) ** int(decimals)
    return int((d * scale).quantize(D("1")))

def from_base_units(amount_base: int, decimals: int = 9) -> str:
    return str(D(amount_base) / (D(10) ** int(decimals)))

# -------------------------
# Server helpers
# -------------------------
def peek_nonce(server_url: str, address: str) -> int:
    r = requests.get(f"{server_url}/api/nonce/peek/{address}", timeout=10)
    r.raise_for_status()
    return int(r.json()["next"])

# -------------------------
# Canonical signed messages (must match server)
# -------------------------
def build_msg(frm: str, to: str, amount: str, nonce: int) -> str:
    return f"nova|transfer|from={frm}|to={to}|amount={amount}|nonce={nonce}"

def build_token_msg(frm: str, to: str, symbol: str, amount_base: int, nonce: int) -> str:
    return f"nova|token_transfer|sym={symbol.upper()}|from={frm}|to={to}|amount_base={amount_base}|nonce={nonce}"

def build_token_create_msg(frm: str, symbol: str, decimals: int, uri: str, nonce: int) -> str:
    u = uri or ""
    return f"nova|token_create|from={frm}|sym={symbol.upper()}|dec={int(decimals)}|uri={u}|nonce={nonce}"

def build_token_mint_message(minter_addr: str, symbol: str, to_addr: str, amount_base: int, nonce: int) -> str:
    return (f"nova|token_mint|from={minter_addr}|sym={symbol.upper()}|to={to_addr}"
            f"|amount_base={int(amount_base)}|nonce={nonce}")

# -------------------------
# Wallet ops
# -------------------------
def keygen():
    """Generate ed25519 wallet, register pubkey with server, save secret locally."""
    sk = SigningKey.generate()
    pk = sk.verify_key
    pk_hex = pk.encode(encoder=HexEncoder).decode()

    r = requests.post(f"{DEFAULT_SERVER}/api/wallet/register", json={"pubkey_hex": pk_hex}, timeout=10)
    if r.status_code != 200:
        print("❌ Failed to register wallet:", r.text)
        return
    addr = r.json()["address"]  # nova1…

    data = {
        "server_url": DEFAULT_SERVER,
        "address": addr,
        "pubkey_hex": pk_hex,
        "secret_key_hex": sk.encode(encoder=HexEncoder).decode(),  # 64 hex
    }
    save_wallet(data)
    print(f"🧾 Created & registered wallet {addr}")

def balance(address: str | None = None):
    w = load_wallet()
    addr = address or w["address"]
    r  = requests.get(f"{w['server_url']}/api/balance/{addr}", timeout=10)
    rT = requests.get(f"{w['server_url']}/api/wallet/tokens/{addr}", timeout=10)

    if r.status_code == 200:
        j = r.json()
        print(f"💰 balance: {j['balance']} NOVA")
    else:
        print("❌ Failed to fetch balance:", r.text)

    if rT.status_code == 200:
        jt = rT.json()
        tokens = jt.get("tokens", [])
        if tokens:
            print("🪙 Tokens:")
            for t in tokens:
                symbol = t.get("symbol", "?")
                amount = t.get("amount", "0")
                name = t.get("name", symbol)
                print(f"  • ({name}): {amount} {symbol}")

# -------------------------
# NOVA coin transfer
# -------------------------
def transfer(to: str, amount: float):
    w = load_wallet()
    frm = w["address"]
    server = w["server_url"]
    amt = canon_amount(amount)
    nonce = peek_nonce(server, frm)
    msg = build_msg(frm, to, amt, nonce)
    sig_hex = sign(w["secret_key_hex"], msg)

    payload = {"from": frm, "to": to, "amount": amt, "nonce": nonce, "sig": sig_hex}
    r = requests.post(f"{server}/api/transfer", json=payload, timeout=10)
    if r.status_code == 200:
        j = r.json()
        print(f"✅ Transfer submitted. txid={j['txid']}  gas={j['gas']}")
    else:
        print("❌ Transfer failed:", r.text)

# -------------------------
# Token transfers (SPL-like)
# -------------------------
def token_transfer(to: str, amount: float, symbol: str, decimals: int = 9):
    w = load_wallet()
    frm = w["address"]
    server = w["server_url"]

    amount_base = to_base_units(amount, decimals)
    nonce = peek_nonce(server, frm)
    msg = build_token_msg(frm, to, symbol, amount_base, nonce)
    sig_hex = sign(w["secret_key_hex"], msg)

    payload = {
        "symbol": symbol.upper(),
        "from": frm,
        "to": to,
        "amount_base": amount_base,
        "nonce": nonce,
        "sig": sig_hex
    }
    r = requests.post(f"{server}/api/token/transfer", json=payload, timeout=10)
    if r.status_code == 200:
        j = r.json()
        if j.get("ok") and "txid" in j:
            print(f"✅ Token transfer submitted. txid={j['txid']}  gas={j.get('gas')}")
        else:
            print(f"✅ Token transfer ok. gas={j.get('gas')}")
    else:
        print("❌ Token transfer failed:", r.text)

# -------------------------
# Permissionless, signed Token Create / Mint
# -------------------------
def token_create_signed(symbol: str, name: str, decimals: int = 9, uri: str = ""):
    w = load_wallet()
    frm = w["address"]; server = w["server_url"]
    nonce = peek_nonce(server, frm)
    msg = build_token_create_msg(frm, symbol, decimals, uri, nonce)
    sig_hex = sign(w["secret_key_hex"], msg)

    payload = {
        "from": frm,
        "symbol": symbol.upper(),
        "name": name,
        "decimals": int(decimals),
        "uri": uri,
        "nonce": nonce,
        "sig": sig_hex,
    }
    r = requests.post(f"{server}/api/token/create", json=payload, timeout=10)
    if r.status_code == 200:
        j = r.json()
        print(f"✅ Token created: {j['symbol']} (dec={j['decimals']})  authority={j['mint_authority']}  gas={j['gas']}")
        if j.get("uri"): print(f"   uri: {j['uri']}")
    else:
        print("❌ Token create failed:", r.status_code, r.text)

def token_mint_signed(symbol: str, amount_human: D | float | str, to: str | None, decimals_hint: int = 9):
    w = load_wallet()
    minter = w["address"]; server = w["server_url"]
    if not to:
        to = minter
        print(f"ℹ️ No --to specified, defaulting to your wallet: {to}")

    amt_base = int((D(str(amount_human)) * (D(10) ** int(decimals_hint))).quantize(D("1")))
    nonce = peek_nonce(server, minter)
    msg   = build_token_mint_message(minter, symbol, to, amt_base, nonce)
    sig_hex = sign(w["secret_key_hex"], msg)

    payload = {
        "from": minter,
        "symbol": symbol.upper(),
        "to": to,
        "amount_base": amt_base,
        "nonce": nonce,
        "sig": sig_hex,
    }
    r = requests.post(f"{server}/api/token/mint", json=payload, timeout=10)
    if r.status_code == 200:
        j = r.json()
        print(f"✅ Minted {j['amount']} {j['symbol']} to {j['to']}  (gas {j['gas']} NOVA)")
    else:
        print("❌ Token mint failed:", r.status_code, r.text)

# -------------------------
# Dev-only legacy airdrop (coin mint)
# -------------------------
def airdrop(amount: float, to: str | None = None):
    w = load_wallet()
    target = to or w["address"]
    payload = {"to": target, "amount": canon_amount(amount)}
    r = requests.post(f"{w['server_url']}/api/mint", json=payload, timeout=10)
    if r.status_code == 200:
        j = r.json()
        print(f"🪂 Mint enqueued. txid={j['txid']}")
    else:
        print("❌ Mint failed:", r.text)

# -------------------------
# UX
# -------------------------
def show():
    w = load_wallet()
    print("📄 Wallet")
    print("  Address:", w["address"])
    print("  Server :", w["server_url"])

# -------------------------
# CLI
# -------------------------
def main():
    p = argparse.ArgumentParser(prog="nova", description="NOVA Wallet CLI")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("keygen", help="Generate a new nova1… wallet")

    sp = sub.add_parser("balance", help="Show wallet balance")
    sp.add_argument("--address", help="Address to query (defaults to your wallet)")

    tp = sub.add_parser("transfer", help="Send NOVA (signed)")
    tp.add_argument("--to", required=True, help="Recipient nova1… address")
    tp.add_argument("--amount", type=float, required=True)

    ap = sub.add_parser("airdrop", help="DEV: mint NOVA to an address via /api/mint (insecure)")
    ap.add_argument("--amount", type=float, required=True)
    ap.add_argument("--to", help="Target address (defaults to your wallet)")

    # Token transfer
    tkn = sub.add_parser("token-transfer", help="Send a token (signed)")
    tkn.add_argument("--symbol", required=True, help="Token symbol, e.g. LOG")
    tkn.add_argument("--to", required=True, help="Recipient nova1… address")
    amtgrp = tkn.add_mutually_exclusive_group(required=True)
    amtgrp.add_argument("--amount", type=float, help="Human amount (e.g., 1.23)")
    amtgrp.add_argument("--amount-base", type=int, help="Base units (integer)")
    tkn.add_argument("--decimals", type=int, default=9, help="Token decimals (default 9)")

    # Permissionless, signed token create
    tc = sub.add_parser("token-create", help="Create a token (signed; you become mint authority)")
    tc.add_argument("--symbol", required=True, help="Token symbol, e.g. LOG or wSOL")
    tc.add_argument("--name", required=True, help="Full token name")
    tc.add_argument("--decimals", type=int, default=9, help="Decimal precision")
    tc.add_argument("--uri", default="", help="Metadata URI (JSON)")

    # Permissionless, signed token mint (only mint authority)
    tm = sub.add_parser("token-mint", help="Mint tokens (signed; only mint authority)")
    tm.add_argument("--symbol", required=True, help="Token symbol, e.g. LOG or wSOL")
    tm.add_argument("--amount", type=float, required=True, help="Human amount (e.g., 12.5)")
    tm.add_argument("--to", help="Recipient nova1… address (defaults to your wallet)")
    tm.add_argument("--decimals", type=int, default=9, help="Hint for base conversion when signing")

    sub.add_parser("show", help="Show wallet info")

    args = p.parse_args()

    if args.cmd == "keygen":
        keygen()
    elif args.cmd == "balance":
        balance(args.address)
    elif args.cmd == "transfer":
        transfer(args.to, args.amount)
    elif args.cmd == "token-create":
        token_create_signed(args.symbol, args.name, args.decimals, args.uri)
    elif args.cmd == "token-mint":
        token_mint_signed(args.symbol, args.amount, args.to, args.decimals)
    elif args.cmd == "token-transfer":
        if args.amount_base is not None:
            # Convenience: if base provided, log human but sign with base via decimals hint
            token_transfer(
                to=args.to,
                amount=(args.amount_base / (10 ** args.decimals)),
                symbol=args.symbol,
                decimals=args.decimals
            )
        else:
            token_transfer(args.to, args.amount, args.symbol, args.decimals)
    elif args.cmd == "airdrop":
        airdrop(args.amount, args.to)
    elif args.cmd == "show":
        show()
    else:
        p.print_help()

if __name__ == "__main__":
    main()
