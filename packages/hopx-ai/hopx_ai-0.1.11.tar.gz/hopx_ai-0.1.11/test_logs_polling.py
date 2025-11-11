#!/usr/bin/env python3
"""
Test Python SDK - Build Logs Polling

Demonstrates offset-based log polling for template builds.
"""

import asyncio
import os
import sys
from bunnyshell.template import (
    Template,
    create_template,
    get_logs,
    BuildOptions,
)

API_KEY = os.getenv("BUNNYSHELL_API_KEY", "hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0")
BASE_URL = "https://api.hopx.dev"


async def test_logs_polling():
    """Test build logs with offset-based polling"""
    
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║      🧪 Python SDK - Build Logs Polling Test                     ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    
    # Create template
    template = (
        create_template()
        .from_image("ubuntu:22.04")
        .run_cmd("apt-get update")
        .run_cmd("apt-get install -y curl")
        .run_cmd("curl --version")
    )
    
    # Build options
    options = BuildOptions(
        alias=f"test-logs-{int(asyncio.get_event_loop().time())}",
        api_key=API_KEY,
        base_url=BASE_URL,
        cpu=2,
        memory=2048,
        disk_gb=10,
    )
    
    print("1️⃣  Triggering build...")
    result = await Template.build(template, options)
    build_id = result.build_id
    print(f"✅ Build started: {build_id}")
    print()
    
    print("2️⃣  Polling logs with offset...")
    print("══════════════════════════════════════════════════════════════════")
    print()
    
    offset = 0
    iteration = 0
    
    while True:
        iteration += 1
        
        # Get logs from current offset
        response = await get_logs(build_id, API_KEY, offset=offset, base_url=BASE_URL)
        
        # Print new logs if any
        if response.logs:
            print(response.logs, end='')
            sys.stdout.flush()
        
        # Update offset for next poll
        offset = response.offset
        
        # Show status every 10 iterations if no new logs
        if not response.logs and iteration % 10 == 0:
            print(f"\r⏳ [{iteration * 2}s] Status: {response.status}, Offset: {offset}     ", end='')
            sys.stdout.flush()
        
        # Check if build is complete
        if response.complete:
            print()
            print()
            print(f"✅ Build complete! Status: {response.status}")
            print(f"   Final offset: {offset}")
            break
        
        # Wait before next poll
        await asyncio.sleep(2)
    
    print()
    print("══════════════════════════════════════════════════════════════════")
    print("✨ Test completed successfully!")
    print()


if __name__ == "__main__":
    asyncio.run(test_logs_polling())

