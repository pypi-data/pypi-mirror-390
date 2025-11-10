#!/usr/bin/env python3
"""
End-to-end test of cite-agent registration and query flow.
Tests the complete user journey from registration to making queries.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path
import pytest

# Test configuration
BACKEND_URL = "https://cite-agent-api-720dfadd602c.herokuapp.com"
TEST_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture
def email():
    """Provide test email"""
    return TEST_EMAIL


@pytest.fixture
def password():
    """Provide test password"""
    return TEST_PASSWORD


@pytest.fixture
def token(email, password):
    """Provide authentication token by registering/logging in"""
    # Try registration first
    response = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"email": email, "password": password},
        timeout=30
    )

    if response.status_code == 201:
        return response.json().get('access_token')

    # If already registered, try login
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=30
    )

    if response.status_code == 200:
        return response.json().get('access_token')

    pytest.skip(f"Could not authenticate: {response.status_code}")


def test_registration():
    """Test user registration"""
    print(f"🔄 Testing registration with: {TEST_EMAIL}")

    response = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=30
    )

    if response.status_code == 201:
        data = response.json()
        print(f"✅ Registration successful")
        print(f"   User ID: {data.get('user_id')}")
        print(f"   Token expires: {data.get('expires_at')}")
        return data.get('access_token')
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_login(email, password):
    """Test user login"""
    print(f"\n🔄 Testing login with: {email}")

    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": email, "password": password},
        timeout=30
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful")
        return data.get('access_token')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_health():
    """Test backend health check"""
    print(f"\n🔄 Testing backend health")

    response = requests.get(f"{BACKEND_URL}/api/health/", timeout=10)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend healthy")
        print(f"   Status: {data.get('status')}")
        print(f"   Version: {data.get('version')}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_query(token):
    """Test making a query to the backend"""
    print(f"\n🔄 Testing query with authentication")

    response = requests.post(
        f"{BACKEND_URL}/api/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": "What is 2+2?",
            "context": {},
            "user_id": "test_user",
            "conversation_id": "test_conv"
        },
        timeout=60
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Query successful")
        print(f"   Response: {data.get('response', data.get('answer', ''))[:100]}")
        return True
    else:
        print(f"❌ Query failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_quota_check(token):
    """Test checking remaining quota"""
    print(f"\n🔄 Testing quota check")

    response = requests.get(
        f"{BACKEND_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Quota check successful")
        print(f"   Tokens used today: {data.get('tokens_used_today', 0)}")
        print(f"   Tokens remaining: {data.get('tokens_remaining', 0)}")
        return True
    else:
        print(f"❌ Quota check failed: {response.status_code}")
        return False

def main():
    print("=" * 60)
    print("🧪 Cite-Agent End-to-End Test Suite")
    print("=" * 60)

    # Test 1: Health check
    if not test_health():
        print("\n❌ Backend is not healthy, aborting tests")
        sys.exit(1)

    # Test 2: Registration
    token = test_registration()
    if not token:
        print("\n❌ Registration failed, aborting tests")
        sys.exit(1)

    # Test 3: Login (should work with same credentials)
    login_token = test_login(TEST_EMAIL, TEST_PASSWORD)
    if not login_token:
        print("\n❌ Login failed, aborting tests")
        sys.exit(1)

    # Test 4: Query with token
    if not test_query(token):
        print("\n❌ Query failed, aborting tests")
        sys.exit(1)

    # Test 5: Quota check
    if not test_quota_check(token):
        print("\n❌ Quota check failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\n📝 Test Summary:")
    print(f"   • Backend health: ✅")
    print(f"   • User registration: ✅")
    print(f"   • User login: ✅")
    print(f"   • Query execution: ✅")
    print(f"   • Quota checking: ✅")
    print(f"\n🎉 The cite-agent backend is fully operational!")

if __name__ == "__main__":
    main()
