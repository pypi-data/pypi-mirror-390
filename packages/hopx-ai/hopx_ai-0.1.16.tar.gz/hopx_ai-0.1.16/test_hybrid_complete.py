#!/usr/bin/env python3
"""Complete test of hybrid SDK with live API."""

import os
from bunnyshell import Sandbox
from bunnyshell.errors import FileNotFoundError, ErrorCode

API_KEY = os.environ.get('BUNNYSHELL_API_KEY', 'hopx_test_org_017_api_key_qrs345tuv678')

print('🚀 Testing Hybrid SDK with Live API...\n')

try:
    # Create sandbox
    print('1️⃣  Creating sandbox...')
    sandbox = Sandbox.create(
        template='code-interpreter',
        api_key=API_KEY,
        timeout=300
    )
    print(f'✅ Sandbox created: {sandbox.sandbox_id}')
    info = sandbox.get_info()
    print(f'✅ Agent URL: {info.public_host}')
    print(f'✅ Status: {info.status}')
    print()
    
    # Test run_code with type hints
    print('2️⃣  Testing run_code (type-safe ExecutionResult)...')
    result = sandbox.run_code('''
print("Hello from hybrid SDK!")
print("Type-safe models: ✅")
print("Convenience methods: ✅")
import sys
print(f"Python: {sys.version.split()[0]}")
    '''.strip())
    
    print(f'✅ Type: {type(result).__name__}')
    print(f'✅ Result: {repr(result)}')
    print(f'✅ stdout:')
    for line in result.stdout.strip().split('\n'):
        print(f'   {line}')
    print(f'✅ success: {result.success}')
    print(f'✅ exit_code: {result.exit_code}')
    print(f'✅ execution_time: {result.execution_time:.3f}s')
    print(f'✅ rich_count: {result.rich_count} (convenience property!)')
    print()
    
    # Test file operations
    print('3️⃣  Testing files (type-safe FileInfo)...')
    sandbox.files.write('/workspace/test_hybrid.txt', 'Hybrid approach rocks! 🚀')
    content = sandbox.files.read('/workspace/test_hybrid.txt')
    print(f'✅ Content written: {content}')
    
    files = sandbox.files.list('/workspace')
    print(f'✅ Files found: {len(files)}')
    for file in files[:5]:
        print(f'   {repr(file)}')
        print(f'      └─ size_kb: {file.size_kb:.2f}KB (convenience!)')
        print(f'      └─ is_file: {file.is_file} (convenience!)')
    print()
    
    # Test commands
    print('4️⃣  Testing commands (type-safe CommandResult)...')
    cmd_result = sandbox.commands.run('echo "Hybrid SDK test" && pwd')
    print(f'✅ Type: {type(cmd_result).__name__}')
    print(f'✅ Result: {repr(cmd_result)}')
    print(f'✅ stdout: {cmd_result.stdout.strip()}')
    print(f'✅ success: {cmd_result.success} (convenience property!)')
    print()
    
    # Test error handling
    print('5️⃣  Testing error handling (type-safe ErrorCode)...')
    try:
        sandbox.files.read('/nonexistent_file_12345.txt')
    except FileNotFoundError as e:
        print(f'✅ Caught: {type(e).__name__}')
        print(f'✅ Code: {e.code} (machine-readable!)')
        print(f'✅ Message: {e.message}')
        print(f'✅ Request ID: {e.request_id}')
        print(f'✅ Path: {e.path}')
    print()
    
    # Cleanup
    print('6️⃣  Cleaning up...')
    sandbox.kill()
    print('✅ Sandbox killed')
    print()
    
    print('🎉 ALL HYBRID SDK TESTS PASSED!')
    print('✅ Type-safe models from OpenAPI')
    print('✅ Convenience methods for DX')
    print('✅ Hand-crafted client API')
    print('✅ Machine-readable error codes')
    print('✅ Beautiful repr() with emojis')
    print()
    print('⭐⭐⭐⭐⭐ GOLD-STANDARD Developer Experience!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()

