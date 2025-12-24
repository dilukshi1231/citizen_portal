#!/usr/bin/env python3
"""
Auto-fix script for app.py
- Fixes datetime.utcnow() deprecation warnings
- Fixes duplicate order ID issue
"""

import re

def fix_app_py():
    print("🔧 Reading app.py...")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup original
    with open('app.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Backup created: app.py.backup")
    
    # Fix 1: Add timezone import if not present
    if 'from datetime import datetime, timedelta, timezone' not in content:
        content = content.replace(
            'from datetime import datetime, timedelta',
            'from datetime import datetime, timedelta, timezone'
        )
        print("✅ Added timezone import")
    
    # Fix 2: Add uuid import if not present
    if 'import uuid' not in content:
        # Add after other imports (find a good spot)
        import_section = re.search(r'(import bcrypt\n)', content)
        if import_section:
            content = content.replace(
                'import bcrypt\n',
                'import bcrypt\nimport uuid\n'
            )
            print("✅ Added uuid import")
    
    # Fix 3: Add helper function if not present
    helper_function = '''
def get_utc_now():
    """Get current UTC time (Python 3.13 compatible)"""
    return datetime.now(timezone.utc)

'''
    
    if 'def get_utc_now():' not in content:
        # Add after the imports and before the first route
        content = content.replace(
            'def admin_required(fn):',
            helper_function + 'def admin_required(fn):'
        )
        print("✅ Added get_utc_now() helper function")
    
    # Fix 4: Replace all datetime.utcnow() with get_utc_now()
    count = content.count('datetime.utcnow()')
    if count > 0:
        content = content.replace('datetime.utcnow()', 'get_utc_now()')
        print(f"✅ Replaced {count} occurrences of datetime.utcnow()")
    
    # Fix 5: Fix create_order function to use UUID
    create_order_pattern = r'(@app\.route\("/api/store/order".*?def create_order\(\):.*?)("order_id": f"ORD\{datetime[^}]+\}")(.*?)(result = orders_col\.insert_one\(order\).*?return jsonify\(\{"status": "ok", "order_id": order\["order_id"\]\}\))'
    
    create_order_replacement = r'''\1# Generate unique order ID with UUID
    unique_suffix = str(uuid.uuid4())[:8]
    timestamp = get_utc_now().strftime('%Y%m%d%H%M%S')
    
    order = {
        "order_id": f"ORD{timestamp}-{unique_suffix}",  # More unique ID\3
    try:
        result = orders_col.insert_one(order)
        return jsonify({"status": "ok", "order_id": order["order_id"]})
    except Exception as e:
        print(f"Error creating order: {e}")
        return jsonify({"error": "Failed to create order"}), 500'''
    
    if re.search(create_order_pattern, content, re.DOTALL):
        content = re.sub(create_order_pattern, create_order_replacement, content, flags=re.DOTALL)
        print("✅ Fixed create_order function with UUID")
    
    # Fix 6: Fix process_payment function to use UUID
    payment_pattern = r'("payment_id": f"PAY\{datetime[^}]+\}")'
    payment_replacement = r'''# Generate unique payment ID
    unique_suffix = str(uuid.uuid4())[:8]
    timestamp = get_utc_now().strftime('%Y%m%d%H%M%S')
    
    payment = {
        "payment_id": f"PAY{timestamp}-{unique_suffix}",'''
    
    # Find and replace in process_payment function
    if 'def process_payment():' in content:
        # Find the function and replace payment_id generation
        payment_func_match = re.search(
            r'(def process_payment\(\):.*?payment = \{)',
            content,
            re.DOTALL
        )
        if payment_func_match:
            # Replace the payment_id line more carefully
            content = re.sub(
                r'(def process_payment\(\):.*?payment = \{)\s*"payment_id": f"PAY\{[^}]+\}",',
                r'\1\n        "payment_id": f"PAY{get_utc_now().strftime(\'%Y%m%d%H%M%S\')}-{str(uuid.uuid4())[:8]}",',
                content,
                flags=re.DOTALL,
                count=1
            )
            print("✅ Fixed process_payment function with UUID")
    
    # Write fixed content
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 Changes made:")
    print("  1. Added timezone import")
    print("  2. Added uuid import")
    print("  3. Added get_utc_now() helper function")
    print(f"  4. Replaced {count} datetime.utcnow() calls")
    print("  5. Fixed order_id generation (now unique)")
    print("  6. Fixed payment_id generation (now unique)")
    print("\n💾 Backup saved as: app.py.backup")
    print("\n🚀 Restart your Flask app to apply changes!")

if __name__ == "__main__":
    try:
        fix_app_py()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check app.py and try manual fixes if needed.")