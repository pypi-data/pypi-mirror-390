---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Describe the Bug

A clear and concise description of what the bug is.

## To Reproduce

Steps to reproduce the behavior:

1. Initialize fleet with '...'
2. Execute agent '...'
3. Call function '...'
4. See error

## Expected Behavior

A clear and concise description of what you expected to happen.

## Actual Behavior

A clear and concise description of what actually happened.

## Code Sample

If applicable, provide a minimal code sample that reproduces the issue:

```python
from lionagi_qe.agents import TestGenerator

# Your code here
generator = TestGenerator()
result = generator.generate(...)
```

## Error Messages

If applicable, paste the full error message and stack trace:

```
Traceback (most recent call last):
  ...
```

## Environment

Please complete the following information:

- **OS**: [e.g., Ubuntu 22.04, macOS 14.0, Windows 11]
- **Python Version**: [e.g., 3.10.5, 3.11.2]
- **lionagi-qe-fleet Version**: [e.g., 1.0.0]
- **LionAGI Version**: [e.g., 0.18.2]
- **Installation Method**: [e.g., pip, uv, from source]

## Additional Context

Add any other context about the problem here:

- Related issues or pull requests
- Workarounds you've tried
- Screenshots or logs
- Configuration files (sanitized)

## Possible Solution

If you have an idea of what might be causing the issue or how to fix it, please share.

## Checklist

- [ ] I have searched existing issues to ensure this is not a duplicate
- [ ] I have provided all requested information
- [ ] I have included a minimal reproducible example
- [ ] I have checked the documentation
