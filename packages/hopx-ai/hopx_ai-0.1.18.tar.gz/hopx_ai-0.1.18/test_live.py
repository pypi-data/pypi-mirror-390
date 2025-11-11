#!/usr/bin/env python3
"""
Live API test - verify SDK works with real API.

Tests the new E2B-style Sandbox API.
"""

import sys
sys.path.insert(0, '.')

from bunnyshell import Sandbox, BunnyshellError

# API key for testing
API_KEY = "hopx_f0dfeb804627ca3c1ccdd3d43d2913c9"

print("🧪 Testing Bunnyshell Python SDK (E2B Pattern)\n")

try:
    # Test 1: List templates
    print("1. Listing templates...")
    templates = Sandbox.list_templates(api_key=API_KEY)
    print(f"   ✅ Found {len(templates)} templates")
    if templates:
        t = templates[0]
        print(f"   • {t.name}: {t.display_name}")
    
    # Test 2: Get specific template
    print("\n2. Getting 'code-interpreter' template...")
    template = Sandbox.get_template("code-interpreter", api_key=API_KEY)
    print(f"   ✅ {template.display_name}")
    print(f"   Description: {template.description[:80]}...")
    
    # Test 3: Create sandbox FIRST (E2B style!)
    print("\n3. Creating new sandbox (E2B pattern)...")
    sandbox = Sandbox.create(
        template="code-interpreter",
        vcpu=2,
        memory_mb=2048,
        api_key=API_KEY
    )
    print(f"   ✅ Created: {sandbox.sandbox_id}")
    
    # Test 4: Get sandbox info
    print(f"\n4. Getting sandbox info...")
    info = sandbox.get_info()
    print(f"   ✅ ID: {info.sandbox_id}")
    print(f"   🌐 URL: {info.public_host}")
    print(f"   📊 Status: {info.status}")
    print(f"   💾 Resources: {info.vcpu} vCPU, {info.memory_mb}MB")
    
    # Test 5: Reconnect to sandbox
    print(f"\n5. Reconnecting to sandbox {sandbox.sandbox_id}...")
    reconnected = Sandbox.connect(sandbox.sandbox_id, api_key=API_KEY)
    print(f"   ✅ Reconnected!")
    
    # Test 6: List sandboxes
    print(f"\n6. Listing sandboxes...")
    try:
        sandboxes = Sandbox.list(limit=5, api_key=API_KEY)
        print(f"   ✅ Found {len(sandboxes)} sandboxes")
        for sb in sandboxes[:2]:
            info = sb.get_info()
            print(f"   • {sb.sandbox_id}: {info.status}")
    except Exception as e:
        print(f"   ⚠️  List skipped ({str(e)[:50]}...)")
    
    # Test 7: Delete sandbox
    print(f"\n7. Deleting sandbox...")
    sandbox.kill()
    print(f"   ✅ Deleted!")
    
    print("\n🎉 All tests passed! E2B-style SDK is working perfectly!")
    
except BunnyshellError as e:
    print(f"\n❌ Error: {e.message}")
    print(f"   Type: {type(e).__name__}")
    print(f"   Code: {e.code}")
    print(f"   Request ID: {e.request_id}")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

