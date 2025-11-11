#!/usr/bin/env python3
"""
Comprehensive QA Tests with REAL API Key
"""
import requests
import time
import hashlib
import os
import tempfile

# REAL API KEY
API_KEY = 'hopx_f0dfeb804627ca3c1ccdd3d43d2913c9'
BASE_URL = 'https://api.hopx.dev'

def h():
    return {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

print("🔍 COMPREHENSIVE QA TESTS - REAL API")
print(f"API: {BASE_URL}")
print(f"Key: {API_KEY[:20]}...")
print("="*70)

passed = 0
failed = 0
total = 0

def test(name, expected, fn):
    global passed, failed, total
    total += 1
    print(f"\n{'='*70}")
    print(f"Test #{total}: {name}")
    print(f"Expected: HTTP {expected}")
    try:
        status, note = fn()
        print(f"Got: HTTP {status}")
        if note:
            print(f"📝 {note}")
        if status == expected:
            passed += 1
            print("✅ PASS")
            return True
        else:
            failed += 1
            print(f"❌ FAIL (expected {expected}, got {status})")
            return False
    except Exception as e:
        failed += 1
        print(f"❌ EXCEPTION: {e}")
        return False

# =============================================================================
# CATEGORY 1: HAPPY PATH TESTS
# =============================================================================

print("\n" + "="*70)
print("🟢 CATEGORY 1: HAPPY PATH TESTS")
print("="*70)

test("Simple RUN step", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-simple-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo "hello world"'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build ID: {r.json().get('build_id')}"
))

test("Multiple RUN steps (5 commands)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-multi-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y curl git'},
            {'type': 'run', 'command': 'curl --version'},
            {'type': 'run', 'command': 'git --version'},
            {'type': 'run', 'command': 'echo "all installed"'}
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build ID: {r.json().get('build_id')}"
))

test("ENV variables", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-env-{int(time.time())}',
        'steps': [
            {'type': 'env', 'key': 'MY_VAR', 'value': 'test123'},
            {'type': 'env', 'key': 'APP_ENV', 'value': 'production'},
            {'type': 'run', 'command': 'env | grep MY_VAR'}
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build ID: {r.json().get('build_id')}"
))

test("WORKDIR step", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-workdir-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'mkdir -p /myapp'},
            {'type': 'workdir', 'path': '/myapp'},
            {'type': 'run', 'command': 'pwd'},
            {'type': 'run', 'command': 'echo "test" > file.txt'}
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build ID: {r.json().get('build_id')}"
))

test("Ready check - PORT", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-ready-port-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'apt-get update'}],
        'start_cmd': 'python3 -m http.server 8000',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build ID: {r.json().get('build_id')}"
))

test("Ready check - HTTP", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-ready-http-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'apt-get update'}],
        'start_cmd': 'python3 -m http.server 8080',
        'ready_cmd': {'type': 'http', 'url': 'http://localhost:8080'},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Build ID: {r.json().get('build_id')}"
))

# =============================================================================
# CATEGORY 2: EDGE CASES
# =============================================================================

print("\n" + "="*70)
print("🟡 CATEGORY 2: EDGE CASES")
print("="*70)

test("Long alias (100 chars)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': 'test-long-' + 'x' * 90,
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Testing long alias acceptance"
))

test("Special characters in alias", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': 'test-with_special.chars-123',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Dashes, underscores, dots, numbers"
))

test("Minimum resources (1 CPU, 128MB, 1GB)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-min-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 1, 'memory_mb': 128, 'disk_gb': 1
    })).status_code,
    "Testing minimum resource limits"
))

test("High resources (8 CPU, 8GB, 50GB)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-high-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 8, 'memory_mb': 8192, 'disk_gb': 50
    })).status_code,
    "Testing high resource allocation"
))

test("Many steps (20 commands)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-many-steps-{int(time.time())}',
        'steps': [{'type': 'run', 'command': f'echo "step {i}"'} for i in range(20)],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "20 sequential RUN steps"
))

# =============================================================================
# CATEGORY 3: ERROR HANDLING
# =============================================================================

