"""
Officer Filtering Diagnostic Tool
Run: python diagnose_officers.py
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["citizen_portal"]
services_col = db["services"]
officers_col = db["officers"]

print("=" * 70)
print("👥 OFFICER FILTERING DIAGNOSTIC")
print("=" * 70)

# Check all officers
print("\n📋 ALL OFFICERS IN DATABASE:")
all_officers = list(officers_col.find({}, {"_id": 0}))
print(f"Total officers: {len(all_officers)}")

for officer in all_officers:
    print(f"\n  Officer: {officer.get('name')}")
    print(f"  Ministry ID: {officer.get('ministry_id')}")
    print(f"  Role: {officer.get('role')}")

# Check all services (ministries)
print("\n\n📋 ALL MINISTRIES IN DATABASE:")
all_services = list(services_col.find({}, {"_id": 0, "id": 1, "name": 1}))
print(f"Total ministries: {len(all_services)}")

for service in all_services[:10]:  # Show first 10
    print(f"\n  Ministry ID: {service.get('id')}")
    print(f"  Name: {service.get('name', {}).get('en', 'N/A')}")

# Test filtering
print("\n\n🔍 TESTING OFFICER FILTERING:")
test_ministry_ids = ["ministry_it", "ministry_education", "ministry_health"]

for ministry_id in test_ministry_ids:
    officers = list(officers_col.find({"ministry_id": ministry_id}, {"_id": 0}))
    print(f"\n  Ministry: {ministry_id}")
    print(f"  Officers found: {len(officers)}")
    
    if officers:
        for officer in officers:
            print(f"    - {officer.get('name')} ({officer.get('role')})")
    else:
        print(f"    ⚠️ No officers found for this ministry!")

# Check for mismatches
print("\n\n🔎 CHECKING FOR ID MISMATCHES:")
service_ids = set(s['id'] for s in all_services)
officer_ministry_ids = set(o['ministry_id'] for o in all_officers)

print(f"\nService IDs in DB: {sorted(service_ids)[:5]}...")
print(f"Officer ministry_ids in DB: {sorted(officer_ministry_ids)}")

orphaned = officer_ministry_ids - service_ids
if orphaned:
    print(f"\n⚠️ WARNING: Officers with invalid ministry_ids:")
    for ministry_id in orphaned:
        print(f"  - {ministry_id} (no matching service)")

# Recommendations
print("\n" + "=" * 70)
print("📊 DIAGNOSTIC SUMMARY")
print("=" * 70)

if len(all_officers) == 0:
    print("\n❌ ISSUE: No officers in database")
    print("   FIX: Run 'python migrate_db.py' to create sample officers")
elif orphaned:
    print(f"\n⚠️ ISSUE: {len(orphaned)} officers have invalid ministry_ids")
    print("   FIX: Update officer ministry_ids to match service IDs")
else:
    print("\n✅ Officer data looks correct!")
    print("   Check the frontend JavaScript to ensure:")
    print("   1. Officers are loaded on page load")
    print("   2. Ministry ID is passed correctly to showOfficersForMinistry()")
    print("   3. Filter logic matches database IDs")

print("=" * 70)