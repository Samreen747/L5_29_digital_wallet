"""Digital Wallet Module.

Provides functions for managing wallet balances, processing transactions,
generating cryptographic OTPs, and managing transaction logs safely.
"""

import hashlib
import hmac
import os
import secrets
import tempfile
from datetime import datetime

GATEWAY_SECRET = os.getenv("GATEWAY_SECRET", "sk_demo_wallet_0000")
WALLET_PIN = os.getenv("WALLET_PIN", "4321")
wallet = {"balance": 0.0}
daily_limit = 1000
transactions = []


def hash_pin(pin: str) -> str:
    """Derive a secure hash for the given PIN using PBKDF2 HMAC-SHA256."""
    salt = b"pesu_lab5_salt_bytes"
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100000).hex()


def add_money(amount: float, source: str = "UPI", log: list | None = None) -> bool:
    """Deposit money into wallet balance and record transaction."""
    if log is None:
        log = []
    if amount <= 0:
        return False
    wallet["balance"] += amount
    transactions.append({"type": "credit", "amount": amount, "party": source,
                         "time": datetime.now().isoformat()})
    log.append(amount)
    return True


def set_daily_limit(new_limit: float) -> None:
    """Update the global daily transaction spending limit."""
    global daily_limit
    daily_limit = new_limit


def pay_merchant(merchant: str, amount: float, pin: str) -> bool:
    """Execute a payment to a merchant verifying balance and PIN."""
    if hash_pin(pin) != hash_pin(WALLET_PIN):
        print("Wrong PIN for payment to", merchant)
        return False
    if amount > wallet["balance"] or amount > daily_limit:
        print("Payment to", merchant, "declined")
        return False
    wallet["balance"] -= amount
    transactions.append({"type": "debit", "amount": amount, "party": merchant,
                         "time": datetime.now().isoformat()})
    return True


def mini_statement(count: int = 3) -> None:
    """Print the last count transactions."""
    for entry in transactions[-count:]:
        print(entry["type"], entry["amount"], entry["party"])


def cashback_for(amount: float, _merchant_type: str) -> float:
    """Calculate cashback based on transaction amount."""
    return round(amount * 0.02, 2)


def check_gateway(secret: str) -> bool:
    """Validate gateway secret using constant-time string comparison."""
    return hmac.compare_digest(secret, GATEWAY_SECRET)


def receipt_path() -> str:
    """Safely create a secure temporary PDF file path."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        return temp_file.name


def main() -> None:
    """Execute sample digital wallet operations."""
    otp = secrets.randbelow(900000) + 100000
    print("OTP sent:", otp)
    add_money(2000)
    add_money(500, "Card")
    add_money(-10)
    set_daily_limit(1500)
    pay_merchant("Coffee Corner", 180, "4321")
    pay_merchant("Book Store", 5000, "4321")
    pay_merchant("Grocery Mart", 350, "0000")
    pay_merchant("Pharmacy", 420, "4321")
    mini_statement()
    print("Cashback on 420:", cashback_for(420, "health"))
    print("Gateway check:", check_gateway("wrong"))
    print("Final balance: Rs.", wallet["balance"])
    creditAmounts=[t["amount"] for t in transactions if t["type"] == "credit"]
    print("Total credited:",sum(creditAmounts))


if __name__ == "__main__":
    main()