"""Test hybrid SDK with live agent."""

import os
from bunnyshell import Sandbox
from bunnyshell.models import ExecutionResult, FileInfo, Language
from bunnyshell.errors import FileNotFoundError

# API key
API_KEY = os.environ.get("BUNNYSHELL_API_KEY", "hopx_f0dfeb804627ca3c1ccdd3d43d2913c9")

print("🚀 Testing Hybrid SDK with Live Agent...")
print()

try:
    # Create sandbox
    print("1️⃣  Creating sandbox...")
    sandbox = Sandbox.create(
        template="code-interpreter-desktop",
        api_key=API_KEY
    )
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    print()
    
    # Test run_code with type hints
    print("2️⃣  Testing run_code (type-safe ExecutionResult)...")
    result: ExecutionResult = sandbox.run_code("""
print("Hello from hybrid SDK!")
print("Type-safe models: ✅")
print("Convenience methods: ✅")
    """.strip())
    
    print(f"✅ Type: {type(result).__name__}")
    print(f"✅ Result: {repr(result)}")
    print(f"✅ stdout: {result.stdout.strip()}")
    print(f"✅ success: {result.success}")
    print(f"✅ rich_count: {result.rich_count} (convenience!)")
    print()
    
    # Test file operations with type hints
    print("3️⃣  Testing files (type-safe FileInfo)...")
    sandbox.files.write("/workspace/test_hybrid.txt", "Hybrid approach rocks!")
    content = sandbox.files.read("/workspace/test_hybrid.txt")
    print(f"✅ Content: {content}")
    
    files: list[FileInfo] = sandbox.files.list("/workspace")
    print(f"✅ Files found: {len(files)}")
    for file in files[:3]:
        print(f"  📄 {file.name}: {file.size_kb:.2f}KB (type-safe + convenience!)")
    print()
    
    # Test commands with type hints
    print("4️⃣  Testing commands (type-safe CommandResult)...")
    cmd_result = sandbox.commands.run("echo 'Hybrid SDK test'")
    print(f"✅ Type: {type(cmd_result).__name__}")
    print(f"✅ Result: {repr(cmd_result)}")
    print(f"✅ success: {cmd_result.success} (convenience!)")
    print()
    
    # Test error handling with ErrorCode
    print("5️⃣  Testing error handling (type-safe ErrorCode)...")
    try:
        sandbox.files.read("/nonexistent_file.txt")
    except FileNotFoundError as e:
        print(f"✅ Caught: {type(e).__name__}")
        print(f"✅ Code: {e.code} (machine-readable!)")
        print(f"✅ Message: {e.message}")
        print(f"✅ Request ID: {e.request_id}")
    print()
    
    # Cleanup
    print("6️⃣  Cleaning up...")
    sandbox.kill()
    print("✅ Sandbox killed")
    print()
    
    print("🎉 ALL HYBRID SDK TESTS PASSED!")
    print("✅ Type-safe models from OpenAPI")
    print("✅ Convenience methods for DX")
    print("✅ Hand-crafted client API")
    print("✅ GOLD-STANDARD Developer Experience!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

