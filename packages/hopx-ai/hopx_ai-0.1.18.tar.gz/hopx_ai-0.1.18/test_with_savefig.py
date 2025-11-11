from hopx_ai import Sandbox
import json

sandbox = Sandbox.create(template='code-interpreter')
sandbox._ensure_agent_client()

# Try with savefig like in test_agent.sh
code = '''
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 5))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('sin(X)')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()  # Display triggers Jupyter capture
print("Plot created")
'''

# Patch to see response
original_post = sandbox._agent_client.post
def debug_post(*args, **kwargs):
    response = original_post(*args, **kwargs)
    try:
        data = response.json()
        print("\nResponse keys:", list(data.keys()))
        for key in ['png', 'html', 'json', 'result']:
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    print(f"  {key}: <{len(val)} chars>")
                else:
                    print(f"  {key}: {type(val)}")
    except:
        pass
    return response

sandbox._agent_client.post = debug_post

result = sandbox.run_code(code, language='python', timeout=30)
print(f"\nrich_count: {result.rich_count}")
print(f"success: {result.success}")

sandbox.kill()
