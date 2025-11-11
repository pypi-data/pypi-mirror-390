import httpx
from hopx_ai import Sandbox

sandbox = Sandbox.create(template='code-interpreter')
info = sandbox.get_info()

# Get agent health with features
response = httpx.get(f"{info.public_host}/health")
health = response.json()

print("Agent Features:")
print(f"  Version: {health.get('version')}")
print(f"  Features: {health.get('features', [])}")
print(f"  Jupyter: {'jupyter' in health.get('features', [])}")

sandbox.kill()
