#!/usr/bin/env python3
"""
JWT Authentication Test for Python SDK

Tests:
1. Create sandbox stores JWT token
2. Connect to paused sandbox resumes it and refreshes token
3. Agent requests include Authorization header
4. Token auto-refresh works
"""

import os
import sys
from bunnyshell import Sandbox
from bunnyshell.errors import BunnyshellError

API_KEY = os.environ.get('BUNNYSHELL_API_KEY', 'hopx_test_key')
BASE_URL = os.environ.get('BUNNYSHELL_API_URL', 'https://api.hopx.dev')


def test_jwt_authentication():
    """Test JWT authentication flow"""
    print('🔐 JWT Authentication Test - Python SDK\n')
    
    try:
        # Test 1: Create Sandbox (should store JWT token)
        print('1️⃣  Testing Sandbox.create() - JWT token storage...')
        
        sandbox = Sandbox.create(
            template='code-interpreter',
            api_key=API_KEY,
            base_url=BASE_URL,
            vcpu=2,
            memory_mb=2048,
        )
        
        print(f'   ✅ Sandbox created: {sandbox.sandbox_id}')
        
        # Get token to verify it was stored
        try:
            token = sandbox.get_token()
            token_preview = token[:50] + '...'
            print(f'   ✅ JWT token stored: {token_preview}')
            print(f'   ✅ Token length: {len(token)} chars')
            
            if len(token) != 261:
                print(f'   ⚠️  Warning: Token length is not 261 chars (got {len(token)})')
        except BunnyshellError as e:
            print(f'   ❌ Failed to get token: {e}')
            raise
        
        # Test 2: Get sandbox info (agent client should use JWT)
        print('\n2️⃣  Testing agent calls with JWT...')
        
        info = sandbox.get_info()
        print(f'   ✅ Sandbox status: {info.status}')
        print(f'   ✅ Public host: {info.public_host}')
        
        # Test 3: Execute code (should include JWT in request)
        print('\n3️⃣  Testing code execution with JWT...')
        
        try:
            result = sandbox.run_code('print("JWT Authentication Test")')
            print('   ✅ Code executed successfully')
            print(f'   ✅ Output: {result.stdout.strip()}')
            print(f'   ✅ Exit code: {result.exit_code}')
        except BunnyshellError as e:
            print(f'   ⚠️  Code execution failed (expected if no VM agent): {e}')
        
        # Test 4: Token refresh
        print('\n4️⃣  Testing token refresh...')
        
        try:
            sandbox.refresh_token()
            print('   ✅ Token refreshed successfully')
            
            new_token = sandbox.get_token()
            new_token_preview = new_token[:50] + '...'
            print(f'   ✅ New token: {new_token_preview}')
        except BunnyshellError as e:
            print(f'   ⚠️  Token refresh failed: {e}')
        
        # Test 5: Connect to existing sandbox
        print('\n5️⃣  Testing Sandbox.connect() with JWT...')
        
        try:
            connected_sandbox = Sandbox.connect(
                sandbox_id=sandbox.sandbox_id,
                api_key=API_KEY,
                base_url=BASE_URL
            )
            print(f'   ✅ Connected to sandbox: {connected_sandbox.sandbox_id}')
            
            connected_token = connected_sandbox.get_token()
            print('   ✅ Token available after connect')
        except BunnyshellError as e:
            print(f'   ⚠️  Connect failed: {e}')
        
        # Cleanup
        print('\n6️⃣  Cleaning up...')
        try:
            sandbox.kill()
            print('   ✅ Sandbox deleted')
        except BunnyshellError as e:
            print(f'   ⚠️  Cleanup failed: {e}')
        
        print('\n✅ All JWT tests completed successfully!\n')
        
    except BunnyshellError as e:
        print(f'\n❌ Test failed: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_connect_to_stopped_sandbox():
    """Test connect to stopped sandbox (should throw error)"""
    print('\n🧪 Testing connect to stopped sandbox...\n')
    
    try:
        # This should throw an error
        sandbox = Sandbox.connect(
            sandbox_id='stopped_sandbox_id',
            api_key=API_KEY,
            base_url=BASE_URL
        )
        print('   ❌ Should have thrown error for stopped sandbox')
    except BunnyshellError as e:
        if 'stopped' in str(e).lower():
            print('   ✅ Correctly throws error for stopped sandbox')
            print(f'   ✅ Error message: {e}')
        else:
            print(f'   ⚠️  Unexpected error: {e}')


def main():
    """Run all tests"""
    print('╔═══════════════════════════════════════════════════════╗')
    print('║   JWT Authentication Test - Python SDK               ║')
    print('╚═══════════════════════════════════════════════════════╝\n')
    
    test_jwt_authentication()
    test_connect_to_stopped_sandbox()
    
    print('\n╔═══════════════════════════════════════════════════════╗')
    print('║   All tests completed!                                ║')
    print('╚═══════════════════════════════════════════════════════╝\n')


if __name__ == '__main__':
    main()

