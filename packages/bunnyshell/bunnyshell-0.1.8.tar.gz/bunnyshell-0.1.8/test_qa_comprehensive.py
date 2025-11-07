#!/usr/bin/env python3
"""
Senior QA Engineer - Comprehensive Template Building Tests
Tests all scenarios, edge cases, error handling
"""

import requests
import time
import hashlib
import json

API_KEY = 'hopx_test_1e0a0fba0e81a124662a7cf0535d751b311937c2d6b7acfe7d9b88879f338ad0'
BASE_URL = 'https://api.hopx.dev'

def headers():
    return {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

class QA:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0
        self.findings = []
    
    def test(self, name, expected_status, fn):
        self.total += 1
        print(f"\n{'='*70}")
        print(f"Test #{self.total}: {name}")
        print(f"Expected: HTTP {expected_status}")
        print(f"{'='*70}")
        
        try:
            result = fn()
            status = result.get('status', 0)
            data = result.get('data', {})
            
            print(f"Got: HTTP {status}")
            
            if status == expected_status:
                self.passed += 1
                print(f"✅ PASS")
                if 'note' in result:
                    print(f"   📝 {result['note']}")
                return True
            else:
                self.failed += 1
                print(f"❌ FAIL - Expected {expected_status}, got {status}")
                if 'error' in data:
                    print(f"   Error: {data['error']}")
                self.findings.append(f"{name}: Expected {expected_status}, got {status}")
                return False
        except Exception as e:
            self.failed += 1
            print(f"❌ EXCEPTION: {e}")
            self.findings.append(f"{name}: Exception - {str(e)}")
            return False
    
    def summary(self):
        print(f"\n{'='*70}")
        print(f"📊 QA TEST SUMMARY")
        print(f"{'='*70}")
        print(f"Total: {self.total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {100*self.passed//self.total if self.total > 0 else 0}%")
        
        if self.findings:
            print(f"\n📝 FINDINGS ({len(self.findings)}):")
            for i, f in enumerate(self.findings, 1):
                print(f"  {i}. {f}")

qa = QA()

print("🔍 SENIOR QA ENGINEER - COMPREHENSIVE TEST SUITE")
print(f"API: {BASE_URL}")
print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("="*70)

# =============================================================================
# HAPPY PATH TESTS
# =============================================================================

print("\n🟢 CATEGORY 1: HAPPY PATH TESTS")

qa.test("Simple RUN step", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-simple-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo "hello"'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json(),
    'note': f"Build ID: {r.json().get('build_id', 'N/A')}"
})

qa.test("Multiple RUN steps (5 steps)", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-multi-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y curl'},
            {'type': 'run', 'command': 'curl --version'},
            {'type': 'run', 'command': 'which curl'},
            {'type': 'run', 'command': 'echo done'},
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("ENV variables", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-env-{int(time.time())}',
        'steps': [
            {'type': 'env', 'key': 'MY_VAR', 'value': 'test123'},
            {'type': 'run', 'command': 'env | grep MY_VAR'},
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("WORKDIR step", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-workdir-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'mkdir -p /myapp'},
            {'type': 'workdir', 'path': '/myapp'},
            {'type': 'run', 'command': 'pwd'},
        ],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Ready check - PORT", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-ready-port-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'apt-get update'}],
        'start_cmd': 'python3 -m http.server 8000',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Ready check - HTTP", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-ready-http-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'apt-get update'}],
        'start_cmd': 'python3 -m http.server 8000',
        'ready_cmd': {'type': 'http', 'url': 'http://localhost:8000'},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

# =============================================================================
# EDGE CASES
# =============================================================================

print("\n🟡 CATEGORY 2: EDGE CASES")

qa.test("Long alias (100 chars)", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': 'test-' + 'a' * 95,
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Alias with special chars (dashes, underscores, dots)", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': 'test-with_special.chars-123',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Minimum resources (1 CPU, 128MB, 1GB)", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-min-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 1, 'memory_mb': 128, 'disk_gb': 1,
    })).status_code,
    'data': r.json()
})

qa.test("High resources (16 CPU, 16GB, 50GB)", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-high-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 16, 'memory_mb': 16384, 'disk_gb': 50,
    })).status_code,
    'data': r.json()
})

# =============================================================================
# ERROR HANDLING
# =============================================================================

print("\n🔴 CATEGORY 3: ERROR HANDLING")

qa.test("Invalid API key", 401, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Authorization': 'Bearer invalid_key_xxx',
        'Content-Type': 'application/json',
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Missing API key", 401, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers={
        'Content-Type': 'application/json',
    }, json={
        'alias': 'test',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Missing 'alias' field", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Missing 'steps' field", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': 'test',
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Empty steps array", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-empty-{int(time.time())}',
        'steps': [],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Invalid step type", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-invalid-{int(time.time())}',
        'steps': [{'type': 'INVALID', 'command': 'test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Negative CPU", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-neg-cpu-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': -1, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Zero memory", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-zero-mem-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 0, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Negative disk", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-neg-disk-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': -10,
    })).status_code,
    'data': r.json()
})

# =============================================================================
# CACHE TESTS
# =============================================================================

print("\n💾 CATEGORY 4: CACHE TESTS")

qa.test("Upload link - first request", 200, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=headers(), json={
        'files_hash': hashlib.sha256(f'test-{time.time()}'.encode()).hexdigest(),
        'content_length': 1024,
    })).status_code,
    'data': r.json(),
    'note': f"Present: {r.json().get('present')}, Has URL: {bool(r.json().get('upload_url'))}"
})

