#!/usr/bin/env python3
"""
Simple JWT Test - Tests only JWT functionality without template dependencies
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import only what we need (avoid template imports)
from bunnyshell._client import HTTPClient
from bunnyshell.sandbox import Sandbox, _token_cache
from bunnyshell.errors import BunnyshellError

API_KEY = os.environ.get('BUNNYSHELL_API_KEY', 'hopx_test_org_011_api_key_cde567fgh890')
BASE_URL = os.environ.get('BUNNYSHELL_API_URL', 'https://api.hopx.dev')

print('🔐 JWT Authentication Test - Python SDK (Simple)\n')

try:
    # Test 1: Create Sandbox
    print('1️⃣  Testing Sandbox.create() - JWT token storage...')
    
    sandbox = Sandbox.create(
        template='code-interpreter',
        api_key=API_KEY,
        base_url=BASE_URL,
        vcpu=2,
        memory_mb=2048,
    )
    
    print(f'   ✅ Sandbox created: {sandbox.sandbox_id}')
    
    # Test 2: Verify token is stored
    print('\n2️⃣  Verifying JWT token storage...')
    
    if sandbox.sandbox_id in _token_cache:
        token_data = _token_cache[sandbox.sandbox_id]
        print(f'   ✅ Token stored in cache')
        print(f'   ✅ Token length: {len(token_data.token)} chars')
        print(f'   ✅ Token expires at: {token_data.expires_at}')
    else:
        print('   ❌ Token NOT found in cache!')
    
    # Test 3: Get token via method
    print('\n3️⃣  Testing get_token() method...')
    
    try:
        token = sandbox.get_token()
        print(f'   ✅ Token retrieved: {token[:50]}...')
    except Exception as e:
        print(f'   ⚠️  get_token() failed: {e}')
    
    # Test 4: Get sandbox info
    print('\n4️⃣  Testing sandbox.get_info()...')
    
    try:
        info = sandbox.get_info()
        print(f'   ✅ Sandbox status: {info.status}')
        print(f'   ✅ Public host: {info.public_host}')
    except Exception as e:
        print(f'   ⚠️  get_info() failed: {e}')
    
    # Test 5: Token refresh
    print('\n5️⃣  Testing token refresh...')
    
    try:
        sandbox.refresh_token()
        print('   ✅ Token refresh successful')
        
        new_token = sandbox.get_token()
        print(f'   ✅ New token: {new_token[:50]}...')
    except Exception as e:
        print(f'   ⚠️  Token refresh failed: {e}')
    
    # Test 6: Connect to sandbox
    print('\n6️⃣  Testing Sandbox.connect()...')
    
    try:
        connected = Sandbox.connect(
            sandbox_id=sandbox.sandbox_id,
            api_key=API_KEY,
            base_url=BASE_URL
        )
        print(f'   ✅ Connected to sandbox: {connected.sandbox_id}')
    except Exception as e:
        print(f'   ⚠️  Connect failed: {e}')
    
    # Cleanup
    print('\n7️⃣  Cleaning up...')
    try:
        sandbox.kill()
        print('   ✅ Sandbox deleted')
    except Exception as e:
        print(f'   ⚠️  Cleanup failed: {e}')
    
    print('\n✅ Python SDK JWT test completed!\n')
    
except BunnyshellError as e:
    print(f'\n❌ Test failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'\n❌ Unexpected error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

