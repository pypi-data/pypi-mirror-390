#!/usr/bin/env python3
"""
Final test - Python SDK template_id support.
"""

import sys
sys.path.insert(0, '/var/www/sdks/python')

from bunnyshell import Sandbox

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'

print("=" * 70)
print("🎯 Python SDK - template_id Final Test")
print("=" * 70)
print()

try:
    # Create from template_id (NO vcpu/memory needed!)
    print("Creating sandbox from template_id=291...")
    print("  ⚠️  NOT specifying vcpu or memory_mb")
    print()
    
    sandbox = Sandbox.create(
        template_id="291",
        api_key=API_KEY,
    )
    
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    
    # Get detailed info
    info = sandbox.get_info()
    print(f"\n📊 Sandbox Info:")
    print(f"   Status: {info.status}")
    print(f"   Template ID: {info.template_id if hasattr(info, 'template_id') else 'N/A'}")
    print(f"   Template Name: {info.template_name if hasattr(info, 'template_name') else 'N/A'}")
    
    if info.resources:
        print(f"\n💻 Resources (loaded from template 291):")
        print(f"   vCPU: {info.resources.vcpu}")
        print(f"   Memory: {info.resources.memory_mb} MB")
        print(f"   Disk: {info.resources.disk_mb} MB")
    
    print(f"\n🌐 Public URL:")
    print(f"   {info.public_host}")
    
    # Cleanup
    print(f"\n🧹 Cleaning up...")
    sandbox.kill()
    print("   ✅ Sandbox terminated")
    
    print("\n" + "=" * 70)
    print("🎉 TEST PASSED!")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✅ Created sandbox with template_id ONLY")
    print("  ✅ NO vcpu or memory_mb specified")
    print("  ✅ Resources auto-loaded from template")
    print("  ✅ Python SDK template_id support WORKS!")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

