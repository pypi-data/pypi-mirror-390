import requests
import os

AGENT_URL = "https://7777-1762806326yw9qagff.eu2.vms.hopx.dev"
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2bV9pZCI6IjE3NjI4MDYzMjZ5dzlxYWdmZiIsIm9yZ19pZCI6MzAsImlzcyI6Im5vZGVtZ3IiLCJzdWIiOiIxNzYyODA2MzI2eXc5cWFnZmYiLCJleHAiOjE3NjI4OTM3MjMsIm5iZiI6MTc2MjgwNzMyMywiaWF0IjoxNzYyODA3MzIzfQ.HUc5go-GFRyiC3MeT6qvGTFQMKyciL1geXWmRI-raLA"

code = '''
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [1, 4, 9])
plt.title("Test")
plt.show()
'''

response = requests.post(
    f"{AGENT_URL}/execute",
    headers={"Authorization": f"Bearer {JWT_TOKEN}"},
    json={"language": "python", "code": code, "timeout": 30}
)

print("Status:", response.status_code)
print("Response keys:", list(response.json().keys()))
print("Full response:")
import json
print(json.dumps(response.json(), indent=2, default=str)[:2000])
