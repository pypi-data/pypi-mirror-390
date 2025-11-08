# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

We take the security of LionAGI QE Fleet seriously. If you discover a security vulnerability, please follow these steps:

### 1. Do Not Publicly Disclose

**Do not** open a public GitHub issue for security vulnerabilities. This helps protect users who haven't yet updated.

### 2. Contact Us Privately

Email security concerns to: **security@agentic-qe.dev**

Please include:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Affected versions
- Suggested fix (if any)
- Your contact information for follow-up

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Updates**: Every 5 business days
- **Fix Timeline**: Critical issues within 7 days, others within 30 days
- **Public Disclosure**: After patch release and coordination with reporter

### 4. Recognition

Security researchers who responsibly disclose vulnerabilities will be:
- Credited in the CHANGELOG.md (unless anonymity is requested)
- Listed in our security acknowledgments
- Eligible for our bug bounty program (if applicable)

## Security Best Practices

When using LionAGI QE Fleet, follow these security guidelines:

### Input Validation

```python
# ✅ GOOD: Validate all external inputs
def execute_test(file_path: str):
    if not os.path.abspath(file_path).startswith(PROJECT_ROOT):
        raise ValueError("Invalid file path")
    # Safe to proceed
```

```python
# ❌ BAD: No validation
def execute_test(file_path: str):
    subprocess.run(f"pytest {file_path}", shell=True)  # VULNERABLE!
```

### Subprocess Execution

```python
# ✅ GOOD: Use list arguments, disable shell
subprocess.run(
    ["pytest", file_path, "-v"],
    shell=False,
    timeout=60
)
```

```python
# ❌ BAD: String concatenation with shell=True
subprocess.run(
    f"pytest {file_path} -v",
    shell=True  # Command injection risk!
)
```

### Serialization

```python
# ✅ GOOD: Use JSON for data serialization
import json
data = json.loads(input_data)
```

```python
# ❌ BAD: Never use pickle for untrusted data
import pickle
data = pickle.loads(input_data)  # Arbitrary code execution!
```

### Function Whitelisting

```python
# ✅ GOOD: Whitelist allowed functions
ALLOWED_FUNCTIONS = {"run_test", "analyze_coverage"}

async def execute_function(func_name: str, *args):
    if func_name not in ALLOWED_FUNCTIONS:
        raise ValueError(f"Function {func_name} not allowed")
    func = globals()[func_name]
    return await alcall(func, *args)
```

```python
# ❌ BAD: Unrestricted function access
async def execute_function(func_name: str, *args):
    func = globals()[func_name]  # Can execute ANY function!
    return await alcall(func, *args)
```

### File Operations

```python
# ✅ GOOD: Validate paths before operations
from pathlib import Path

def read_file(file_path: str):
    path = Path(file_path).resolve()
    if not path.is_relative_to(PROJECT_ROOT):
        raise ValueError("Path traversal detected")
    return path.read_text()
```

### API Rate Limiting

```python
# ✅ GOOD: Implement rate limiting
from lionagi_qe.core.hooks import enable_cost_alerts

enable_cost_alerts(
    cost_threshold=10.0,  # Alert if cost > $10/hour
    rate_limit=100  # Max 100 calls/minute
)
```

## Known Security Considerations

### Test Executor
- **Risk**: Executes arbitrary test commands
- **Mitigation**: Always validate test file paths, disable shell=True
- **Status**: Fixed in v1.0.0

### Code Analyzer
- **Risk**: Operates on filesystem
- **Mitigation**: Implement path validation, restrict to project directory
- **Status**: Path validation added in v1.0.0

### Hooks System
- **Risk**: Tracks sensitive cost/usage data
- **Mitigation**: Encrypt data at rest, restrict access to authorized users
- **Status**: Encryption recommended (not yet implemented)

### AI Model Integration
- **Risk**: Potential prompt injection attacks
- **Mitigation**: Sanitize inputs, validate outputs, implement rate limiting
- **Status**: Basic validation in place

## Security Fixes by Version

### Version 1.0.0 (2025-11-05)

#### Critical Fixes

1. **Command Injection (CVE-TBD, CVSS 9.8)**
   - **Component**: test_executor.py
   - **Issue**: shell=True allowed arbitrary command execution
   - **Fix**: Removed shell=True, switched to list-based arguments
   - **Affected Versions**: 0.1.x
   - **Fixed in**: 1.0.0

2. **Arbitrary Code Execution (CVE-TBD, CVSS 9.1)**
   - **Component**: alcall wrapper
   - **Issue**: Unrestricted function access via globals()
   - **Fix**: Added function whitelist validation
   - **Affected Versions**: 0.1.x
   - **Fixed in**: 1.0.0

3. **Insecure Deserialization (CVE-TBD, CVSS 8.8)**
   - **Component**: hooks.py
   - **Issue**: pickle.loads() on untrusted data
   - **Fix**: Replaced with JSON deserialization
   - **Affected Versions**: 0.1.x
   - **Fixed in**: 1.0.0

#### High Priority Fixes

4. **Path Traversal (CVE-TBD, CVSS 7.5)**
   - **Component**: code_analyzer.py
   - **Issue**: Missing path validation
   - **Fix**: Added path validation and sandboxing
   - **Affected Versions**: 0.1.x
   - **Fixed in**: 1.0.0

See [CHANGELOG.md](CHANGELOG.md) for complete release notes.

## Security Development Practices

### Code Review
- All code changes require security review
- Automated SAST scanning in CI/CD
- Dependency vulnerability scanning

### Testing
- Security-focused test cases
- Penetration testing for major releases
- Fuzzing for input validation

### Dependencies
- Regular dependency updates
- Automated vulnerability scanning
- Minimal dependency footprint

## Vulnerability Disclosure Timeline

1. **Day 0**: Vulnerability reported privately
2. **Day 2**: Initial acknowledgment sent
3. **Day 7**: Assessment complete, fix timeline established
4. **Day 14-30**: Patch developed and tested
5. **Day 30**: Patch released to supported versions
6. **Day 37**: Public disclosure (7 days after patch)

## Security Audit History

- **2025-11-05**: Internal security audit (qe-security-scanner agent)
  - 3 critical vulnerabilities found and fixed
  - 3 high-priority issues addressed
  - Security score improved from 68/100 to 95/100

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## Contact

- **Security Email**: security@lionagi-qe-fleet.example.com
- **General Issues**: [GitHub Issues](https://github.com/proffesor-for-testing/lionagi-qe-fleet/issues)
- **Documentation**: [Security Best Practices](docs/SECURITY_FIX_REPORT.md)

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
