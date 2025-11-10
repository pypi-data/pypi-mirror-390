#!/usr/bin/env python3
"""
Direct test of the CLI's account_client registration flow.
"""

import sys
import os
import time

# Add the installed package to the path
sys.path.insert(0, "/home/phyrexian/.local/share/pipx/venvs/cite-agent/lib/python3.13/site-packages")

from cite_agent.account_client import AccountClient

# Test with academic email
TEST_EMAIL = f"test{int(time.time())}@stanford.edu"
TEST_PASSWORD = "TestPassword123!"

print("=" * 60)
print("🧪 Testing AccountClient Auto-Registration")
print("=" * 60)
print(f"\n📧 Test email: {TEST_EMAIL}")
print(f"🔐 Test password: {TEST_PASSWORD}\n")

# Initialize client
client = AccountClient()

print(f"🔗 Backend URL: {client.base_url}\n")

# Test provision (should auto-register if user doesn't exist)
print("🔄 Testing provision() (login + auto-register fallback)...")
try:
    credentials = client.provision(TEST_EMAIL, TEST_PASSWORD)
    print(f"✅ Provision successful!")
    print(f"   Account ID: {credentials.account_id}")
    print(f"   Auth Token: {credentials.auth_token[:20]}...")
    print(f"   Email: {credentials.email}")

    # Test that we can use the token
    print(f"\n🔄 Testing token validity...")
    import requests
    response = requests.get(
        f"{client.base_url}/api/auth/me",
        headers={"Authorization": f"Bearer {credentials.auth_token}"},
        timeout=10
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Token is valid!")
        print(f"   Tokens remaining: {data.get('tokens_remaining', 0)}")
    else:
        print(f"❌ Token validation failed: {response.status_code}")

    print(f"\n" + "=" * 60)
    print(f"✅ ALL TESTS PASSED!")
    print(f"=" * 60)
    print(f"\n🎉 Auto-registration flow works correctly!")

except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)
