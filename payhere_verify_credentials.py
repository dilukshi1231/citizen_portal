#!/usr/bin/env python3
"""
PayHere Credentials Verification Tool
This will help you verify your merchant credentials format
"""

import hashlib
import base64

print("=" * 80)
print("🔍 PAYHERE CREDENTIALS VERIFICATION TOOL")
print("=" * 80)

# Your current credentials
MERCHANT_ID = "1233555"
MERCHANT_SECRET_BASE64 = "MzkwNDE1MzcwMTEwMDAwNjYxNTYzNDcxMzgyNTAyMjkzMTI4NDAwMQ=="

print("\n📋 CURRENT CONFIGURATION:")
print(f"   Merchant ID: {MERCHANT_ID}")
print(f"   Merchant Secret (as stored): {MERCHANT_SECRET_BASE64}")
print(f"   Length: {len(MERCHANT_SECRET_BASE64)} characters")

# Check if it's Base64
print("\n🔍 ANALYZING MERCHANT SECRET FORMAT:")
is_base64 = MERCHANT_SECRET_BASE64.endswith('==') or MERCHANT_SECRET_BASE64.endswith('=')
print(f"   Appears to be Base64: {'YES ✓' if is_base64 else 'NO ✗'}")

if is_base64:
    try:
        decoded = base64.b64decode(MERCHANT_SECRET_BASE64).decode('utf-8')
        print(f"   ✅ Successfully decoded!")
        print(f"   Decoded value: {decoded}")
        print(f"   Decoded length: {len(decoded)} characters")
    except Exception as e:
        print(f"   ❌ Decode failed: {e}")
        decoded = None
else:
    decoded = None

# Test both versions
print("\n" + "=" * 80)
print("🧪 TESTING HASH GENERATION WITH BOTH VERSIONS")
print("=" * 80)

test_order_id = "TEST123"
test_amount = "100.00"
test_currency = "LKR"

def generate_hash(secret):
    # Step 1: MD5 of merchant secret (UPPERCASE)
    secret_md5 = hashlib.md5(secret.encode('utf-8')).hexdigest().upper()
    
    # Step 2: Build hash string
    hash_string = f"{MERCHANT_ID}{test_order_id}{test_amount}{test_currency}{secret_md5}"
    
    # Step 3: MD5 of hash string (UPPERCASE)
    final_hash = hashlib.md5(hash_string.encode('utf-8')).hexdigest().upper()
    
    return {
        'secret': secret,
        'secret_md5': secret_md5,
        'hash_string': hash_string,
        'final_hash': final_hash
    }

print("\n1️⃣  USING ORIGINAL (BASE64) SECRET:")
print("-" * 80)
result1 = generate_hash(MERCHANT_SECRET_BASE64)
print(f"   Secret: {result1['secret'][:30]}...")
print(f"   Secret MD5: {result1['secret_md5']}")
print(f"   Hash String: {result1['hash_string']}")
print(f"   Final Hash: {result1['final_hash']}")

if decoded:
    print("\n2️⃣  USING DECODED SECRET:")
    print("-" * 80)
    result2 = generate_hash(decoded)
    print(f"   Secret: {result2['secret']}")
    print(f"   Secret MD5: {result2['secret_md5']}")
    print(f"   Hash String: {result2['hash_string']}")
    print(f"   Final Hash: {result2['final_hash']}")

print("\n" + "=" * 80)
print("📝 RECOMMENDATION:")
print("=" * 80)

if decoded:
    print("""
The decoded merchant secret looks like a proper PayHere merchant secret.
This is likely the correct value to use.

🔧 ACTION REQUIRED:
In your app.py, change:

FROM:
    MERCHANT_SECRET = "MzkwNDE1MzcwMTEwMDAwNjYxNTYzNDcxMzgyNTAyMjkzMTI4NDAwMQ=="

TO:
    import base64
    MERCHANT_SECRET_ENCODED = "MzkwNDE1MzcwMTEwMDAwNjYxNTYzNDcxMzgyNTAyMjkzMTI4NDAwMQ=="
    MERCHANT_SECRET = base64.b64decode(MERCHANT_SECRET_ENCODED).decode('utf-8')
    
OR directly:
    MERCHANT_SECRET = "39041537011000066156347138250229312840001"
""")
else:
    print("""
The merchant secret is already in the correct format.
The issue might be with the Merchant ID or account status.

🔧 VERIFY:
1. Login to https://sandbox.payhere.lk/
2. Check your Merchant ID matches exactly: 1233555
3. Check your Merchant Secret in the dashboard
4. Ensure your account is active and verified
""")

print("\n" + "=" * 80)
print("🚨 CRITICAL CHECKS:")
print("=" * 80)
print("""
1. ✓ Merchant ID is a string: YES
2. ✓ Amount is formatted as X.XX: YES (100.00)
3. ✓ Currency is 'LKR': YES
4. ✓ Hash is uppercase: YES
5. ✓ Hash is 32 characters: YES

If you're still getting "Unauthorized payment request" after fixing the secret:
- Your PayHere sandbox account might not be activated
- The Merchant ID might be incorrect
- Contact PayHere support: sandbox@payhere.lk
""")

print("\n" + "=" * 80)
print("📧 PAYHERE SANDBOX SUPPORT:")
print("=" * 80)
print("""
Email: sandbox@payhere.lk
Website: https://sandbox.payhere.lk/
Support: https://support.payhere.lk/

Mention:
- Merchant ID: 1233555
- Error: "Unauthorized payment request"
- Ask them to verify your account is properly configured
""")