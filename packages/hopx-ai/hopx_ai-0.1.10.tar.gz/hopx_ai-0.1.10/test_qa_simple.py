#!/usr/bin/env python3
"""
Senior QA - Comprehensive Template Building Tests
"""
import requests
import time
import hashlib

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'
BASE_URL = 'https://api.hopx.dev'

def h():
    return {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

passed = 0
failed = 0
total = 0

def test(name, expected, fn):
    global passed, failed, total
    total += 1
    print(f"\n{'='*60}")
    print(f"Test #{total}: {name}")
    try:
        status, note = fn()
        print(f"Expected: {expected}, Got: {status}")
        if note:
            print(f"Note: {note}")
        if status == expected:
            passed += 1
            print("✅ PASS")
        else:
            failed += 1
            print("❌ FAIL")
    except Exception as e:
        failed += 1
        print(f"❌ EXCEPTION: {e}")

print("🔍 SENIOR QA - COMPREHENSIVE TESTS")
print(f"API: {BASE_URL}")
print("="*60)

# HAPPY PATH
print("\n🟢 HAPPY PATH TESTS")

test("Simple RUN step", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa1-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo hello'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build: {r.json().get('build_id', 'N/A')}"
))

test("Multiple RUN steps", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa2-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y curl'},
            {'type': 'run', 'command': 'curl --version'}
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    None
))

test("ENV variables", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa3-{int(time.time())}',
        'steps': [
            {'type': 'env', 'key': 'MY_VAR', 'value': 'test'},
            {'type': 'run', 'command': 'echo $MY_VAR'}
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    None
))

test("WORKDIR step", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa4-{int(time.time())}',
        'steps': [
            {'type': 'workdir', 'path': '/tmp'},
            {'type': 'run', 'command': 'pwd'}
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    None
))

test("Port ready check", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa5-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'apt-get update'}],
        'start_cmd': 'python3 -m http.server 8000',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    None
))

# ERROR HANDLING
print("\n🔴 ERROR HANDLING TESTS")

test("Invalid API key", 401, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': 'Bearer invalid_key',
        'Content-Type': 'application/json'
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject invalid key"
))

test("Missing alias", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should require alias"
))

test("Empty steps", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-empty-{int(time.time())}',
        'steps': [],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject empty steps"
))

test("Invalid step type", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-invalid-{int(time.time())}',
        'steps': [{'type': 'INVALID', 'command': 'test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject invalid step type"
))

test("Negative CPU", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-neg-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': -1, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject negative CPU"
))

# COMPLEX SCENARIOS
print("\n🚀 REALISTIC TEMPLATES")

test("Python Flask App", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'flask-app-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y python3-pip'},
            {'type': 'run', 'command': 'pip3 install flask gunicorn'},
            {'type': 'env', 'key': 'FLASK_APP', 'value': 'app.py'},
            {'type': 'workdir', 'path': '/app'}
        ],
        'start_cmd': 'gunicorn app:app',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Flask template - Build: {r.json().get('build_id')}"
))

test("Node.js Express App", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'express-app-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -'},
            {'type': 'run', 'command': 'apt-get install -y nodejs'},
            {'type': 'env', 'key': 'NODE_ENV', 'value': 'production'},
            {'type': 'workdir', 'path': '/app'}
        ],
        'start_cmd': 'node server.js',
        'ready_cmd': {'type': 'port', 'port': 3000},
        'cpu': 4, 'memory_mb': 4096, 'disk_gb': 20
    })).status_code,
    f"Express template - Build: {r.json().get('build_id')}"
))

test("Redis Server", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'redis-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y redis-server'},
            {'type': 'env', 'key': 'REDIS_PORT', 'value': '6379'}
        ],
        'start_cmd': 'redis-server --port 6379',
        'ready_cmd': {'type': 'port', 'port': 6379},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    None
))

# CACHE TESTS
print("\n�� CACHE & FILE TESTS")

test("Upload link request", 200, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=h(), json={
        'files_hash': hashlib.sha256(f'test-{time.time()}'.encode()).hexdigest(),
        'content_length': 1024
    })).status_code,
    f"Present: {r.json().get('present')}"
))

test("Invalid hash length", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=h(), json={
        'files_hash': 'short',
        'content_length': 1024
    })).status_code,
    "Should reject short hash"
))

# BUILD STATUS
print("\n📊 BUILD STATUS & LOGS")

def test_status():
    b = requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-status-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    }).json()
    time.sleep(1)
    r = requests.get(f'{BASE_URL}/v1/templates/build/{b["build_id"]}/status', headers=h())
    return r.status_code, f"Status: {r.json().get('status')}"

test("Build status check", 200, test_status)

def test_logs():
    b = requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-logs-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    }).json()
    r = requests.get(f'{BASE_URL}/v1/templates/build/{b["build_id"]}/logs', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'text/event-stream'
    }, stream=True)
    return r.status_code, f"Content-Type: {r.headers.get('content-type')}"

test("SSE log streaming", 200, test_logs)

test("List templates", 200, lambda: (
    (r := requests.get(f'{BASE_URL}/v1/templates?limit=5', headers=h())).status_code,
    f"Found {len(r.json().get('data', []))} templates"
))

test("Non-existent build_id", 404, lambda: (
    (r := requests.get(f'{BASE_URL}/v1/templates/build/bld_nonexistent/status', headers=h())).status_code,
    "Should return 404"
))

# SUMMARY
print(f"\n{'='*60}")
print(f"📊 QA SUMMARY")
print(f"{'='*60}")
print(f"Total: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {100*passed//total if total > 0 else 0}%")

if passed / total >= 0.9:
    print(f"\n✅ EXCELLENT - API is production ready!")
elif passed / total >= 0.75:
    print(f"\n⚠️  GOOD - Minor issues to address")
else:
    print(f"\n❌ NEEDS WORK - Significant issues")
