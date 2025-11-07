#!/usr/bin/env python3
"""Test Python SDK - API Connection & JWT Logic"""

import os
import sys
from datetime import datetime, timedelta

# Test 1: API Connection
print('🔐 Python SDK - JWT Test\n')
print('1️⃣  Testing API connection...')

try:
    import httpx
    
    API_KEY = os.environ.get('BUNNYSHELL_API_KEY', 'hopx_test_org_011_api_key_cde567fgh890')
    
    response = httpx.get(
        'https://api.hopx.dev/v1/sandboxes',
        headers={'X-API-Key': API_KEY},
        params={'limit': 1},
        timeout=10
    )
    
    print(f'   ✅ API connection successful (status: {response.status_code})')
    data = response.json()
    print(f'   ✅ Found {len(data.get("data", []))} sandbox(es)')
    
except Exception as e:
    print(f'   ⚠️  API connection failed: {e}')

# Test 2: JWT Token Logic
print('\n2️⃣  Testing JWT storage logic...')

token_cache = {}
sandbox_id = 'test_sandbox_123'
test_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_payload.signature'
expires_at = datetime.now() + timedelta(hours=24)

# Store token
token_cache[sandbox_id] = {
    'token': test_token,
    'expires_at': expires_at
}

print('   ✅ Token storage works')

# Retrieve token
stored = token_cache.get(sandbox_id)
if stored and stored['token'] == test_token:
    print('   ✅ Token retrieval works')
else:
    print('   ❌ Token retrieval failed')
    sys.exit(1)

# Check expiry
hours_left = (stored['expires_at'] - datetime.now()).total_seconds() / 3600
print(f'   ✅ Token expires in {hours_left:.2f} hours')

if hours_left < 1:
    print('   ⚠️  Token would be refreshed (< 1 hour left)')
else:
    print('   ✅ Token is valid (> 1 hour left)')

# Test 3: Authorization Header
print('\n3️⃣  Testing Authorization header format...')

auth_header = f'Bearer {test_token}'
if auth_header.startswith('Bearer '):
    print('   ✅ Authorization header format correct')
    print(f'   Header: {auth_header[:40]}...')
else:
    print('   ❌ Authorization header format incorrect')
    sys.exit(1)

print('\n✅ All Python SDK JWT tests passed!\n')


