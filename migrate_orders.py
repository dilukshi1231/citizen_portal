"""
Migrate existing orders to pending status for admin approval
Run: python migrate_orders.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
orders_col = db["orders"]

print("=" * 60)
print("📦 ORDER STATUS MIGRATION")
print("=" * 60)

# Update all "paid" orders to "pending" for admin review
result = orders_col.update_many(
    {"status": "paid"},
    {
        "$set": {
            "status": "pending",
            "payment_status": "completed"
        }
    }
)

print(f"✅ Migrated {result.modified_count} paid orders to pending status")
print("=" * 60)
print("\n🔄 Now refresh the admin dashboard to see approve/cancel buttons")