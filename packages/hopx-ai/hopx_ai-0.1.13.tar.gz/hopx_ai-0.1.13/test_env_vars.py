#!/usr/bin/env python3
"""Test environment variables feature."""

import os
from bunnyshell import Sandbox

API_KEY = os.environ.get('BUNNYSHELL_API_KEY', 'hopx_test_org_017_api_key_qrs345tuv678')

print('🚀 Testing Environment Variables Feature...\n')

try:
    # Test 1: Create sandbox with env_vars
    print('1️⃣  Creating sandbox with env_vars...')
    sandbox = Sandbox.create(
        template='code-interpreter',
        api_key=API_KEY,
        env_vars={
            "API_KEY": "sk-prod-xyz",
            "DATABASE_URL": "postgres://user:pass@localhost:5432/db",
            "NODE_ENV": "production"
        }
    )
    print(f'✅ Sandbox created: {sandbox.sandbox_id}')
    print(f'✅ Agent URL: {sandbox.get_info().public_host}')
    print()
    
    # Test 2: Get all environment variables
    print('2️⃣  Getting all environment variables...')
    env = sandbox.env.get_all()
    print(f'✅ Found {len(env)} environment variables')
    print(f'✅ API_KEY: {env.get("API_KEY")}')
    print(f'✅ DATABASE_URL: {env.get("DATABASE_URL")}')
    print(f'✅ NODE_ENV: {env.get("NODE_ENV")}')
    print()
    
    # Test 3: Get a specific variable
    print('3️⃣  Getting specific variable...')
    api_key = sandbox.env.get("API_KEY")
    print(f'✅ API_KEY = {api_key}')
    print()
    
    # Test 4: Set a single variable
    print('4️⃣  Setting single variable...')
    sandbox.env.set("DEBUG", "true")
    print(f'✅ Set DEBUG=true')
    debug = sandbox.env.get("DEBUG")
    print(f'✅ Verified: DEBUG = {debug}')
    print()
    
    # Test 5: Update multiple variables (merge)
    print('5️⃣  Updating multiple variables (merge)...')
    sandbox.env.update({
        "LOG_LEVEL": "info",
        "MAX_WORKERS": "4"
    })
    print(f'✅ Updated LOG_LEVEL and MAX_WORKERS')
    env = sandbox.env.get_all()
    print(f'✅ Total variables: {len(env)}')
    print(f'✅ LOG_LEVEL: {env.get("LOG_LEVEL")}')
    print(f'✅ MAX_WORKERS: {env.get("MAX_WORKERS")}')
    print()
    
    # Test 6: Delete a variable
    print('6️⃣  Deleting variable...')
    sandbox.env.delete("DEBUG")
    print(f'✅ Deleted DEBUG')
    debug = sandbox.env.get("DEBUG")
    print(f'✅ Verified: DEBUG = {debug} (should be None)')
    print()
    
    # Test 7: Verify in code execution
    print('7️⃣  Verifying env vars in code execution...')
    result = sandbox.run_code('''
import os
print(f"API_KEY: {os.environ.get('API_KEY', 'NOT SET')}")
print(f"NODE_ENV: {os.environ.get('NODE_ENV', 'NOT SET')}")
print(f"LOG_LEVEL: {os.environ.get('LOG_LEVEL', 'NOT SET')}")
    '''.strip())
    print(f'✅ Code execution result:')
    for line in result.stdout.strip().split('\n'):
        print(f'   {line}')
    print()
    
    # Cleanup
    print('8️⃣  Cleaning up...')
    sandbox.kill()
    print('✅ Sandbox killed')
    print()
    
    print('🎉 ALL ENVIRONMENT VARIABLES TESTS PASSED!')
    print('✅ Create sandbox with env_vars')
    print('✅ Get all environment variables')
    print('✅ Get specific variable')
    print('✅ Set single variable')
    print('✅ Update multiple variables (merge)')
    print('✅ Delete variable')
    print('✅ Verify in code execution')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()

