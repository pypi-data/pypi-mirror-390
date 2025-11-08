# Quick Start Guide

Get up and running with the LionAGI QE Fleet in under 10 minutes.

## What You'll Learn

1. [Installation](installation.md) - Install and configure the QE Fleet
2. [Your First Agent](your-first-agent.md) - Create and execute your first QE agent
3. [Basic Workflows](basic-workflows.md) - Common patterns for agent coordination

## Prerequisites

Before starting, ensure you have:
- Python 3.10 or higher
- pip or uv package manager
- API key for OpenAI (required) or Anthropic (optional)

## Quick Installation

```bash
pip install lionagi-qe-fleet
```

Set up your API keys:
```bash
export OPENAI_API_KEY=your-key-here
```

## Verify Installation

```python
import lionagi
from lionagi_qe import QEFleet

print(f"LionAGI version: {lionagi.__version__}")
print("QE Fleet installed successfully!")
```

## 5-Minute Example

Generate tests with a single agent:

```python
import asyncio
from lionagi import iModel
from lionagi_qe import QEFleet, QETask
from lionagi_qe.agents import TestGeneratorAgent

async def main():
    # Initialize fleet
    fleet = QEFleet(enable_routing=True)
    await fleet.initialize()

    # Create agent
    model = iModel(provider="openai", model="gpt-4o-mini")
    agent = TestGeneratorAgent(
        agent_id="test-gen",
        model=model,
        memory=fleet.memory
    )
    fleet.register_agent(agent)

    # Generate tests
    task = QETask(
        task_type="generate_tests",
        context={
            "code": "def add(a: int, b: int) -> int:\n    return a + b",
            "framework": "pytest"
        }
    )

    result = await fleet.execute("test-gen", task)
    print(f"Generated test:\n{result.test_code}")

asyncio.run(main())
```

## Next Steps

Ready to dive deeper? Choose your path:

### For Beginners
1. [Installation](installation.md) - Detailed setup instructions
2. [Your First Agent](your-first-agent.md) - Step-by-step walkthrough
3. [Basic Workflows](basic-workflows.md) - Common patterns

### For Advanced Users
- [Agent Catalog](../agents/index.md) - Explore all 18 agents
- [Workflow Patterns](../patterns/index.md) - Advanced coordination patterns
- [System Architecture](../architecture/system-overview.md) - Technical deep dive

### For Teams
- [Migration Guide](../guides/migration.md) - Migrate from other frameworks
- [Cost Optimization](../guides/cost-optimization.md) - Save 70-81% on AI costs
- [Observability](../guides/observability.md) - Monitor fleet operations

## Getting Help

- Check [Troubleshooting](installation.md#troubleshooting) for common issues
- Read [System Overview](../architecture/system-overview.md) for architecture details
- Open an issue on [GitHub](https://github.com/lion-agi/lionagi-qe-fleet)
- Join [LionAGI Discord](https://discord.gg/lionagi) for community support

---

**Next**: [Installation](installation.md) - Set up your environment →
