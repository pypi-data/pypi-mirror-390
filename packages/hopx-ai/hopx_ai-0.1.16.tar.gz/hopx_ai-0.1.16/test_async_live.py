#!/usr/bin/env python3
"""
Live async API test.

Tests AsyncSandbox with real API.
"""

import sys
import asyncio
sys.path.insert(0, '.')

from bunnyshell import AsyncSandbox, BunnyshellError

# API key for testing
API_KEY = "hopx_f0dfeb804627ca3c1ccdd3d43d2913c9"


async def main():
    print("🧪 Testing Bunnyshell Async SDK\n")
    
    try:
        # Test 1: List templates (async)
        print("1. Listing templates (async)...")
        templates = await AsyncSandbox.list_templates(api_key=API_KEY)
        print(f"   ✅ Found {len(templates)} templates")
        if templates:
            t = templates[0]
            print(f"   • {t.name}: {t.display_name}")
        
        # Test 2: Get specific template (async)
        print("\n2. Getting 'code-interpreter' template (async)...")
        template = await AsyncSandbox.get_template("code-interpreter", api_key=API_KEY)
        print(f"   ✅ {template.display_name}")
        print(f"   Description: {template.description[:80]}...")
        
        # Test 3: Create sandbox (async)
        print("\n3. Creating sandbox (async)...")
        sandbox = await AsyncSandbox.create(
            template="code-interpreter",
            vcpu=2,
            memory_mb=2048,
            api_key=API_KEY
        )
        
        try:
            print(f"   ✅ Created: {sandbox.sandbox_id}")
            
            # Test 4: Get info (async)
            print(f"\n4. Getting sandbox info (async)...")
            info = await sandbox.get_info()
            print(f"   ✅ ID: {info.sandbox_id}")
            print(f"   🌐 URL: {info.public_host}")
            print(f"   📊 Status: {info.status}")
            print(f"   💾 Resources: {info.vcpu} vCPU, {info.memory_mb}MB")
            
            # Test 5: Reconnect (async)
            print(f"\n5. Reconnecting to sandbox (async)...")
            reconnected = await AsyncSandbox.connect(sandbox.sandbox_id, api_key=API_KEY)
            print(f"   ✅ Reconnected!")
            
        finally:
            # Clean up
            print(f"\n6. Deleting sandbox...")
            await sandbox.kill()
            print(f"   ✅ Deleted!")
        
        # Test 7: Async iterator
        print(f"\n7. Testing async iterator...")
        count = 0
        async for sb in AsyncSandbox.iter(api_key=API_KEY):
            print(f"   • {sb.sandbox_id}")
            count += 1
            if count >= 2:
                print("   (stopping early)")
                break
        
        print("\n🎉 All async tests passed!")
        
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


if __name__ == "__main__":
    asyncio.run(main())

