# LionAGI QE Fleet

**Build trustworthy AI-powered quality engineering workflows with 18 specialized agents**

## The Problem

Traditional QE approaches struggle to scale. Manual testing is slow, automated testing misses edge cases, and quality feedback comes too late. Test suites grow linearly with codebase size, creating bottlenecks.

The LionAGI QE Fleet solves this with:
- **Intelligent agents** that generate, execute, and analyze tests
- **Sublinear algorithms** that scale coverage without linear test growth
- **Multi-agent coordination** for comprehensive quality assurance
- **Observable workflows** where every quality decision is transparent

## Installation

```bash
pip install lionagi-qe-fleet
```

Set your API keys:
```bash
# Required for OpenAI models
export OPENAI_API_KEY=your-key

# Optional for Anthropic models
export ANTHROPIC_API_KEY=your-key
```

## Your First QE Agent

Here's the simplest example - generating tests with AI:

```python
import asyncio
from lionagi import iModel
from lionagi_qe import QEFleet, QETask
from lionagi_qe.agents import TestGeneratorAgent

async def main():
    # Initialize fleet with intelligent routing
    fleet = QEFleet(enable_routing=True)
    await fleet.initialize()

    # Create test generator with GPT-4o-mini
    model = iModel(provider="openai", model="gpt-4o-mini")
    test_gen = TestGeneratorAgent(
        agent_id="test-generator",
        model=model,
        memory=fleet.memory
    )

    # Register agent with fleet
    fleet.register_agent(test_gen)

    # Create test generation task
    task = QETask(
        task_type="generate_tests",
        context={
            "code": """
def add(a: int, b: int) -> int:
    return a + b
""",
            "framework": "pytest"
        }
    )

    # Execute and get results
    result = await fleet.execute("test-generator", task)

    print(f"Generated Test:\n{result.test_code}")
    # See the generated test with edge cases and assertions

asyncio.run(main())
```

### Available Agents (19 Total)

**Core Testing**: test-generator, test-executor, coverage-analyzer, quality-gate, quality-analyzer, code-complexity
**Performance & Security**: performance-tester, security-scanner
**Strategic Planning**: requirements-validator, production-intelligence, fleet-commander
**Advanced Testing**: regression-risk-analyzer, test-data-architect, api-contract-validator, flaky-test-hunter
**Specialized**: deployment-readiness, visual-tester, chaos-engineer

## Why Observable QE Workflows Matter

- **Trust through transparency**: See every quality decision, not just pass/fail
- **Intelligent automation**: AI agents that learn patterns and catch edge cases
- **Sublinear scaling**: Maintain coverage without linear test growth
- **Cost optimization**: up to 80% theoretical savings through intelligent model routing
- **Multi-agent coordination**: Different specialists tackle different quality aspects

## When to Use LionAGI QE Fleet

✅ **Perfect for:**
- Teams needing comprehensive quality automation
- Projects requiring intelligent test generation
- Systems where quality feedback must be fast and accurate
- Organizations wanting observable QE workflows

❌ **Not for:**
- Simple projects with manual testing only
- Teams not ready to adopt AI-powered QE
- Prototypes without quality requirements

## Core Concepts Made Simple

**Agents = Quality Specialists**
Each agent focuses on specific QE tasks (generation, execution, analysis)

**Fleet = Orchestration**
The fleet coordinates agents and manages shared context

**Observable > Black Box**
Every quality decision is logged and explainable

**Sublinear > Linear**
Maintain coverage without proportional test growth

## Quick Patterns

### Sequential QE Pipeline
```python
# Generate → Execute → Analyze → Gate
result = await fleet.execute_pipeline(
    pipeline=["test-generator", "test-executor", "coverage-analyzer", "quality-gate"],
    context={"code": code, "framework": "pytest"}
)
```

### Parallel Quality Checks
```python
# Run multiple quality checks simultaneously
results = await fleet.execute_parallel(
    agents=["security-scanner", "performance-tester", "visual-tester"],
    tasks=[security_task, perf_task, visual_task]
)
```

### Hierarchical Coordination
```python
# Fleet commander coordinates multiple agents
result = await fleet.execute_fan_out_fan_in(
    coordinator="fleet-commander",
    workers=["test-gen", "security", "performance"],
    context={"request": "Comprehensive QA for UserService"}
)
```

## Learning Path

1. **Start Here** → [Installation](quickstart/installation.md)
2. **First Agent** → [Your First Agent](quickstart/your-first-agent.md)
3. **Understand Why** → [System Overview](architecture/system-overview.md)
4. **Explore Agents** → [Agent Catalog](agents/index.md)
5. **Learn Patterns** → [Workflow Patterns](patterns/index.md)
6. **Go Advanced** → [Advanced Topics](advanced/index.md)

## The Key Difference

```python
# ❌ Traditional QE: Manual or simplistic automation
write_tests_manually()
run_all_tests()  # Slow, linear growth
# Miss edge cases, late feedback

# ✅ LionAGI QE Fleet: Intelligent, observable, scalable
test_gen = await fleet.execute("test-generator", task)  # AI-powered
coverage = await fleet.execute("coverage-analyzer", test_gen)  # Sublinear
gate = await fleet.execute("quality-gate", coverage)  # Intelligent decisions
# Every step observable and optimized
```

## Key Features

### Multi-Model Routing (70-81% Cost Savings)
Simple tasks use GPT-3.5 ($0.0004), complex tasks use GPT-4 ($0.0048), critical tasks use Claude Sonnet 4.5 ($0.0065)

### Sublinear Coverage Analysis
Johnson-Lindenstrauss dimension reduction and spectral sparsification for O(log n) gap detection

### Agent Coordination
18 specialized agents share context through `aqe/*` memory namespace

### Streaming Progress
Real-time visibility into long-running operations

### Learning & Patterns
Q-learning integration for continuous improvement

## Quick Stats

- **18 specialized agents** for comprehensive QE
- **Parallel execution** with async-first architecture
- **Up to 80% theoretical cost savings** through intelligent routing
- **O(log n) coverage** analysis algorithms
- **34 QE skills** (Claude Code IDE features for development)

## Get Started

**Ready to build?** Start with [Installation](quickstart/installation.md) →

**Understand the architecture?** Read [System Overview](architecture/system-overview.md) →

**Explore agents?** Check [Agent Catalog](agents/index.md) →

**Need help?** [GitHub Issues](https://github.com/lion-agi/lionagi-qe-fleet) | [Main LionAGI Docs](https://khive-ai.github.io/lionagi/)

---

*LionAGI QE Fleet: Observable, intelligent, scalable quality engineering*

Apache 2.0 License
