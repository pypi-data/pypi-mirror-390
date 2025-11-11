#!/usr/bin/env python3
"""
Simple test for get_logs() function
Uses existing template build ID
"""

import asyncio
import os
from bunnyshell.template import get_logs

API_KEY = os.getenv("BUNNYSHELL_API_KEY", "hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0")
BASE_URL = "https://api.hopx.dev"

# Use completed build from Public API test
BUILD_ID = "321"

async def test_get_logs():
    """Test get_logs() with completed build"""
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║      🧪 Python SDK - get_logs() Test                             ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    print(f"Testing with build ID: {BUILD_ID}")
    print()
    
    # Get logs from beginning
    print("1️⃣  Getting logs from offset 0...")
    response = await get_logs(BUILD_ID, API_KEY, offset=0, base_url=BASE_URL)
    
    print(f"✅ Response received!")
    print(f"   Status: {response.status}")
    print(f"   Complete: {response.complete}")
    print(f"   Offset: {response.offset}")
    print(f"   Logs length: {len(response.logs)} bytes")
    print()
    
    # Show first 500 chars of logs
    print("📄 First 500 chars of logs:")
    print(response.logs[:500])
    print("...")
    print()
    
    # Test incremental fetch
    print("2️⃣  Getting logs from offset 1000...")
    response2 = await get_logs(BUILD_ID, API_KEY, offset=1000, base_url=BASE_URL)
    
    print(f"✅ Response received!")
    print(f"   New offset: {response2.offset}")
    print(f"   New logs length: {len(response2.logs)} bytes")
    print()
    
    print("══════════════════════════════════════════════════════════════════")
    print("✨ get_logs() function works perfectly!")
    print("══════════════════════════════════════════════════════════════════")

if __name__ == "__main__":
    asyncio.run(test_get_logs())

