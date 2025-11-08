# API Reference

Complete API reference for the LionAGI QE Fleet.

## Core APIs

### QEFleet

Main fleet orchestrator managing agents and workflows.

**Import**:
```python
from lionagi_qe import QEFleet
```

**Constructor**:
```python
QEFleet(
    enable_routing: bool = False,
    enable_learning: bool = False,
    max_concurrent: int = 10,
    enable_audit_log: bool = False
)
```

**Methods**:

#### `async initialize()`
Initialize the fleet and memory system.

```python
fleet = QEFleet()
await fleet.initialize()
```

#### `register_agent(agent: BaseQEAgent)`
Register an agent with the fleet.

```python
fleet.register_agent(test_gen)
```

#### `async execute(agent_id: str, task: QETask) -> Any`
Execute a single agent.

```python
result = await fleet.execute("test-generator", task)
```

#### `async execute_pipeline(pipeline: list[str], context: dict) -> dict`
Execute sequential pipeline.

```python
result = await fleet.execute_pipeline(
    pipeline=["test-generator", "test-executor"],
    context={"code": code}
)
```

#### `async execute_parallel(agent_ids: list[str], tasks: list[dict]) -> list`
Execute agents in parallel.

```python
results = await fleet.execute_parallel(
    agent_ids=["agent1", "agent2"],
    tasks=[task1, task2]
)
```

#### `async execute_fan_out_fan_in(coordinator: str, workers: list[str], context: dict) -> dict`
Execute fan-out/fan-in pattern.

```python
result = await fleet.execute_fan_out_fan_in(
    coordinator="fleet-commander",
    workers=["agent1", "agent2"],
    context={"request": "..."}
)
```

#### `async get_status() -> dict`
Get fleet status and metrics.

```python
status = await fleet.get_status()
```

**Properties**:
- `memory: QEMemory` - Shared memory namespace
- `agents: dict[str, BaseQEAgent]` - Registered agents

---

### BaseQEAgent

Base class for all QE agents.

**Import**:
```python
from lionagi_qe.agents import BaseQEAgent
```

**Constructor**:
```python
BaseQEAgent(
    agent_id: str,
    model: iModel,
    memory: QEMemory,
    skills: list[str] = None
)
```

**Abstract Methods** (must implement):

#### `get_system_prompt() -> str`
Define agent's expertise and behavior.

```python
def get_system_prompt(self) -> str:
    return "You are an expert test generation agent..."
```

#### `async execute(task: dict) -> Any`
Execute agent's primary function.

```python
async def execute(self, task: dict) -> GeneratedTest:
    # Agent logic here
    return result
```

**Provided Methods**:

#### `async store_result(key: str, value: Any)`
Store results in shared memory.

```python
await self.store_result("last_generated", result)
```

#### `async retrieve_context(key: str) -> Any`
Retrieve context from shared memory.

```python
context = await self.retrieve_context("aqe/shared/data")
```

#### `async get_metrics() -> dict`
Get agent metrics.

```python
metrics = await agent.get_metrics()
```

**Lifecycle Hooks** (optional override):

#### `async on_pre_task(data: dict)`
Called before task execution.

```python
async def on_pre_task(self, data):
    await self.load_context()
```

#### `async on_post_task(data: dict)`
Called after successful task execution.

```python
async def on_post_task(self, data):
    await self.store_result("output", data.result)
```

#### `async on_task_error(data: dict)`
Called on task failure.

```python
async def on_task_error(self, data):
    await self.log_error(data.error)
```

---

### QETask

Task definition for agents.

**Import**:
```python
from lionagi_qe import QETask
```

**Constructor**:
```python
QETask(
    task_type: str,
    context: dict,
    metadata: dict = None
)
```

**Example**:
```python
task = QETask(
    task_type="generate_tests",
    context={
        "code": source_code,
        "framework": "pytest"
    },
    metadata={"priority": "high"}
)
```

---

### QEMemory

Shared memory namespace for agent coordination.

**Import**:
```python
from lionagi_qe.core import QEMemory
```

**Methods**:

#### `async store(key: str, value: Any, ttl: int = None)`
Store value in memory.

```python
await memory.store("aqe/results", data, ttl=3600)
```

#### `async retrieve(key: str) -> Any`
Retrieve value from memory.

```python
data = await memory.retrieve("aqe/results")
```

#### `async search(pattern: str) -> dict`
Search memory by regex pattern.

```python
matches = await memory.search(r"aqe/patterns/.*")
```

