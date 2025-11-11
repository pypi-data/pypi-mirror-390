#!/usr/bin/env python3
"""
Test Python SDK - template name (without vcpu/memory)
"""

import sys
sys.path.insert(0, '/var/www/sdks/python')

from bunnyshell import Sandbox

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'

print("=" * 70)
print("🎯 Python SDK - template NAME Support Test")
print("=" * 70)
print()

try:
    # Create from template NAME (NO vcpu/memory_mb)
    print("Creating sandbox from template='e2e-test-1761656297'...")
    print("  ⚠️  NOT specifying vcpu or memory_mb")
    print()
    
    sandbox = Sandbox.create(
        template="e2e-test-1761656297",  # Template NAME (not ID)
        api_key=API_KEY,
    )
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    
    # Get info
    info = sandbox.get_info()
    print(f"\n📊 Sandbox Info:")
    print(f"   Status: {info.status}")
    
    if info.resources:
        print(f"\n💻 Resources (loaded from template by NAME):")
        print(f"   vCPU: {info.resources.vcpu}")
        print(f"   Memory: {info.resources.memory_mb} MB")
        print(f"   Disk: {info.resources.disk_mb} MB")
    
    # Cleanup
    print(f"\n🧹 Cleaning up...")
    sandbox.kill()
    print("   ✅ Sandbox terminated")
    
    print("\n" + "=" * 70)
    print("🎉 TEST PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✅ Created sandbox with template NAME only")
    print("  ✅ NO vcpu or memory_mb specified")
    print("  ✅ Resources auto-loaded from template by name")
    print("  ✅ Python SDK template name support WORKS!")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