def test_cache():
    test_hash = 'a' * 64
    r1 = requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=headers(), json={
        'files_hash': test_hash,
        'content_length': 1024,
    })
    r2 = requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=headers(), json={
        'files_hash': test_hash,
        'content_length': 1024,
    })
    return {
        'status': r2.status_code,
        'data': r2.json(),
        'note': f"Request 1 present: {r1.json().get('present')}, Request 2 present: {r2.json().get('present')}"
    }

qa.test("Upload link - same hash (cache test)", 200, test_cache)

# =============================================================================
# COMPLEX SCENARIOS  
# =============================================================================

print("\n🚀 CATEGORY 5: REALISTIC SCENARIOS")

qa.test("Python Web App Template", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'python-web-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update -qq'},
            {'type': 'run', 'command': 'apt-get install -y python3-pip'},
            {'type': 'run', 'command': 'pip3 install flask gunicorn'},
            {'type': 'env', 'key': 'FLASK_APP', 'value': 'app.py'},
            {'type': 'workdir', 'path': '/app'},
        ],
        'start_cmd': 'gunicorn -b 0.0.0.0:8000 app:app',
        'ready_cmd': {'type': 'port', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Node.js API Template", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'nodejs-api-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash -'},
            {'type': 'run', 'command': 'apt-get install -y nodejs'},
            {'type': 'env', 'key': 'NODE_ENV', 'value': 'production'},
            {'type': 'workdir', 'path': '/app'},
        ],
        'start_cmd': 'node server.js',
        'ready_cmd': {'type': 'port', 'port': 3000},
        'cpu': 4, 'memory_mb': 4096, 'disk_gb': 20,
    })).status_code,
    'data': r.json()
})

qa.test("Database Server Template", 202, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'postgres-{int(time.time())}',
        'steps': [
            {'type': 'run', 'command': 'apt-get update'},
            {'type': 'run', 'command': 'apt-get install -y postgresql postgresql-contrib'},
            {'type': 'env', 'key': 'POSTGRES_PASSWORD', 'value': 'secret'},
            {'type': 'env', 'key': 'POSTGRES_DB', 'value': 'myapp'},
        ],
        'start_cmd': 'pg_ctlcluster 14 main start',
        'ready_cmd': {'type': 'port', 'port': 5432},
        'cpu': 2, 'memory_mb': 4096, 'disk_gb': 20,
    })).status_code,
    'data': r.json()
})

# =============================================================================
# DATA VALIDATION
# =============================================================================

print("\n📋 CATEGORY 6: DATA VALIDATION")

qa.test("Build status polling", 200, lambda: {
    # First create a build
    build = requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-status-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    }).json()
    
    build_id = build.get('build_id')
    time.sleep(1)
    
    # Check status
    r = requests.get(f'{BASE_URL}/v1/templates/build/{build_id}/status', headers=headers())
    return {
        'status': r.status_code,
        'data': r.json(),
        'note': f"Status: {r.json().get('status')}, Progress: {r.json().get('progress')}%"
    }
})

qa.test("SSE log streaming connection", 200, lambda: {
    # First create a build
    build = requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-logs-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    }).json()
    
    build_id = build.get('build_id')
    
    # Connect to logs
    r = requests.get(f'{BASE_URL}/v1/templates/build/{build_id}/logs', headers={
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'text/event-stream',
    }, stream=True)
    
    return {
        'status': r.status_code,
        'data': {},
        'note': f"Content-Type: {r.headers.get('content-type')}"
    }
})

qa.test("List templates", 200, lambda: {
    'status': (r := requests.get(f'{BASE_URL}/v1/templates?limit=5', headers=headers())).status_code,
    'data': r.json(),
    'note': f"Found {len(r.json().get('data', []))} templates"
})

# =============================================================================
# INVALID FIELD VALUES
# =============================================================================

print("\n⚠️  CATEGORY 7: INVALID INPUTS")

qa.test("Invalid ready_cmd type", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-invalid-ready-{int(time.time())}',
        'steps': [{'type': 'run', 'command': 'echo test'}],
        'ready_cmd': {'type': 'INVALID_TYPE', 'port': 8000},
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Missing command in RUN step", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/build', headers=headers(), json={
        'alias': f'qa-no-cmd-{int(time.time())}',
        'steps': [{'type': 'run'}],  # Missing command
        'cpu': 2, 'memory_mb': 2048, 'disk_gb': 10,
    })).status_code,
    'data': r.json()
})

qa.test("Invalid files_hash (not 64 chars)", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=headers(), json={
        'files_hash': 'short_hash',  # Not 64 chars
        'content_length': 1024,
    })).status_code,
    'data': r.json()
})

qa.test("Missing content_length", 400, lambda: {
    'status': (r := requests.post(f'{BASE_URL}/v1/templates/files/upload-link', headers=headers(), json={
        'files_hash': 'a' * 64,
        # Missing content_length
    })).status_code,
    'data': r.json()
})

qa.test("Non-existent build_id in status", 404, lambda: {
    'status': (r := requests.get(f'{BASE_URL}/v1/templates/build/bld_nonexistent/status', 
                                 headers=headers())).status_code,
    'data': r.json()
})

# Print summary
qa.summary()

print(f"\n{'='*70}")
print(f"🎯 QA ASSESSMENT")
print(f"{'='*70}")
if qa.passed / qa.total >= 0.9:
    print(f"✅ EXCELLENT: {qa.passed}/{qa.total} tests passed ({100*qa.passed//qa.total}%)")
    print(f"   API is production ready!")
elif qa.passed / qa.total >= 0.7:
    print(f"⚠️  GOOD: {qa.passed}/{qa.total} tests passed ({100*qa.passed//qa.total}%)")
    print(f"   Minor issues to address")
else:
    print(f"❌ NEEDS WORK: {qa.passed}/{qa.total} tests passed ({100*qa.passed//qa.total}%)")
    print(f"   Significant issues found")

