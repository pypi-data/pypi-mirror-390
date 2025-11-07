"""
Comprehensive agent testing to identify bugs and missing features.

Tests all agent endpoints and documents issues.
"""

import os
import sys
import json
import base64
from bunnyshell import Sandbox

class AgentTester:
    def __init__(self):
        self.issues = []
        self.working = []
        self.warnings = []
        
    def log_issue(self, severity, category, title, description, endpoint=None):
        """Log an issue."""
        self.issues.append({
            "severity": severity,  # critical, high, medium, low
            "category": category,  # bug, missing_feature, dx_issue, performance
            "title": title,
            "description": description,
            "endpoint": endpoint,
        })
    
    def log_working(self, title, details):
        """Log working feature."""
        self.working.append({"title": title, "details": details})
    
    def log_warning(self, title, details):
        """Log warning."""
        self.warnings.append({"title": title, "details": details})
    
    def test_all(self, sandbox):
        """Run all tests."""
        print("=" * 70)
        print("🧪 COMPREHENSIVE AGENT TESTING")
        print("=" * 70)
        print()
        
        self.test_health(sandbox)
        self.test_info(sandbox)
        self.test_file_write(sandbox)
        self.test_file_read(sandbox)
        self.test_file_list(sandbox)
        self.test_file_exists(sandbox)
        self.test_file_upload_download(sandbox)
        self.test_code_execution(sandbox)
        self.test_code_rich_output(sandbox)
        self.test_commands(sandbox)
        self.test_binary_files(sandbox)
        self.test_error_messages(sandbox)
        self.test_performance(sandbox)
        
    def test_health(self, sandbox):
        """Test /health endpoint."""
        print("1️⃣  Testing /health endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            response = httpx.get(f"{agent_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_working("Health endpoint", f"Status: {response.status_code}")
                print("✅ Health endpoint working\n")
            else:
                self.log_issue("medium", "bug", 
                    "Health endpoint returns non-200",
                    f"Got {response.status_code}, expected 200",
                    "/health")
                print(f"⚠️  Health returned {response.status_code}\n")
        except Exception as e:
            self.log_issue("high", "bug",
                "Health endpoint failed",
                str(e),
                "/health")
            print(f"❌ Health failed: {e}\n")
    
    def test_info(self, sandbox):
        """Test /info endpoint."""
        print("2️⃣  Testing /info endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            response = httpx.get(f"{agent_url}/info", timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                self.log_working("Info endpoint", 
                    f"Agent: {data.get('agent')}, Version: {data.get('agent_version')}")
                print(f"✅ Info endpoint working")
                print(f"   Agent: {data.get('agent')}")
                print(f"   Version: {data.get('agent_version')}\n")
            else:
                self.log_issue("high", "bug",
                    "Info endpoint failed",
                    f"Status: {response.status_code}",
                    "/info")
                print(f"❌ Info failed: {response.status_code}\n")
        except Exception as e:
            self.log_issue("high", "bug",
                "Info endpoint error",
                str(e),
                "/info")
            print(f"❌ Info error: {e}\n")
    
    def test_file_write(self, sandbox):
        """Test /files/write endpoint."""
        print("3️⃣  Testing /files/write endpoint...")
        try:
            # Try to write a simple file
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Test 1: Simple text write
            response = httpx.post(
                f"{agent_url}/files/write",
                json={
                    "path": "/tmp/test.txt",
                    "content": "Hello, World!",
                    "mode": "0644"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_working("File write", "Simple text write successful")
                print("✅ File write working\n")
            else:
                self.log_issue("critical", "bug",
                    "File write fails",
                    f"Status: {response.status_code}, Body: {response.text[:200]}",
                    "/files/write")
                print(f"❌ File write failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}\n")
                
        except Exception as e:
            self.log_issue("critical", "bug",
                "File write exception",
                str(e),
                "/files/write")
            print(f"❌ File write exception: {e}\n")
    
    def test_file_read(self, sandbox):
        """Test /files/read endpoint."""
        print("4️⃣  Testing /files/read endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Test reading /etc/hostname (should exist)
            response = httpx.get(
                f"{agent_url}/files/read",
                params={"path": "/etc/hostname"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", "")
                self.log_working("File read", f"Read {len(content)} chars from /etc/hostname")
                print(f"✅ File read working ({len(content)} chars)\n")
            elif response.status_code == 403:
                self.log_issue("high", "dx_issue",
                    "File read returns 403 instead of 404",
                    "Should return 404 for not found, not 403 (confusing for users)",
                    "/files/read")
                print("⚠️  File read returns 403 (should be 404 for not found)\n")
            else:
                self.log_issue("high", "bug",
                    "File read failed",
                    f"Status: {response.status_code}",
                    "/files/read")
                print(f"❌ File read failed: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("high", "bug",
                "File read exception",
                str(e),
                "/files/read")
            print(f"❌ File read exception: {e}\n")
    
    def test_file_list(self, sandbox):
        """Test /files/list endpoint."""
        print("5️⃣  Testing /files/list endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Test listing /tmp (should exist and be accessible)
            response = httpx.get(
                f"{agent_url}/files/list",
                params={"path": "/tmp"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                files = data.get("files", [])
                self.log_working("File list", f"Listed {len(files)} items from /tmp")
                print(f"✅ File list working ({len(files)} items)\n")
            else:
                self.log_issue("critical", "bug",
                    "File list fails",
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    "/files/list")
                print(f"❌ File list failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}\n")
                
        except Exception as e:
            self.log_issue("critical", "bug",
                "File list exception",
                str(e),
                "/files/list")
            print(f"❌ File list exception: {e}\n")
    
    def test_file_exists(self, sandbox):
        """Test /files/exists endpoint."""
        print("6️⃣  Testing /files/exists endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            response = httpx.get(
                f"{agent_url}/files/exists",
                params={"path": "/etc/hostname"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                exists = data.get("exists", False)
                self.log_working("File exists", f"Returns exists={exists}")
                print(f"✅ File exists working (exists={exists})\n")
            else:
                self.log_issue("medium", "bug",
                    "File exists failed",
                    f"Status: {response.status_code}",
                    "/files/exists")
                print(f"❌ File exists failed: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("medium", "bug",
                "File exists exception",
                str(e),
                "/files/exists")
            print(f"❌ File exists exception: {e}\n")
    
    def test_file_upload_download(self, sandbox):
        """Test /files/upload and /files/download endpoints."""
        print("7️⃣  Testing /files/upload and /files/download...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Create test file
            test_data = b"Test upload data"
            
            # Upload
            response = httpx.post(
                f"{agent_url}/files/upload",
                files={"file": ("test.txt", test_data)},
                data={"path": "/tmp/uploaded.txt"},
                timeout=30
            )
            
            if response.status_code == 200:
                self.log_working("File upload", "Upload successful")
                print("✅ File upload working")
                
                # Try download
                dl_response = httpx.get(
                    f"{agent_url}/files/download",
                    params={"path": "/tmp/uploaded.txt"},
                    timeout=30
                )
                
                if dl_response.status_code == 200:
                    self.log_working("File download", f"Downloaded {len(dl_response.content)} bytes")
                    print(f"✅ File download working ({len(dl_response.content)} bytes)\n")
                else:
                    self.log_issue("high", "bug",
                        "File download failed",
                        f"Status: {dl_response.status_code}",
                        "/files/download")
                    print(f"❌ Download failed: {dl_response.status_code}\n")
            else:
                self.log_issue("high", "bug",
                    "File upload failed",
                    f"Status: {response.status_code}, Response: {response.text[:200]}",
                    "/files/upload")
                print(f"❌ Upload failed: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("high", "bug",
                "File upload/download exception",
                str(e),
                "/files/upload, /files/download")
            print(f"❌ Upload/download exception: {e}\n")
    
    def test_code_execution(self, sandbox):
        """Test /execute endpoint."""
        print("8️⃣  Testing /execute endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            response = httpx.post(
                f"{agent_url}/execute",
                json={
                    "language": "python",
                    "code": "print('Hello from test')",
                    "working_dir": "/tmp"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                stdout = data.get("stdout", "")
                stderr = data.get("stderr", "")
                exit_code = data.get("exit_code", -1)
                
                if "Hello from test" in stdout:
                    self.log_working("Code execution", f"Stdout captured correctly")
                    print(f"✅ Code execution working")
                    print(f"   Stdout: {stdout.strip()}\n")
                else:
                    self.log_issue("high", "bug",
                        "Code execution - stdout not captured",
                        f"Expected 'Hello from test', got: '{stdout}'",
                        "/execute")
                    print(f"⚠️  Stdout not captured properly")
                    print(f"   Expected: 'Hello from test'")
                    print(f"   Got: '{stdout}'\n")
                    
                if exit_code != 0:
                    self.log_warning("Exit code non-zero",
                        f"Simple print returned exit_code={exit_code}, expected 0")
                    print(f"⚠️  Exit code: {exit_code} (expected 0)\n")
                    
            else:
                self.log_issue("critical", "bug",
                    "Code execution failed",
                    f"Status: {response.status_code}",
                    "/execute")
                print(f"❌ Code execution failed: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("critical", "bug",
                "Code execution exception",
                str(e),
                "/execute")
            print(f"❌ Code execution exception: {e}\n")
    
    def test_code_rich_output(self, sandbox):
        """Test /execute/rich endpoint."""
        print("9️⃣  Testing /execute/rich endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Test matplotlib plot
            code = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

plt.figure(figsize=(6, 4))
plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
plt.title('Test Plot')
plt.savefig('/tmp/test_plot.png')
file_size = os.path.getsize('/tmp/test_plot.png')
print(f'Plot saved! Size: {file_size} bytes')
"""
            
            response = httpx.post(
                f"{agent_url}/execute/rich",
                json={
                    "language": "python",
                    "code": code,
                    "working_dir": "/tmp"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                rich_outputs = data.get("rich_outputs", [])
                stdout = data.get("stdout", "")
                
                if len(rich_outputs) > 0:
                    self.log_working("Rich output", f"Captured {len(rich_outputs)} rich outputs")
                    print(f"✅ Rich output working ({len(rich_outputs)} outputs)")
                    for output in rich_outputs:
                        print(f"   - {output.get('type')}")
                else:
                    self.log_issue("high", "missing_feature",
                        "Rich output not captured",
                        "Matplotlib plot not automatically captured in rich_outputs",
                        "/execute/rich")
                    print("⚠️  Rich output not captured (expected matplotlib plot)")
                
                if "Plot saved!" in stdout:
                    print(f"   Stdout: {stdout.strip()}\n")
                else:
                    self.log_issue("medium", "bug",
                        "Rich execution - stdout missing",
                        f"Expected 'Plot saved!', got: '{stdout}'",
                        "/execute/rich")
                    print(f"⚠️  Stdout missing: '{stdout}'\n")
                    
            else:
                self.log_issue("high", "bug",
                    "Rich execution failed",
                    f"Status: {response.status_code}",
                    "/execute/rich")
                print(f"❌ Rich execution failed: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("high", "bug",
                "Rich execution exception",
                str(e),
                "/execute/rich")
            print(f"❌ Rich execution exception: {e}\n")
    
    def test_commands(self, sandbox):
        """Test /commands/run endpoint."""
        print("🔟 Testing /commands/run endpoint...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            response = httpx.post(
                f"{agent_url}/commands/run",
                json={
                    "command": "echo 'Test command'",
                    "timeout": 10
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                stdout = data.get("stdout", "")
                exit_code = data.get("exit_code", -1)
                
                if "Test command" in stdout:
                    self.log_working("Commands", f"Command execution working")
                    print(f"✅ Commands working")
                    print(f"   Stdout: {stdout.strip()}")
                    print(f"   Exit code: {exit_code}\n")
                else:
                    self.log_issue("high", "bug",
                        "Command stdout not captured",
                        f"Expected 'Test command', got: '{stdout}'",
                        "/commands/run")
                    print(f"⚠️  Command stdout missing: '{stdout}'\n")
                    
                if exit_code != 0:
                    self.log_warning("Command exit code",
                        f"Simple echo returned exit_code={exit_code}, expected 0")
                    
            else:
                self.log_issue("critical", "bug",
                    "Command execution failed",
                    f"Status: {response.status_code}",
                    "/commands/run")
                print(f"❌ Commands failed: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("critical", "bug",
                "Commands exception",
                str(e),
                "/commands/run")
            print(f"❌ Commands exception: {e}\n")
    
    def test_binary_files(self, sandbox):
        """Test binary file support."""
        print("1️⃣1️⃣  Testing binary file support...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Create binary data
            binary_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR' + b'\x00' * 100
            
            # Test writing binary via base64
            content_b64 = base64.b64encode(binary_data).decode('ascii')
            
            response = httpx.post(
                f"{agent_url}/files/write",
                json={
                    "path": "/tmp/test.bin",
                    "content": content_b64,
                    "mode": "0644",
                    "encoding": "base64"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.log_working("Binary files", "Base64 encoding supported")
                print("✅ Binary file write (base64) working\n")
            else:
                self.log_issue("high", "missing_feature",
                    "Binary file support missing",
                    f"Base64 encoding not supported: {response.status_code}",
                    "/files/write")
                print(f"⚠️  Binary files (base64) not supported: {response.status_code}\n")
                
        except Exception as e:
            self.log_issue("high", "missing_feature",
                "Binary file exception",
                str(e),
                "/files/write")
            print(f"❌ Binary file exception: {e}\n")
    
    def test_error_messages(self, sandbox):
        """Test error message quality."""
        print("1️⃣2️⃣  Testing error messages...")
        try:
            import httpx
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Test 1: Non-existent file
            response = httpx.get(
                f"{agent_url}/files/read",
                params={"path": "/nonexistent/file.txt"},
                timeout=10
            )
            
            if response.status_code in (403, 404):
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error") or error_data.get("message")
                    
                    if error_msg and len(error_msg) > 5:
                        self.log_working("Error messages", f"Clear error: {error_msg[:50]}")
                        print(f"✅ Error messages clear")
                        print(f"   Example: {error_msg[:80]}\n")
                    else:
                        self.log_issue("medium", "dx_issue",
                            "Error messages unclear",
                            f"Got: '{error_msg}'",
                            "all endpoints")
                        print(f"⚠️  Error message unclear: '{error_msg}'\n")
                except:
                    self.log_issue("medium", "dx_issue",
                        "Error messages not JSON",
                        "Errors should return JSON with 'error' or 'message' field",
                        "all endpoints")
                    print("⚠️  Error not in JSON format\n")
            else:
                print(f"⚠️  Unexpected status: {response.status_code}\n")
                
        except Exception as e:
            print(f"⚠️  Error message test exception: {e}\n")
    
    def test_performance(self, sandbox):
        """Test performance."""
        print("1️⃣3️⃣  Testing performance...")
        try:
            import httpx
            import time
            agent_url = sandbox.get_info().public_host.rstrip('/')
            
            # Test response time
            start = time.time()
            response = httpx.get(f"{agent_url}/health", timeout=10)
            elapsed = time.time() - start
            
            if elapsed < 0.5:
                self.log_working("Performance", f"Health endpoint: {elapsed*1000:.0f}ms")
                print(f"✅ Performance good ({elapsed*1000:.0f}ms)\n")
            elif elapsed < 2:
                self.log_warning("Performance OK",
                    f"Health endpoint: {elapsed*1000:.0f}ms (could be faster)")
                print(f"⚠️  Performance OK ({elapsed*1000:.0f}ms)\n")
            else:
                self.log_issue("medium", "performance",
                    "Slow response times",
                    f"Health endpoint took {elapsed*1000:.0f}ms",
                    "/health")
                print(f"⚠️  Slow response ({elapsed*1000:.0f}ms)\n")
                
        except Exception as e:
            print(f"⚠️  Performance test exception: {e}\n")
    
    def generate_report(self):
        """Generate final report."""
        print("\n" + "=" * 70)
        print("📊 TEST REPORT")
        print("=" * 70)
        print()
        
        print(f"✅ Working: {len(self.working)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Issues: {len(self.issues)}")
        print()
        
        if self.working:
            print("✅ WORKING FEATURES:")
            for item in self.working:
                print(f"   • {item['title']}: {item['details']}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"   • {item['title']}: {item['details']}")
            print()
        
        if self.issues:
            print("❌ ISSUES FOUND:")
            # Group by severity
            critical = [i for i in self.issues if i['severity'] == 'critical']
            high = [i for i in self.issues if i['severity'] == 'high']
            medium = [i for i in self.issues if i['severity'] == 'medium']
            low = [i for i in self.issues if i['severity'] == 'low']
            
            for severity, issues in [('CRITICAL', critical), ('HIGH', high), ('MEDIUM', medium), ('LOW', low)]:
                if issues:
                    print(f"\n   {severity} ({len(issues)}):")
                    for issue in issues:
                        print(f"   • [{issue['category']}] {issue['title']}")
                        print(f"     {issue['description']}")
                        if issue['endpoint']:
                            print(f"     Endpoint: {issue['endpoint']}")
        
        print("\n" + "=" * 70)
        print(f"Total: {len(self.working)} working, {len(self.warnings)} warnings, {len(self.issues)} issues")
        print("=" * 70)
        
        return {
            "working": self.working,
            "warnings": self.warnings,
            "issues": self.issues
        }


def main():
    api_key = os.getenv("BUNNYSHELL_API_KEY")
    if not api_key:
        print("❌ BUNNYSHELL_API_KEY not set!")
        return False
    
    print("Creating sandbox for testing...\n")
    sandbox = Sandbox.create(template="code-interpreter")
    print(f"✅ Sandbox created: {sandbox.sandbox_id}")
    print(f"   Agent URL: {sandbox.get_info().public_host}\n")
    
    try:
        tester = AgentTester()
        tester.test_all(sandbox)
        report = tester.generate_report()
        
        # Save report
        with open('agent_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print("\n📄 Full report saved to: agent_test_report.json")
        
        return len(tester.issues) == 0
        
    finally:
        print("\n🧹 Cleaning up...")
        sandbox.kill()
        print("✅ Sandbox destroyed")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

