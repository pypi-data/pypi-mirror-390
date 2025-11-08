# Troubleshooting Guide

This guide helps you resolve common issues when installing and using LionAGI QE Fleet.

---

## Installation Issues

### Issue: externally-managed-environment Error

**Error Message**:
```
error: externally-managed-environment
× This environment is externally managed
```

**Cause**: Modern Python installations protect the system Python from modifications.

**Solution**: Always use a virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On Linux/macOS:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Now install
pip install -e .
```

---

### Issue: LionAGI Not Found

**Error Message**:
```
ERROR: Could not find a version that satisfies the requirement lionagi>=0.18.2
```

**Cause**: LionAGI 0.18.2 is available on PyPI. This usually means network issues or pip cache problems.

**Solutions**:

1. **Update pip**:
```bash
pip install --upgrade pip
```

2. **Clear pip cache**:
```bash
pip cache purge
pip install lionagi>=0.18.2
```

3. **Use specific index**:
```bash
pip install lionagi>=0.18.2 --index-url https://pypi.org/simple
```

4. **Install from source** (if needed):
```bash
pip install git+https://github.com/lion-agi/lionagi.git
```

---

### Issue: python-dotenv Not Found

**Error Message**:
```
ModuleNotFoundError: No module named 'dotenv'
```

**Cause**: python-dotenv is in the dependencies but not installed.

**Solution**:
```bash
pip install python-dotenv
```

Or reinstall the package:
```bash
pip install -e .[dev]
```

---

### Issue: Import Errors

**Error Message**:
```
ImportError: cannot import name 'QEFleet' from 'lionagi_qe'
```

**Cause**: Package not installed or installed incorrectly.

**Solutions**:

1. **Reinstall in editable mode**:
```bash
pip uninstall lionagi-qe-fleet
pip install -e .
```

2. **Check installation**:
```bash
pip list | grep lionagi
```

Should show both `lionagi` and `lionagi-qe-fleet`.

3. **Verify Python path**:
```python
import sys
print(sys.path)
```

Make sure your project directory is in the path.

---

## Runtime Issues

### Issue: API Key Not Found

**Error Message**:
```
ValueError: OPENAI_API_KEY environment variable not set
```

**Solution**:

1. **Create .env file**:
```bash
# In project root
echo "OPENAI_API_KEY=your-key-here" > .env
```

2. **Set environment variable**:
```bash
# Linux/macOS
export OPENAI_API_KEY=your-key-here

# Windows
set OPENAI_API_KEY=your-key-here
```

3. **Load in code**:
```python
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing lionagi
```

---

### Issue: Agent Not Found

**Error Message**:
```
KeyError: 'test-generator'
```

**Cause**: Agent not registered with fleet.

**Solution**:
```python
from lionagi_qe import QEFleet
from lionagi_qe.agents import TestGeneratorAgent

# Initialize fleet
fleet = QEFleet()
await fleet.initialize()

# Register agent BEFORE using
test_gen = TestGeneratorAgent(agent_id="test-generator")
fleet.register_agent(test_gen)

# Now you can use it
result = await fleet.execute("test-generator", task)
```

---

### Issue: Tests Not Running

**Error Message**:
```
ModuleNotFoundError: No module named 'lionagi'
```

**Cause**: LionAGI not installed in test environment.

**Solution**:
```bash
# Install all dependencies including test requirements
pip install -e .[dev]

# Run tests
pytest tests/ -v
```

---

## Platform-Specific Issues

### macOS

**Issue: SSL Certificate Error**

**Solution**:
```bash
/Applications/Python\ 3.*/Install\ Certificates.command
```

**Issue: Permission Denied**

**Solution**:
```bash
sudo chown -R $(whoami) /path/to/project
```

---

### Windows

**Issue: Long Path Names**

**Solution**: Enable long paths in Windows:
```
reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
```

**Issue: PowerShell Execution Policy**

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### Linux

**Issue: Python 3.10+ Not Available**

**Solution**:
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv

# Or use pyenv
curl https://pyenv.run | bash
pyenv install 3.11
pyenv local 3.11
```

---

## Performance Issues

### Issue: Slow Test Generation

**Possible Causes**:
1. Using expensive model (GPT-4, Claude Opus)
2. No rate limiting
3. Sequential execution instead of parallel

**Solutions**:

1. **Enable multi-model routing**:
```python
fleet = QEFleet(enable_routing=True)
# Automatically uses cheaper models for simple tasks
```

2. **Use parallel execution**:
```python
# Instead of sequential
results = await fleet.execute_parallel(
    agents=["test-gen-1", "test-gen-2", "test-gen-3"],
    tasks=[task1, task2, task3]
)
```

3. **Enable caching** (if LionAGI supports it):
```python
fleet = QEFleet(enable_caching=True)
```

---

## Testing Issues

### Issue: Tests Fail with "LionAGI Not Found"

**Cause**: Tests run in isolated environment without dependencies.

**Solution**: Install test requirements:
```bash
pip install -e .[dev]
pytest tests/ -v
```

---

### Issue: Coverage Not Generated

**Cause**: pytest-cov not installed or misconfigured.

**Solution**:
```bash
pip install pytest-cov
pytest --cov=src/lionagi_qe --cov-report=html
```

View coverage:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov\index.html  # Windows
```

---

## Getting Help

If your issue isn't covered here:

1. **Check Examples**: See `examples/` directory for working code
2. **Read Documentation**: Full docs at `docs/index.md`
3. **Search Issues**: https://github.com/lionagi/lionagi-qe-fleet/issues
4. **Ask Question**: https://github.com/lionagi/lionagi-qe-fleet/discussions
5. **Report Bug**: Use bug report template

---

## Verification Checklist

Before reporting an issue, verify:

- [ ] Using Python 3.10 or higher
- [ ] In a virtual environment
- [ ] All dependencies installed (`pip install -e .[dev]`)
- [ ] Environment variables set (API keys)
- [ ] Latest version of lionagi-qe-fleet
- [ ] Tried solutions in this guide

---

## Quick Diagnostic

Run this diagnostic script:

```python
import sys
print(f"Python: {sys.version}")

try:
    import lionagi
    print(f"✅ LionAGI: {lionagi.__version__}")
except ImportError:
    print("❌ LionAGI not installed")

try:
    import lionagi_qe
    print("✅ lionagi-qe-fleet installed")
except ImportError:
    print("❌ lionagi-qe-fleet not installed")

try:
    import dotenv
    print("✅ python-dotenv installed")
except ImportError:
    print("❌ python-dotenv not installed")

import os
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"✅ OPENAI_API_KEY set ({api_key[:8]}...)")
else:
    print("❌ OPENAI_API_KEY not set")
```

Save as `diagnostic.py` and run: `python diagnostic.py`

---

**Last Updated**: 2025-11-05
**Version**: 1.0.0