print("\n" + "="*70)
print("🔴 CATEGORY 3: ERROR HANDLING")
print("="*70)

test("Invalid API key", 401, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': 'Bearer invalid_key_xxx',
        'Content-Type': 'application/json'
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject invalid key"
))

test("Missing API key", 401, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Content-Type': 'application/json'
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject missing auth header"
))

test("Missing 'alias' field", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Required field validation"
))

test("Empty steps array", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-empty-{int(time.time())}',
        'steps': [],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject empty steps"
))

test("Invalid step type", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-invalid-type-{int(time.time())}',
        'steps': [{'type': 'INVALID_TYPE', 'command': 'test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject unknown step type"
))

test("Negative CPU", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-neg-cpu-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': -1, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject negative CPU"
))

test("Zero memory", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-zero-mem-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 0, 'disk_gb': 10
    })).status_code,
    "Should reject zero memory"
))

test("Extremely high CPU (1000)", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-extreme-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 1000, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    "Should reject unrealistic CPU count"
))

# =============================================================================
# CATEGORY 4: REALISTIC TEMPLATES
# =============================================================================

print("\n" + "="*70)
print("🚀 CATEGORY 4: REALISTIC APPLICATION TEMPLATES")
print("="*70)

test("Python Flask Web App", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'flask-app-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y python3-pip python3-dev'},
            {'type': 'run', 'command': 'pip3 install flask gunicorn redis celery'},
            {'type': 'env', 'key': 'FLASK_APP', 'value': 'app.py'},
            {'type': 'env', 'key': 'FLASK_ENV', 'value': 'production'},
            {'type': 'workdir', 'path': '/app'}
        ],
        'start_cmd': 'gunicorn -b 0.0.0.0:8000 app:app',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    })).status_code,
    f"Flask app - Build: {r.json().get('build_id')}"
))

test("Node.js Express API", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'express-api-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -'},
            {'type': 'run', 'command': 'apt-get install -y nodejs'},
            {'type': 'run', 'command': 'npm install -g pm2'},
            {'type': 'env', 'key': 'NODE_ENV', 'value': 'production'},
            {'type': 'env', 'key': 'PORT', 'value': '3000'},
            {'type': 'workdir', 'path': '/app'}
        ],
        'start_cmd': 'pm2 start server.js --no-daemon',
        'ready_cmd': {'type': 'port', 'port': 3000},
        'cpu': 4, 'memory_mb': 4096, 'disk_gb': 20
    })).status_code,
    f"Express API - Build: {r.json().get('build_id')}"
))

test("PostgreSQL Database", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'postgres-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y postgresql-14'},
            {'type': 'env', 'key': 'POSTGRES_PASSWORD', 'value': 'secret'},
            {'type': 'env', 'key': 'POSTGRES_DB', 'value': 'myapp'}
        ],
        'start_cmd': 'service postgresql start',
        'ready_cmd': {'type': 'port', 'port': 5432},
        'cpu': 2, 'memory_mb': 4096, 'disk_gb': 20
    })).status_code,
    f"PostgreSQL - Build: {r.json().get('build_id')}"
))

test("Redis Cache Server", 202, lambda: (
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
    f"Redis - Build: {r.json().get('build_id')}"
))

test("Nginx Web Server", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'nginx-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y nginx'},
            {'type': 'env', 'key': 'NGINX_PORT', 'value': '80'}
        ],
        'start_cmd': 'nginx -g "daemon off;"',
        'ready_cmd': {'type': 'port', 'port': 80},
        'cpu': 2, 'memory_mb': 1024, 'disk_gb': 10
    })).status_code,
    f"Nginx - Build: {r.json().get('build_id')}"
))

# =============================================================================
# CATEGORY 5: FILE OPERATIONS
# =============================================================================

print("\n" + "="*70)
print("💾 CATEGORY 5: FILE UPLOAD & CACHING")
print("="*70)