#### `async delete(key: str)`
Delete key from memory.

```python
await memory.delete("aqe/temp/data")
```

#### `async clear(pattern: str = None)`
Clear memory (optionally by pattern).

```python
await memory.clear("aqe/temp/*")  # Clear temp namespace
await memory.clear()  # Clear all
```

---

## Agent APIs

### TestGeneratorAgent

Generate comprehensive test suites.

**Import**:
```python
from lionagi_qe.agents import TestGeneratorAgent
```

**Output**: `GeneratedTest`
```python
class GeneratedTest:
    test_name: str
    test_code: str
    framework: str
    assertions: list[str]
    edge_cases: list[str]
```

**Usage**:
```python
agent = TestGeneratorAgent(
    agent_id="test-gen",
    model=iModel(provider="openai", model="gpt-4o-mini"),
    memory=fleet.memory
)

result = await fleet.execute("test-gen", QETask(
    task_type="generate_tests",
    context={"code": code, "framework": "pytest"}
))
```

---

### TestExecutorAgent

Execute tests across frameworks.

**Import**:
```python
from lionagi_qe.agents import TestExecutorAgent
```

**Output**: `TestExecutionResult`
```python
class TestExecutionResult:
    total_tests: int
    passed: int
    failed: int
    skipped: int
    coverage_percent: float
    duration_seconds: float
```

---

### CoverageAnalyzerAgent

Analyze test coverage with sublinear algorithms.

**Import**:
```python
from lionagi_qe.agents import CoverageAnalyzerAgent
```

**Output**: `CoverageAnalysisResult`
```python
class CoverageAnalysisResult:
    coverage_percent: float
    gaps: list[CoverageGap]
    recommendations: list[str]
    critical_paths: list[str]
```

---

## Utility Functions

### `async alcall(items: list, func: callable, max_concurrent: int = 10)`

Parallel execution helper from LionAGI.

```python
from lionagi.ln import alcall

results = await alcall(
    items=[1, 2, 3, 4, 5],
    func=lambda x: process_item(x),
    max_concurrent=3
)
```

---

### `iModel(provider: str, model: str, **kwargs)`

Create AI model instance.

```python
from lionagi import iModel

model = iModel(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=2000
)
```

**Supported Providers**:
- `openai`: GPT-3.5, GPT-4, GPT-4o
- `anthropic`: Claude 3.5 Sonnet, Claude 3 Opus
- `ollama`: Local models

---

## Configuration

### Fleet Configuration

File: `.agentic-qe/config/fleet.json`

```json
{
  "topology": "hierarchical",
  "max_agents": 10,
  "testing_focus": ["unit", "integration"],
  "environments": ["development", "staging"],
  "frameworks": ["pytest", "jest"]
}
```

---

### Routing Configuration

File: `.agentic-qe/config/routing.json`

```json
{
  "multiModelRouter": {
    "enabled": true,
    "models": {
      "simple": "gpt-3.5-turbo",
      "moderate": "gpt-4o-mini",
      "complex": "gpt-4",
      "critical": "claude-3-5-sonnet-20241022"
    }
  }
}
```

---

## Type Definitions

### Common Types

```python
from typing import Literal, Optional

TaskType = Literal[
    "generate_tests",
    "execute_tests",
    "analyze_coverage",
    "security_scan",
    "performance_test"
]

Framework = Literal["pytest", "jest", "mocha", "cypress", "unittest"]

AgentStatus = Literal["idle", "running", "error", "completed"]
```

---

## Error Handling

### QEFleetError

Base exception for fleet errors.

```python
from lionagi_qe.exceptions import QEFleetError

try:
    result = await fleet.execute("agent-id", task)
except QEFleetError as e:
    print(f"Fleet error: {e}")
```

### AgentExecutionError

Agent execution failures.

```python
from lionagi_qe.exceptions import AgentExecutionError

try:
    result = await agent.execute(task)
except AgentExecutionError as e:
    print(f"Agent failed: {e}")
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `ENABLE_ROUTING` | Enable multi-model routing | `false` |
| `ENABLE_LEARNING` | Enable Q-learning | `false` |
| `AQE_LOG_LEVEL` | Logging level | `INFO` |

---

## Next Steps

- [Agent Catalog](../agents/index.md) - Explore all agents
- [Workflow Patterns](../patterns/index.md) - Common usage patterns
- [System Overview](../architecture/system-overview.md) - Architecture details

---

**See Also**: [Quick Start](../quickstart/index.md) | [Guides](../guides/index.md)
