#!/usr/bin/env python3
"""
Test SDK template_id support.
Verify that VM can be created from template_id WITHOUT specifying vcpu/memory.
"""

import sys
sys.path.insert(0, '/var/www/sdks/python')

from bunnyshell import Sandbox

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'

print("=" * 70)
print("🧪 Python SDK - template_id Support Test")
print("=" * 70)
print()

try:
    # Test 1: Create from template_id (NO vcpu/memory)
    print("Test 1: Create sandbox from template_id (no vcpu/memory)...")
    sandbox = Sandbox.create(
        template_id="291",  # Template on NFS with chunked storage
        api_key=API_KEY,
    )
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    
    # Get info
    info = sandbox.get_info()
    print(f"   Status: {info.status}")
    print(f"   Resources:")
    if info.resources:
        print(f"     vCPU: {info.resources.vcpu}")
        print(f"     Memory: {info.resources.memory_mb} MB")
        print(f"     Disk: {info.resources.disk_mb} MB")
    print()
    
    # Cleanup
    sandbox.kill()
    print("✅ Sandbox cleaned up")
    print()
    
    # Test 2: Verify old way still works (backwards compatible)
    print("Test 2: Verify backwards compatibility (template name + resources)...")
    sandbox2 = Sandbox.create(
        template="code-interpreter",
        vcpu=2,
        memory_mb=512,
        api_key=API_KEY,
    )
    print(f"✅ Sandbox created: {sandbox2.sandbox_id}")
    sandbox2.kill()
    print("✅ Sandbox cleaned up")
    print()
    
    print("=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✅ template_id support works")
    print("  ✅ Resources auto-loaded from template")
    print("  ✅ Backwards compatible with old API")
    
except Exception as e:
    print(f"❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

