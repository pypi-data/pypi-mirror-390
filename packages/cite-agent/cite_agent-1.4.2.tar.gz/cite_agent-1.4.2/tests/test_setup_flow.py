#!/usr/bin/env python3
"""
Test the cleaned up setup flow (backend-only, no API keys)
"""
import os
import sys

# Remove any existing control plane URL to test offline mode
os.environ.pop("NOCTURNAL_CONTROL_PLANE_URL", None)

from cite_agent.account_client import AccountClient, AccountCredentials

def test_offline_credentials():
    """Test that offline credentials don't include api_key"""
    print("🧪 Testing offline credential generation...")

    # Force offline mode by passing base_url=None
    client = AccountClient(base_url=None)
    email = "test@university.edu"
    password = "testpassword123"

    # Generate offline credentials
    creds = client.provision(email, password)

    # Verify structure
    assert isinstance(creds, AccountCredentials), "Should return AccountCredentials"
    assert creds.email == email, "Email should match"
    assert creds.account_id, "Account ID should exist"
    assert creds.auth_token, "Auth token should exist"
    assert creds.refresh_token, "Refresh token should exist"
    assert creds.telemetry_token, "Telemetry token should exist"

    # Verify NO api_key attribute
    if hasattr(creds, 'api_key'):
        print("❌ FAIL: AccountCredentials still has api_key attribute!")
        print(f"   Found: {creds.api_key}")
        return False

    print("✅ PASS: Offline credentials generated correctly")
    print(f"   Account ID: {creds.account_id}")
    print(f"   Email: {creds.email}")
    print(f"   Auth Token: {creds.auth_token[:8]}...")
    print(f"   Refresh Token: {creds.refresh_token[:8]}...")
    print(f"   Telemetry Token: {creds.telemetry_token[:8]}...")
    print(f"   ✓ No api_key attribute (correct for backend-only mode)")
    return True

def test_managed_secrets():
    """Test that GROQ_API_KEY is not in MANAGED_SECRETS"""
    print("\n🧪 Testing MANAGED_SECRETS configuration...")

    from cite_agent.setup_config import MANAGED_SECRETS

    if "GROQ_API_KEY" in MANAGED_SECRETS:
        print("❌ FAIL: GROQ_API_KEY still in MANAGED_SECRETS!")
        return False

    print("✅ PASS: GROQ_API_KEY removed from MANAGED_SECRETS")
    print(f"   Optional secrets: {list(MANAGED_SECRETS.keys())}")
    return True

def test_check_setup():
    """Test that check_setup doesn't require Groq API key"""
    print("\n🧪 Testing check_setup logic...")

    from cite_agent.setup_config import NocturnalConfig
    from pathlib import Path
    import tempfile
    import shutil

    # Create temporary config directory
    temp_dir = tempfile.mkdtemp()
    config = NocturnalConfig()
    config.config_dir = Path(temp_dir) / ".nocturnal_archive"
    config.config_dir.mkdir(exist_ok=True)
    config.config_file = config.config_dir / "config.env"

    # Save minimal config (no GROQ_API_KEY)
    config.save_config({
        "NOCTURNAL_ACCOUNT_EMAIL": "test@edu.edu",
        "NOCTURNAL_AUTH_TOKEN": "test_token_123",
    })

    # Check setup should pass without GROQ_API_KEY
    result = config.check_setup()

    # Cleanup
    shutil.rmtree(temp_dir)

    if not result:
        print("❌ FAIL: check_setup() returned False even with email + auth_token")
        return False

    print("✅ PASS: check_setup() works without Groq API key")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Backend-Only Setup Flow Test")
    print("=" * 60)

    all_passed = True
    all_passed &= test_offline_credentials()
    all_passed &= test_managed_secrets()
    all_passed &= test_check_setup()

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Setup flow is clean!")
        print("\nUser experience:")
        print("  1. Enter email/password")
        print("  2. Accept beta terms")
        print("  3. Ready to use (backend has API keys)")
        print("\nNo API key prompts, clean SaaS flow! 🎉")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
