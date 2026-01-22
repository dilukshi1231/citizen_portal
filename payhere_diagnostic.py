#!/usr/bin/env python3
"""
PayHere Configuration Diagnostic Tool
Run this to verify your PayHere setup
"""

import hashlib

# Your credentials from app.py
MERCHANT_ID = "1233555"
MERCHANT_SECRET = "MzkwNDE1MzcwMTEwMDAwNjYxNTYzNDcxMzgyNTAyMjkzMTI4NDAwMQ=="

# Test values
TEST_ORDER_ID = "TEST12345"
TEST_AMOUNT = "25000.00"
TEST_CURRENCY = "LKR"

print("=" * 70)
print("🔍 PAYHERE CONFIGURATION DIAGNOSTIC")
print("=" * 70)

print("\n📋 Configuration:")
print(f"   Merchant ID: {MERCHANT_ID}")
print(f"   Merchant ID Type: {type(MERCHANT_ID)}")
print(f"   Merchant ID Length: {len(MERCHANT_ID)}")
print(f"   Merchant Secret: {MERCHANT_SECRET[:20]}... (truncated)")
print(f"   Merchant Secret Type: {type(MERCHANT_SECRET)}")
print(f"   Merchant Secret Length: {len(MERCHANT_SECRET)}")

print("\n🔐 Step 1: Hash Merchant Secret")
merchant_secret_md5 = hashlib.md5(MERCHANT_SECRET.encode('utf-8')).hexdigest()
print(f"   Lowercase: {merchant_secret_md5}")
merchant_secret_md5_upper = merchant_secret_md5.upper()
print(f"   Uppercase: {merchant_secret_md5_upper}")
print(f"   Length: {len(merchant_secret_md5_upper)}")

print("\n🔐 Step 2: Build Hash String")
hash_string = f"{MERCHANT_ID}{TEST_ORDER_ID}{TEST_AMOUNT}{TEST_CURRENCY}{merchant_secret_md5_upper}"
print(f"   Hash String: {hash_string}")
print(f"   Length: {len(hash_string)}")

print("\n   Breakdown:")
print(f"   - '{MERCHANT_ID}' (Merchant ID)")
print(f"   - '{TEST_ORDER_ID}' (Order ID)")
print(f"   - '{TEST_AMOUNT}' (Amount)")
print(f"   - '{TEST_CURRENCY}' (Currency)")
print(f"   - '{merchant_secret_md5_upper}' (Secret MD5)")

print("\n🔐 Step 3: Generate Final Hash")
final_hash_lower = hashlib.md5(hash_string.encode('utf-8')).hexdigest()
print(f"   Lowercase: {final_hash_lower}")
final_hash_upper = final_hash_lower.upper()
print(f"   Uppercase: {final_hash_upper}")
print(f"   Length: {len(final_hash_upper)}")

print("\n✅ Validation:")
checks = {
    "Merchant ID is string": isinstance(MERCHANT_ID, str),
    "Merchant ID not empty": bool(MERCHANT_ID),
    "Merchant Secret not empty": bool(MERCHANT_SECRET),
    "Amount format correct": "." in TEST_AMOUNT and len(TEST_AMOUNT.split(".")[1]) == 2,
    "Currency is LKR": TEST_CURRENCY == "LKR",
    "Final hash is 32 chars": len(final_hash_upper) == 32,
    "Final hash is uppercase": final_hash_upper.isupper(),
    "Secret MD5 is 32 chars": len(merchant_secret_md5_upper) == 32
}

for check, result in checks.items():
    symbol = "✓" if result else "✗"
    print(f"   {symbol} {check}: {result}")

print("\n" + "=" * 70)
print("EXPECTED PAYHERE PAYMENT OBJECT:")
print("=" * 70)
print(f"""{{
    "sandbox": true,
    "merchant_id": "{MERCHANT_ID}",
    "order_id": "{TEST_ORDER_ID}",
    "items": "Test Item",
    "amount": "{TEST_AMOUNT}",
    "currency": "{TEST_CURRENCY}",
    "hash": "{final_hash_upper}",
    "first_name": "Test",
    "last_name": "Customer",
    "email": "test@example.com",
    "phone": "0771234567",
    "address": "Test Address",
    "city": "Colombo",
    "country": "Sri Lanka"
}}""")

print("\n" + "=" * 70)
print("🚨 COMMON ISSUES:")
print("=" * 70)
print("1. 'Unauthorized payment request' usually means:")
print("   - Hash mismatch (case sensitivity, formatting)")
print("   - Merchant ID/Secret mismatch with PayHere sandbox account")
print("   - Amount formatting incorrect (must be X.XX)")
print()
print("2. Verify your PayHere sandbox account:")
print("   - Login to https://sandbox.payhere.lk/")
print("   - Check Merchant ID matches exactly")
print("   - Check Merchant Secret matches exactly")
print("   - Ensure account is active and verified")
print()
print("3. Test with PayHere's test card:")
print("   - Card: 5303732372101006")
print("   - Expiry: 12/25")
print("   - CVV: 123")
print("=" * 70)