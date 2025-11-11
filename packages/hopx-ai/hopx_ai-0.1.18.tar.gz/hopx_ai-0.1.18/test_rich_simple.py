from hopx_ai import Sandbox
import os

API_KEY = os.environ['HOPX_API_KEY']

sandbox = Sandbox.create(template='code-interpreter', api_key=API_KEY)

# Test 1: Simple Matplotlib
code1 = '''
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Test Plot")
plt.show()
'''

print("Test 1: Matplotlib with plt.show()")
result = sandbox.run_code(code1, language='python', timeout=30)
print(f"  success: {result.success}")
print(f"  stdout: '{result.stdout.strip()}'")
print(f"  stderr: '{result.stderr.strip()}'")
print(f"  rich_count: {result.rich_count}")
if result.rich_outputs:
    for i, ro in enumerate(result.rich_outputs):
        print(f"  rich_output[{i}]: type={ro.type}, data_keys={list(ro.data.keys())}")
print()

# Test 2: Simple print (no rich)
code2 = 'print("Hello, world!")'
print("Test 2: Simple print (no rich)")
result2 = sandbox.run_code(code2, language='python', timeout=10)
print(f"  success: {result2.success}")
print(f"  stdout: '{result2.stdout.strip()}'")
print(f"  rich_count: {result2.rich_count}")
print()

sandbox.kill()
