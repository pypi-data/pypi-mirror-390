# Quick test pentru env vars fix
import sys
sys.path.insert(0, "/var/www/sdks/python")

from hopx_ai import Sandbox

sandbox = Sandbox.create(
    template="code-interpreter",
    api_key="hopx_live_Lap0VJrWLii8.KSN6iLWELs13jHt960gSK9Eq63trgPApqMf7yLGVTNo"
)

print("1️⃣  Set env var...")
sandbox.env.update({"TEST_VAR": "hello_world"})
all_vars = sandbox.env.get_all()
print(f"✅ TEST_VAR = {all_vars.get('TEST_VAR')}")

print("\n2️⃣  Update env var...")
sandbox.env.update({"TEST_VAR": "updated_value", "ANOTHER_VAR": "test123"})
all_vars = sandbox.env.get_all()
print(f"✅ TEST_VAR = {all_vars.get('TEST_VAR')}")
print(f"✅ ANOTHER_VAR = {all_vars.get('ANOTHER_VAR')}")

print("\n3️⃣  Delete env var...")
sandbox.env.delete("TEST_VAR")
all_vars = sandbox.env.get_all()
print(f"✅ TEST_VAR after delete = {all_vars.get('TEST_VAR')}")
print(f"✅ ANOTHER_VAR still = {all_vars.get('ANOTHER_VAR')}")

sandbox.kill()
print("\n✅ Test PASSED!")
