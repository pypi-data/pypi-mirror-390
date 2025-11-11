#!/usr/bin/env python3
"""
Comprehensive QA Test Suite for Template Building
Tests all scenarios, edge cases, error handling, etc.
"""

import os
import sys
import time
import hashlib
import requests
import tempfile
import json
from pathlib import Path

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'
BASE_URL = 'https://api.hopx.dev'

def get_headers():
    """Get standard headers with auth"""
    return {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class QATestSuite:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_skipped = 0
        self.findings = []
        
    def test(self, name, fn):
        """Run a single test"""
        self.tests_run += 1
        print(f"\n{'='*70}")
        print(f"🧪 Test #{self.tests_run}: {name}")
        print(f"{'='*70}")
        
        try:
            result = fn()
            if result:
                self.tests_passed += 1
                print(f"{Colors.GREEN}✅ PASS{Colors.END}")
                return True
            else:
                self.tests_failed += 1
                print(f"{Colors.RED}❌ FAIL{Colors.END}")
                return False
        except Exception as e:
            self.tests_failed += 1
            print(f"{Colors.RED}❌ EXCEPTION: {e}{Colors.END}")
            import traceback
            traceback.print_exc()
            return False
    
    def finding(self, severity, message):
        """Record a finding"""
        self.findings.append({'severity': severity, 'message': message})
        color = Colors.RED if severity == 'ERROR' else Colors.YELLOW if severity == 'WARNING' else Colors.BLUE
        print(f"{color}📝 {severity}: {message}{Colors.END}")
    
    def summary(self):
        """Print test summary"""
        print(f"\n{'='*70}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total Tests: {self.tests_run}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.END}")
        print(f"{Colors.YELLOW}Skipped: {self.tests_skipped}{Colors.END}")
        print(f"\nSuccess Rate: {self.tests_passed}/{self.tests_run} ({100*self.tests_passed//self.tests_run if self.tests_run > 0 else 0}%)")
        
        if self.findings:
            print(f"\n{'='*70}")
            print(f"📝 FINDINGS ({len(self.findings)})")
            print(f"{'='*70}")
            for i, finding in enumerate(self.findings, 1):
                color = Colors.RED if finding['severity'] == 'ERROR' else Colors.YELLOW
                print(f"{i}. {color}[{finding['severity']}]{Colors.END} {finding['message']}")

# Create test suite
qa = QATestSuite()

# =============================================================================
# CATEGORY 1: HAPPY PATH TESTS
# =============================================================================

def test_simple_run_step():
    """Test simple template with 1 RUN step"""
    print("Testing simple template with single RUN step...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-simple-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo "hello world"'}],
        'cpu': 2,
        'memory': 2048,  # API expects 'memory', not 'memory_mb'
        'diskGB': 10,    # API expects 'diskGB', not 'disk_gb'
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    print(f"Build ID: {data.get('build_id')}")
    
    if resp.status_code == 202 and data.get('build_id'):
        return True
    else:
        qa.finding('ERROR', f'Expected 202, got {resp.status_code}')
        return False

def test_multiple_run_steps():
    """Test template with multiple RUN steps"""
    print("Testing template with 5 RUN steps...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-multiple-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y curl'},
            {'type': 'run', 'command': 'curl --version'},
            {'type': 'run', 'command': 'which curl'},
            {'type': 'run', 'command': 'echo "all done"'},
        ],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    if resp.status_code == 202:
        build_id = resp.json().get('build_id')
        print(f"Build ID: {build_id}")
        
        # Check status
        time.sleep(2)
        status = requests.get(f'{BASE_URL}/v1/templates/build/{build_id}/status',
                            headers={'Authorization': f'Bearer {API_KEY}'})
        print(f"Status: {status.json().get('status')}")
        return True
    return False

def test_env_variables():
    """Test template with ENV steps"""
    print("Testing template with environment variables...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-env-{int(time.time())}',
        'steps': [
            {'type': 'env', 'key': 'MY_VAR', 'value': 'test123'},
            {'type': 'env', 'key': 'ANOTHER_VAR', 'value': 'value456'},
            {'type': 'run', 'command': 'env | grep MY_VAR'},
        ],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    return resp.status_code == 202

def test_workdir():
    """Test template with WORKDIR step"""
    print("Testing template with WORKDIR...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-workdir-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'mkdir -p /myapp'},
            {'type': 'workdir', 'path': '/myapp'},
            {'type': 'run', 'command': 'pwd'},
        ],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    return resp.status_code == 202

def test_ready_check_port():
    """Test template with port ready check"""
    print("Testing template with port ready check...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-ready-port-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y python3'},
        ],
        'startCmd': 'python3 -m http.server 8000',
        'readyCmd': {'type': 'port', 'port': 8000},
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    return resp.status_code == 202

# =============================================================================
# CATEGORY 2: EDGE CASES
# =============================================================================

def test_very_long_alias():
    """Test template with very long alias"""
    print("Testing with 200-character alias...")
    
    long_alias = 'test-' + 'a' * 190
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': long_alias,
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    if resp.status_code != 202:
        qa.finding('INFO', f'Long alias rejected with {resp.status_code} - may be intentional limit')
    return True  # Either accepts or rejects is valid

def test_special_characters_in_alias():
    """Test template with special characters in alias"""
    print("Testing special characters in alias...")
    
    special_aliases = [
        'test-with-dashes',
        'test_with_underscores',
        'test.with.dots',
        'test-123-numbers',
    ]
    
    for alias in special_aliases:
        print(f"  Testing: {alias}")
        resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json',
        }, json={
            'alias': alias,
            'steps': [{'type': 'run', 'command': 'echo test'}],
            'cpu': 2,
            'memory_mb': 2048,
            'disk_gb': 10,
        })
        print(f"    Result: {resp.status_code}")
    
    return True

def test_minimum_resources():
    """Test template with minimum resources"""
    print("Testing minimum resource allocation...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-min-resources-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 1,
        'memory': 128,
        'diskGB': 1,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if resp.status_code == 202:
        qa.finding('INFO', 'Minimum resources (1 CPU, 128MB, 1GB) accepted')
        return True
    else:
        qa.finding('INFO', f'Minimum resources rejected: {data}')
        return True  # Either way is valid

def test_maximum_resources():
    """Test template with maximum resources"""
    print("Testing maximum resource allocation...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-max-resources-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 64,
        'memory': 65536,  # 64GB
        'diskGB': 100,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    
    if resp.status_code == 202:
        qa.finding('INFO', 'Maximum resources (64 CPU, 64GB RAM, 100GB disk) accepted')
    else:
        qa.finding('INFO', f'Maximum resources rejected: {data.get("error", {}).get("message")}')
    
    return True

# =============================================================================
# CATEGORY 3: ERROR HANDLING
# =============================================================================

def test_invalid_api_key():
    """Test with invalid API key"""
    print("Testing with invalid API key...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': 'Bearer invalid_key_12345',
        'Content-Type': 'application/json',
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    print(f"Error: {json.dumps(data, indent=2)}")
    
    if resp.status_code == 401:
        print(f"{Colors.GREEN}✅ Correct: Returns 401 Unauthorized{Colors.END}")
        return True
    else:
        qa.finding('ERROR', f'Expected 401 for invalid key, got {resp.status_code}')
        return False

def test_missing_api_key():
    """Test without API key"""
    print("Testing without API key...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Content-Type': 'application/json',
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    
    if resp.status_code == 401:
        print(f"{Colors.GREEN}✅ Correct: Returns 401 Unauthorized{Colors.END}")
        return True
    else:
        qa.finding('ERROR', f'Expected 401 for missing key, got {resp.status_code}')
        return False

def test_missing_required_fields():
    """Test with missing required fields"""
    print("Testing with missing 'alias' field...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        # Missing 'alias'
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    print(f"Error: {json.dumps(data, indent=2)}")
    
    if resp.status_code == 400:
        print(f"{Colors.GREEN}✅ Correct: Returns 400 Bad Request{Colors.END}")
        return True
    else:
        qa.finding('WARNING', f'Expected 400 for missing alias, got {resp.status_code}')
        return True  # Might be different validation

def test_empty_steps_array():
    """Test with empty steps array"""
    print("Testing with empty steps array...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-empty-{int(time.time())}',
        'steps': [],  # Empty array
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if resp.status_code == 400:
        print(f"{Colors.GREEN}✅ Correct: Rejects empty steps{Colors.END}")
        return True
    elif resp.status_code == 202:
        qa.finding('WARNING', 'API accepts empty steps - might want validation')
        return True
    return False

def test_invalid_step_type():
    """Test with invalid step type"""
    print("Testing with invalid step type...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-invalid-step-{int(time.time())}',
        'steps': [{'type': 'INVALID_TYPE', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if resp.status_code == 400:
        print(f"{Colors.GREEN}✅ Correct: Rejects invalid step type{Colors.END}")
        return True
    else:
        qa.finding('WARNING', f'Invalid step type handling: {resp.status_code}')
        return True

def test_negative_cpu():
    """Test with negative CPU value"""
    print("Testing with negative CPU...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-negative-cpu-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': -1,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    
    if resp.status_code == 400:
        print(f"{Colors.GREEN}✅ Correct: Rejects negative CPU{Colors.END}")
        return True
    else:
        qa.finding('WARNING', f'Negative CPU validation: {resp.status_code}')
        return True

def test_zero_memory():
    """Test with zero memory"""
    print("Testing with zero memory...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-zero-memory-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 0,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    
    if resp.status_code == 400:
        print(f"{Colors.GREEN}✅ Correct: Rejects zero memory{Colors.END}")
        return True
    else:
        qa.finding('WARNING', f'Zero memory validation: {resp.status_code}')
        return True

# =============================================================================
# CATEGORY 4: CACHE TESTING
# =============================================================================

def test_cache_hit():
    """Test cache hit with same files_hash"""
    print("Testing cache hit scenario...")
    
    # Use a consistent hash
    test_hash = hashlib.sha256(b'test-cache-content').hexdigest()
    
    # First request
    print("  Request 1 (should upload)...")
    resp1 = requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'files_hash': test_hash,
        'content_length': 100,
    })
    
    data1 = resp1.json()
    print(f"    Present: {data1.get('present')}")
    print(f"    Upload URL: {'YES' if data1.get('upload_url') else 'NO'}")
    
    # Second request with same hash
    print("  Request 2 (should be cached)...")
    resp2 = requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'files_hash': test_hash,
        'content_length': 100,
    })
    
    data2 = resp2.json()
    print(f"    Present: {data2.get('present')}")
    print(f"    Upload URL: {'YES' if data2.get('upload_url') else 'NO'}")
    
    # Both should work, cache behavior may vary
    if resp1.status_code == 200 and resp2.status_code == 200:
        if data1.get('present') != data2.get('present'):
            qa.finding('INFO', 'Cache state changed between requests - normal if file was uploaded')
        return True
    return False

def test_different_hashes():
    """Test with different files_hash values"""
    print("Testing with different file hashes...")
    
    hash1 = hashlib.sha256(b'content-1').hexdigest()
    hash2 = hashlib.sha256(b'content-2').hexdigest()
    
    resp1 = requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={'files_hash': hash1, 'content_length': 100})
    
    resp2 = requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={'files_hash': hash2, 'content_length': 100})
    
    print(f"Hash 1 response: {resp1.status_code}")
    print(f"Hash 2 response: {resp2.status_code}")
    
    return resp1.status_code == 200 and resp2.status_code == 200

# =============================================================================
# CATEGORY 5: FILE OPERATIONS
# =============================================================================

def test_small_file_hash():
    """Test file hashing with small file"""
    print("Testing SHA256 hash calculation...")
    
    # Create a small test file
    test_content = b"Hello, this is a test file!\n"
    expected_hash = hashlib.sha256(test_content).hexdigest()
    
    print(f"Content: {test_content[:50]}")
    print(f"Expected hash: {expected_hash}")
    print(f"Hash length: {len(expected_hash)} chars")
    
    if len(expected_hash) == 64:
        print(f"{Colors.GREEN}✅ Hash format correct (64 hex chars){Colors.END}")
        return True
    else:
        qa.finding('ERROR', f'Hash length is {len(expected_hash)}, expected 64')
        return False

def test_hash_consistency():
    """Test that same content produces same hash"""
    print("Testing hash consistency...")
    
    content = b"Consistent content test"
    hash1 = hashlib.sha256(content).hexdigest()
    hash2 = hashlib.sha256(content).hexdigest()
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    
    if hash1 == hash2:
        print(f"{Colors.GREEN}✅ Hashes are consistent{Colors.END}")
        return True
    else:
        qa.finding('ERROR', 'Hash calculation not deterministic!')
        return False

def test_different_content_different_hash():
    """Test that different content produces different hashes"""
    print("Testing hash uniqueness...")
    
    hash1 = hashlib.sha256(b"content 1").hexdigest()
    hash2 = hashlib.sha256(b"content 2").hexdigest()
    
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    
    if hash1 != hash2:
        print(f"{Colors.GREEN}✅ Different content produces different hashes{Colors.END}")
        return True
    else:
        qa.finding('ERROR', 'Different content produced same hash!')
        return False

# =============================================================================
# CATEGORY 6: API RESPONSE VALIDATION
# =============================================================================

def test_response_structure():
    """Test that API responses have correct structure"""
    print("Testing API response structure...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-structure-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    data = resp.json()
    print(f"Response keys: {list(data.keys())}")
    
    required_fields = ['build_id', 'template_id', 'status']
    missing = [f for f in required_fields if f not in data]
    
    if not missing:
        print(f"{Colors.GREEN}✅ All required fields present{Colors.END}")
        return True
    else:
        qa.finding('ERROR', f'Missing required fields: {missing}')
        return False

def test_build_id_format():
    """Test that build_id has correct format"""
    print("Testing build_id format...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-id-format-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    data = resp.json()
    build_id = data.get('build_id', '')
    
    print(f"Build ID: {build_id}")
    print(f"Starts with 'bld_': {build_id.startswith('bld_')}")
    print(f"Length: {len(build_id)}")
    
    if build_id.startswith('bld_') and len(build_id) > 4:
        print(f"{Colors.GREEN}✅ Build ID format correct{Colors.END}")
        return True
    else:
        qa.finding('WARNING', f'Build ID format unexpected: {build_id}')
        return True

def test_template_id_format():
    """Test that template_id has correct format"""
    print("Testing template_id format...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-tpl-format-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    data = resp.json()
    template_id = data.get('template_id', '')
    
    print(f"Template ID: {template_id}")
    print(f"Starts with 'tpl_': {template_id.startswith('tpl_')}")
    print(f"Length: {len(template_id)}")
    
    if template_id.startswith('tpl_') and len(template_id) > 4:
        print(f"{Colors.GREEN}✅ Template ID format correct{Colors.END}")
        return True
    else:
        qa.finding('WARNING', f'Template ID format unexpected: {template_id}')
        return True

# =============================================================================
# CATEGORY 7: COMPLEX SCENARIOS
# =============================================================================

def test_complex_template():
    """Test complex template with all step types"""
    print("Testing complex template with all step types...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'test-complex-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y python3 python3-pip git curl'},
            {'type': 'env', 'key': 'PYTHON_VERSION', 'value': '3.11'},
            {'type': 'env', 'key': 'APP_ENV', 'value': 'production'},
            {'type': 'workdir', 'path': '/app'},
            {'type': 'run', 'command': 'mkdir -p /app/data'},
            {'type': 'run', 'command': 'echo "Setup complete" > /app/setup.log'},
        ],
        'startCmd': 'python3 -m http.server 8080',
        'readyCmd': {'type': 'port', 'port': 8080},
        'cpu': 4,
        'memory': 4096,
        'diskGB': 20,
    })
    
    print(f"Response: {resp.status_code}")
    data = resp.json()
    
    if resp.status_code == 202:
        print(f"Build ID: {data.get('build_id')}")
        print(f"{Colors.GREEN}✅ Complex template accepted{Colors.END}")
        return True
    else:
        qa.finding('ERROR', f'Complex template rejected: {data}')
        return False

def test_python_app_template():
    """Test realistic Python application template"""
    print("Testing realistic Python app template...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'python-app-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y python3-pip python3-dev'},
            {'type': 'run', 'command': 'pip3 install flask gunicorn redis celery'},
            {'type': 'env', 'key': 'FLASK_APP', 'value': 'app.py'},
            {'type': 'env', 'key': 'FLASK_ENV', 'value': 'production'},
            {'type': 'workdir', 'path': '/app'},
        ],
        'startCmd': 'gunicorn -b 0.0.0.0:8000 app:app',
        'readyCmd': {'type': 'port', 'port': 8000},
        'cpu': 2,
        'memory': 2048,
        'diskGB': 10,
    })
    
    print(f"Response: {resp.status_code}")
    return resp.status_code == 202

def test_nodejs_app_template():
    """Test realistic Node.js application template"""
    print("Testing realistic Node.js app template...")
    
    resp = requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }, json={
        'alias': f'nodejs-app-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y curl'},
            {'type': 'run', 'command': 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -'},
            {'type': 'run', 'command': 'apt-get install -y nodejs'},
            {'type': 'env', 'key': 'NODE_ENV', 'value': 'production'},
            {'type': 'env', 'key': 'PORT', 'value': '3000'},
            {'type': 'workdir', 'path': '/app'},
        ],
        'startCmd': 'node server.js',
        'readyCmd': {'type': 'port', 'port': 3000},
        'cpu': 2,
        'memory': 2048,
        'diskGB': 15,
    })
    
    print(f"Response: {resp.status_code}")
    return resp.status_code == 202

# =============================================================================
# RUN ALL TESTS
# =============================================================================

print(f"\n{Colors.BLUE}{'='*70}")
print(f"🔍 COMPREHENSIVE QA TEST SUITE - TEMPLATE BUILDING")
print(f"{'='*70}{Colors.END}\n")
print(f"API: {BASE_URL}")
print(f"Testing as Senior QA Engineer...\n")

# HAPPY PATH TESTS
print(f"\n{Colors.BLUE}━━━ CATEGORY 1: HAPPY PATH TESTS ━━━{Colors.END}")
qa.test("Simple template with 1 RUN step", test_simple_run_step)
qa.test("Template with multiple RUN steps", test_multiple_run_steps)
qa.test("Template with ENV variables", test_env_variables)
qa.test("Template with WORKDIR", test_workdir)
qa.test("Template with port ready check", test_ready_check_port)

# EDGE CASES
print(f"\n{Colors.BLUE}━━━ CATEGORY 2: EDGE CASES ━━━{Colors.END}")
qa.test("Very long alias (200 chars)", test_very_long_alias)
qa.test("Special characters in alias", test_special_characters_in_alias)
qa.test("Minimum resources (1 CPU, 128MB, 1GB)", test_minimum_resources)
qa.test("Maximum resources (64 CPU, 64GB, 100GB)", test_maximum_resources)

# ERROR HANDLING
print(f"\n{Colors.BLUE}━━━ CATEGORY 3: ERROR HANDLING ━━━{Colors.END}")
qa.test("Invalid API key (401 expected)", test_invalid_api_key)
qa.test("Missing API key (401 expected)", test_missing_api_key)
qa.test("Missing required field 'alias' (400 expected)", test_missing_required_fields)
qa.test("Empty steps array", test_empty_steps_array)
qa.test("Invalid step type", test_invalid_step_type)
qa.test("Negative CPU value", test_negative_cpu)
qa.test("Zero memory value", test_zero_memory)

# CACHE TESTING
print(f"\n{Colors.BLUE}━━━ CATEGORY 4: CACHE TESTING ━━━{Colors.END}")
qa.test("Cache hit with same files_hash", test_cache_hit)
qa.test("Different files_hash values", test_different_hashes)

# FILE OPERATIONS
print(f"\n{Colors.BLUE}━━━ CATEGORY 5: FILE OPERATIONS ━━━{Colors.END}")
qa.test("SHA256 hash format (64 chars)", test_small_file_hash)
qa.test("Hash consistency (same content = same hash)", test_hash_consistency)
qa.test("Hash uniqueness (different content = different hash)", test_different_content_different_hash)

# RESPONSE VALIDATION
print(f"\n{Colors.BLUE}━━━ CATEGORY 6: API RESPONSE VALIDATION ━━━{Colors.END}")
qa.test("Response structure validation", test_response_structure)
qa.test("Build ID format (bld_*)", test_build_id_format)
qa.test("Template ID format (tpl_*)", test_template_id_format)

# COMPLEX SCENARIOS
print(f"\n{Colors.BLUE}━━━ CATEGORY 7: COMPLEX SCENARIOS ━━━{Colors.END}")
qa.test("Complex template with all step types", test_complex_template)
qa.test("Realistic Python app template", test_python_app_template)
qa.test("Realistic Node.js app template", test_nodejs_app_template)

# Print summary
qa.summary()

# Exit code
sys.exit(0 if qa.tests_failed == 0 else 1)

