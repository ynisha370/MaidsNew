"""
Direct test of service edit functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

print("="*60)
print("TESTING SERVICE EDIT FUNCTIONALITY")
print("="*60)

# Test 1: Login as admin
print("\n1. Admin Login...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@maids.com", "password": "admin123"},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        admin_token = data.get("access_token") or data.get("token")
        print(f"✓ Login successful")
        print(f"  Token: {admin_token[:30]}...")
    else:
        print(f"✗ Login failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 2: Get services list
print("\n2. Get Services...")
try:
    response = requests.get(
        f"{BASE_URL}/admin/services",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10
    )
    if response.status_code == 200:
        services = response.json()
        print(f"✓ Found {len(services)} services")
        if len(services) > 0:
            test_service = services[0]
            service_id = test_service['id']
            print(f"  Test service: {test_service['name']}")
            print(f"  ID: {service_id}")
            print(f"  Current description: {test_service.get('description', 'N/A')}")
    else:
        print(f"✗ Failed: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)

# Test 3: Update service description
print("\n3. Update Service Description...")
try:
    new_description = "✅ UPDATED VIA API: Professional feather dusting of all window blinds"
    response = requests.patch(
        f"{BASE_URL}/admin/services/{service_id}",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        json={"description": new_description},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Service updated successfully!")
        if data.get('service'):
            print(f"  New description: {data['service'].get('description')}")
    else:
        print(f"✗ Update failed: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Update service price
print("\n4. Update Service Price...")
try:
    response = requests.patch(
        f"{BASE_URL}/admin/services/{service_id}",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        json={"a_la_carte_price": 15.99},
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Price updated successfully!")
        if data.get('service'):
            print(f"  New price: ${data['service'].get('a_la_carte_price')}")
    else:
        print(f"✗ Update failed: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Full update (PUT)
print("\n5. Full Update (PUT)...")
try:
    response = requests.put(
        f"{BASE_URL}/admin/services/{service_id}",
        headers={
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        },
        json={
            "name": "Blinds Dusting Service",
            "description": "✅ FULLY UPDATED: Professional feather dusting",
            "a_la_carte_price": 12.50
        },
        timeout=10
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Service fully updated!")
        if data.get('service'):
            print(f"  Name: {data['service'].get('name')}")
            print(f"  Description: {data['service'].get('description')}")
            print(f"  Price: ${data['service'].get('a_la_carte_price')}")
    else:
        print(f"✗ Update failed: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 6: Verify update persisted
print("\n6. Verify Updates Persisted...")
try:
    response = requests.get(
        f"{BASE_URL}/admin/services",
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=10
    )
    if response.status_code == 200:
        services = response.json()
        updated_service = next((s for s in services if s['id'] == service_id), None)
        if updated_service:
            print(f"✓ Service found after updates")
            print(f"  Name: {updated_service['name']}")
            print(f"  Description: {updated_service.get('description', 'N/A')}")
            print(f"  Price: ${updated_service.get('a_la_carte_price', 0)}")
        else:
            print(f"✗ Service not found in list")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "="*60)
print("✅ SERVICE EDIT TESTING COMPLETE")
print("="*60)

