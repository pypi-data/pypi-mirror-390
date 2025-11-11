#!/usr/bin/env python3
"""
END-TO-END Test - Template Building via SDK
Tests the complete flow as a real user would use it:
SDK -> API Public -> NodeMgr
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path

# Import SDK
sys.path.insert(0, str(Path(__file__).parent))
from bunnyshell.template import Template, BuildOptions
from bunnyshell.template.ready_checks import wait_for_port

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'
BASE_URL = 'https://api.hopx.dev'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

async def test_simple_python_app():
    """Test 1: Simple Python HTTP server"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"🧪 TEST 1: Simple Python HTTP Server")
    print(f"{'='*70}{Colors.END}\n")
    
    # Create a temporary app directory
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = Path(tmpdir) / "app"
        app_dir.mkdir()
        
        # Create a simple Python app
        (app_dir / "server.py").write_text("""
import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever()
""")
        
        (app_dir / "index.html").write_text("<h1>Hello from SDK!</h1>")
        
        print("📝 Building template using SDK...")
        
        # Build template using SDK (as a user would)
        template = (
            Template()
            .from_python_image("3.11")
            .copy(str(app_dir), "/app/")
            .set_start_cmd("python /app/server.py", wait_for_port(8000))
        )
        
        print(f"   Template has {len(template.get_steps())} steps")
        
        try:
            result = await Template.build(template, BuildOptions(
                alias=f"sdk-test-python-{int(asyncio.get_event_loop().time())}",
                api_key=API_KEY,
                base_url=BASE_URL,
                cpu=2,
                memory=2048,
                disk_gb=10,
                context_path=tmpdir,
                on_log=lambda log: print(f"   [LOG] {log.get('message', '')}"),
                on_progress=lambda p: print(f"   [PROGRESS] {p}%"),
            ))
            
            print(f"\n{Colors.GREEN}✅ SUCCESS!{Colors.END}")
            print(f"   Build ID: {result.build_id}")
            print(f"   Template ID: {result.template_id}")
            print(f"   Duration: {result.duration}ms")
            return True
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ FAILED: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            return False


async def test_nodejs_app_with_deps():
    """Test 2: Node.js app with dependencies"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"🧪 TEST 2: Node.js App with Dependencies")
    print(f"{'='*70}{Colors.END}\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = Path(tmpdir) / "app"
        app_dir.mkdir()
        
        # Create Node.js app
        (app_dir / "package.json").write_text("""
{
  "name": "sdk-test-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  }
}
""")
        
        (app_dir / "server.js").write_text("""
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
    res.send('Hello from SDK Node.js app!');
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
""")
        
        print("📝 Building template using SDK...")
        
        # Build with SDK
        template = (
            Template()
            .from_node_image("20")
            .copy(str(app_dir), "/app/")
            .set_workdir("/app")
            .run_cmd("npm install")
            .set_start_cmd("node server.js", wait_for_port(3000))
        )
        
        print(f"   Template has {len(template.get_steps())} steps")
        
        try:
            result = await Template.build(template, BuildOptions(
                alias=f"sdk-test-nodejs-{int(asyncio.get_event_loop().time())}",
                api_key=API_KEY,
                base_url=BASE_URL,
                cpu=2,
                memory=2048,
                disk_gb=10,
                context_path=tmpdir,
                on_log=lambda log: print(f"   [LOG] {log.get('message', '')}"),
            ))
            
            print(f"\n{Colors.GREEN}✅ SUCCESS!{Colors.END}")
            print(f"   Build ID: {result.build_id}")
            print(f"   Template ID: {result.template_id}")
            return True
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ FAILED: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            return False


async def test_ubuntu_with_packages():
    """Test 3: Ubuntu with apt packages"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"🧪 TEST 3: Ubuntu with apt packages")
    print(f"{'='*70}{Colors.END}\n")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = Path(tmpdir) / "app"
        app_dir.mkdir()
        
        # Create a simple script
        (app_dir / "run.sh").write_text("""#!/bin/bash
redis-server --daemonize yes
python3 -m http.server 8000
""")
        
        print("📝 Building template using SDK...")
        
        # Build with SDK - similar to user's example
        template = (
            Template()
            .from_ubuntu_image("22.04")
            .apt_install(["python3", "redis-server"])
            .copy(str(app_dir), "/app/")
            .run_cmd("chmod +x /app/run.sh")
            .set_env("APP_ENV", "production")
            .set_workdir("/app")
            .set_start_cmd("bash /app/run.sh", wait_for_port(8000))
        )
        
        print(f"   Template has {len(template.get_steps())} steps")
        
        try:
            result = await Template.build(template, BuildOptions(
                alias=f"sdk-test-ubuntu-{int(asyncio.get_event_loop().time())}",
                api_key=API_KEY,
                base_url=BASE_URL,
                cpu=2,
                memory=2048,
                disk_gb=15,
                context_path=tmpdir,
                on_log=lambda log: print(f"   [LOG] {log.get('message', '')}"),
            ))
            
            print(f"\n{Colors.GREEN}✅ SUCCESS!{Colors.END}")
            print(f"   Build ID: {result.build_id}")
            print(f"   Template ID: {result.template_id}")
            return True
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ FAILED: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run all E2E tests"""
    print(f"{Colors.BLUE}{'='*70}")
    print(f"🚀 SDK END-TO-END TESTS")
    print(f"{'='*70}{Colors.END}")
    print(f"API: {BASE_URL}")
    print(f"Testing as real user with SDK...")
    
    tests = [
        ("Simple Python App", test_simple_python_app),
        ("Node.js with Dependencies", test_nodejs_app_with_deps),
        ("Ubuntu with apt packages", test_ubuntu_with_packages),
    ]
    
    results = []
    for name, test_func in tests:
        result = await test_func()
        results.append((name, result))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}{Colors.END}")
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = f"{Colors.GREEN}✅ PASS{Colors.END}" if result else f"{Colors.RED}❌ FAIL{Colors.END}"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {len(results)}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    
    success_rate = (passed / len(results) * 100) if results else 0
    print(f"\nSuccess Rate: {success_rate:.0f}%")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())

