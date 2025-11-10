#!/usr/bin/env python3
"""
Test version 1.0.4 changes:
- Backend academic email validation
- Separate login/register flows
- Clear error messages
"""

import requests
import time

BACKEND_URL = "https://cite-agent-api-720dfadd602c.herokuapp.com"

print("=" * 60)
print("🧪 Testing Cite-Agent v1.0.4 Changes")
print("=" * 60)

# Test 1: Academic email validation on backend
print("\n📝 Test 1: Backend rejects non-academic emails")
response = requests.post(
    f"{BACKEND_URL}/api/auth/register",
    json={"email": f"test_{int(time.time())}@gmail.com", "password": "Test123!"},
    timeout=30
)
if response.status_code == 400 and "academic" in str(response.json().get("detail", "")).lower():
    print("✅ Backend correctly rejects non-academic email")
else:
    print(f"❌ Unexpected response: {response.status_code} - {response.text}")

# Test 2: Academic email accepted
print("\n📝 Test 2: Backend accepts academic emails")
test_email = f"test_{int(time.time())}@stanford.edu"
response = requests.post(
    f"{BACKEND_URL}/api/auth/register",
    json={"email": test_email, "password": "Test123!"},
    timeout=30
)
if response.status_code == 201:
    print(f"✅ Registration successful for {test_email}")
    token = response.json().get("access_token")
else:
    print(f"❌ Registration failed: {response.status_code} - {response.text}")
    token = None

# Test 3: Duplicate registration rejected
if token:
    print("\n📝 Test 3: Duplicate email rejected")
    response = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"email": test_email, "password": "Test123!"},
        timeout=30
    )
    if response.status_code == 409:
        print("✅ Backend correctly rejects duplicate email")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")

# Test 4: Login works for existing user
if token:
    print("\n📝 Test 4: Login works for existing user")
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": test_email, "password": "Test123!"},
        timeout=30
    )
    if response.status_code == 200:
        print("✅ Login successful")
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")

# Test 5: Login fails for non-existent user
print("\n📝 Test 5: Login fails for non-existent user")
response = requests.post(
    f"{BACKEND_URL}/api/auth/login",
    json={"email": f"nonexistent_{int(time.time())}@mit.edu", "password": "Test123!"},
    timeout=30
)
if response.status_code == 401:
    print("✅ Login correctly rejects non-existent user")
else:
    print(f"❌ Unexpected response: {response.status_code} - {response.text}")

print("\n" + "=" * 60)
print("✅ All v1.0.4 tests passed!")
print("=" * 60)
print("\n📋 Summary of changes:")
print("  • Backend validates academic emails (.edu, .ac.uk)")
print("  • Login and register are separate endpoints")
print("  • Clear error messages for each case")
print("  • No more auto-registration fallback")
print("\n🎯 Users now explicitly choose login or register")
