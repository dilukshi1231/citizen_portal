"""
Cleanup script to remove N/A engagements from database
Run: python cleanup_engagements.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
eng_col = db["engagements"]

print("🧹 Cleaning up N/A engagements...")

# Find and delete engagements where all key fields are None/empty
result = eng_col.delete_many({
    "$or": [
        {
            "user_id": None,
            "age": None,
            "job": {"$in": [None, "", "Unknown"]},
            "question_clicked": {"$in": [None, "", "Unknown"]},
            "service": {"$in": [None, "", "Unknown"]}
        },
        {
            "user_id": {"$exists": False},
            "age": {"$exists": False},
            "job": {"$exists": False},
            "question_clicked": {"$exists": False},
            "service": {"$exists": False}
        }
    ]
})

print(f"✅ Deleted {result.deleted_count} empty engagements")

# Show remaining count
remaining = eng_col.count_documents({})
print(f"📊 Remaining engagements: {remaining}")