test("Upload link request (new hash)", 200, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=h(), json={
        'files_hash': hashlib.sha256(f'unique-{time.time()}'.encode()).hexdigest(),
        'content_length': 1024
    })).status_code,
    f"Present: {r.json().get('present')}, Has URL: {bool(r.json().get('upload_url'))}"
))

test("Invalid hash length (too short)", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=h(), json={
        'files_hash': 'tooshort',
        'content_length': 1024
    })).status_code,
    "Should reject non-64-char hash"
))

test("Missing content_length", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=h(), json={
        'files_hash': 'a' * 64
    })).status_code,
    "Should require content_length"
))

test("Negative content_length", 400, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=h(), json={
        'files_hash': 'a' * 64,
        'content_length': -1
    })).status_code,
    "Should reject negative size"
))

# =============================================================================
# CATEGORY 6: BUILD STATUS & LOGS
# =============================================================================

print("\n" + "="*70)
print("📊 CATEGORY 6: BUILD STATUS & LOGS")
print("="*70)

def test_build_status():
    b = requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'qa-status-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10
    }).json()
    
    time.sleep(1)
    r = requests.get(f'{BASE_URL}/v1/templates/build/{b["build_id"]}/status', headers=h())
    status_data = r.json()
    
    return r.status_code, f"Status: {status_data.get('status')}, Progress: {status_data.get('progress')}%"

test("Build status check", 200, test_build_status)

def test_sse_logs():
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

test("SSE log streaming", 200, test_sse_logs)

test("List available templates", 200, lambda: (
    (r := requests.get(f'{BASE_URL}/v1/templates?limit=5', headers=h())).status_code,
    f"Found {len(r.json().get('data', []))} templates"
))

test("Non-existent build_id", 404, lambda: (
    (r := requests.get(f'{BASE_URL}/v1/templates/build/bld_nonexistent123/status', headers=h())).status_code,
    "Should return 404 for invalid build_id"
))

# =============================================================================
# CATEGORY 7: COMPLEX COMBINATIONS
# =============================================================================

print("\n" + "="*70)
print("🎯 CATEGORY 7: COMPLEX SCENARIOS")
print("="*70)

test("Full stack app (Python + Redis + Nginx)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'fullstack-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y python3-pip redis-server nginx'},
            {'type': 'run', 'command': 'pip3 install flask redis gunicorn'},
            {'type': 'env', 'key': 'REDIS_URL', 'value': 'redis://localhost:6379'},
            {'type': 'env', 'key': 'FLASK_APP', 'value': 'app.py'},
            {'type': 'workdir', 'path': '/app'}
        ],
        'start_cmd': 'sh -c "redis-server --daemonize yes && gunicorn app:app"',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 4, 'memory_mb': 4096, 'disk_gb': 20
    })).status_code,
    f"Full stack - Build: {r.json().get('build_id')}"
))

test("Development environment (Git + Python + Node)", 202, lambda: (
    (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=h(), json={
        'alias': f'dev-env-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y git curl wget vim'},
            {'type': 'run', 'command': 'apt-get install -y python3-pip'},
            {'type': 'run', 'command': 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -'},
            {'type': 'run', 'command': 'apt-get install -y nodejs'},
            {'type': 'env', 'key': 'EDITOR', 'value': 'vim'}
        ],
        'cpu': 2, 'memory_mb': 4096, 'disk_gb': 30
    })).status_code,
    f"Dev environment - Build: {r.json().get('build_id')}"
))

# =============================================================================
# SUMMARY
# =============================================================================

print(f"\n{'='*70}")
print(f"📊 QA TEST SUMMARY")
print(f"{'='*70}")
print(f"Total Tests: {total}")
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Success Rate: {100*passed//total if total > 0 else 0}%")

if passed / total >= 0.95:
    print(f"\n🎉 EXCELLENT! API is production ready!")
    print(f"   All critical functionality working perfectly")
elif passed / total >= 0.85:
    print(f"\n✅ VERY GOOD! Minor issues to address")
elif passed / total >= 0.70:
    print(f"\n⚠️  GOOD - Some issues found")
else:
    print(f"\n❌ NEEDS WORK - Significant issues")

print(f"\n{'='*70}")
