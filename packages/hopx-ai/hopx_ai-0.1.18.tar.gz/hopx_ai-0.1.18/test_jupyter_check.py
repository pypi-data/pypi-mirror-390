from hopx_ai import Sandbox

sandbox = Sandbox.create(template='code-interpreter')
sandbox._ensure_agent_client()

# Check if Jupyter is available
code = 'import sys; print("Python:", sys.version); import IPython; print("IPython:", IPython.__version__)'

result = sandbox.run_code(code, language='python', timeout=10)
print("Output:")
print(result.stdout)
print("\nErrors:")
print(result.stderr)

# Check agent health
info = sandbox.get_info()
print(f"\nAgent: {info.public_host}")

sandbox.kill()
