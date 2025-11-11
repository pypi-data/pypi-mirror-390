from hopx_ai import Sandbox
import os
import json

API_KEY = os.environ['HOPX_API_KEY']

sandbox = Sandbox.create(template='code-interpreter', api_key=API_KEY)

code = '''
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.savefig('/workspace/test.png')
plt.show()
print("Done")
'''

print("Sending code...")
result = sandbox.run_code(code, language='python', timeout=30)

print(f"\nResult:")
print(f"  success: {result.success}")
print(f"  stdout: {result.stdout}")
print(f"  stderr: {result.stderr}")
print(f"  exit_code: {result.exit_code}")
print(f"  rich_count: {result.rich_count}")
print(f"  rich_outputs: {result.rich_outputs}")

sandbox.kill()
