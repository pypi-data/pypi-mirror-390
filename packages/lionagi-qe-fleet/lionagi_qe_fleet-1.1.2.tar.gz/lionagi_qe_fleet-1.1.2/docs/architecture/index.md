# Architecture

Technical architecture documentation for the LionAGI QE Fleet.

## Overview

The LionAGI QE Fleet is built on a layered architecture that enables observable, scalable, and intelligent quality engineering workflows.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│              User Interface Layer                        │
│  CLI, Python API, Claude Code Integration, MCP Tools    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│            Orchestration Layer (QEFleet)                 │
│  - Workflow patterns (sequential, parallel, fan-out)    │
│  - Agent coordination and lifecycle management          │
│  - Multi-model routing (up to 80% theoretical cost savings)            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Agent Layer (18 Specialized Agents)         │
│  Core Testing | Performance & Security | Strategic      │
│  Advanced Testing | Specialized Agents                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│             Foundation Layer (LionAGI Core)              │
│  - Branch (conversation contexts)                       │
│  - iModel (multi-provider AI models)                    │
│  - Session (state management)                           │
│  - alcall (parallel operations)                         │
│  - ReAct reasoning                                      │
└─────────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

### 1. Observable Workflows Over Black Boxes

**Decision**: Explicit workflow orchestration instead of agent-to-agent conversations

**Rationale**:
- Transparency: Every step is visible and logged
- Debugging: Easy to identify failures
- Reproducibility: Workflows are deterministic
- Control: Users define the workflow, not agents

**Trade-off**: More setup code vs. autonomous agent conversations

---

### 2. Specialized Agents Over General Purpose

**Decision**: 18 specialized agents with focused expertise

**Rationale**:
- Expertise: Each agent masters a specific domain
- Composability: Mix and match agents for workflows
- Cost optimization: Right model for right task
- Scalability: Add new agents without affecting existing ones

**Trade-off**: More agents to learn vs. simpler single-agent model

---

### 3. Shared Memory Over Message Passing

**Decision**: Agents coordinate through shared memory namespace (`aqe/*`)

**Rationale**:
- Simplicity: No complex messaging protocols
- Performance: Direct memory access is fast
- Flexibility: Agents can retrieve any shared data
- Debugging: Easy to inspect memory state

**Trade-off**: Requires namespace conventions vs. type-safe messages

---

### 4. Sublinear Algorithms Over Linear Growth

**Decision**: O(log n) coverage analysis instead of O(n) test growth

**Rationale**:
- Scalability: Maintain coverage as codebase grows
- Efficiency: Fewer tests = faster CI/CD
- Intelligence: Focus on high-value tests
- Sustainability: Prevent test suite explosion

**Trade-off**: Complexity in implementation vs. simpler exhaustive testing

---

### 5. Multi-Model Routing Over Single Model

**Decision**: Intelligent model selection based on task complexity

**Rationale**:
- Cost: up to 80% theoretical savings by using cheaper models for simple tasks
- Quality: Use powerful models only when needed
- Flexibility: Add new models without code changes
- Optimization: Automatic selection removes manual decision

**Trade-off**: Routing overhead vs. always using one model

---

## Core Components

### QEFleet - Orchestrator

**Responsibilities**:
- Agent registration and lifecycle management
- Workflow execution (sequential, parallel, fan-out)
- Memory namespace management
- Cost tracking and optimization

**Key APIs**:
```python
await fleet.initialize()
fleet.register_agent(agent)
await fleet.execute(agent_id, task)
await fleet.execute_pipeline(pipeline, context)
await fleet.execute_parallel(agents, tasks)
```

---

### BaseQEAgent - Agent Foundation

**Responsibilities**:
- Define agent expertise (system prompt)
- Execute agent-specific tasks
- Coordinate via shared memory
- Track metrics and costs

**Key APIs**:
```python
def get_system_prompt() -> str
async def execute(task: dict) -> Any
async def store_result(key, value)
async def retrieve_context(key) -> Any
```

---

### QEMemory - Shared Context

**Responsibilities**:
- Store and retrieve agent results
- Namespace isolation (`aqe/*`)
- TTL-based expiration
- Pattern-based search

**Key APIs**:
```python
await memory.store(key, value, ttl)
await memory.retrieve(key)
await memory.search(pattern)
```

---

### ModelRouter - Cost Optimizer

**Responsibilities**:
- Analyze task complexity
- Select optimal model
- Track costs and savings
- Provide fallback chains

**Decision Tree**:
```
Task Complexity Analysis
    ↓
Simple (GPT-3.5) ← $0.0004
Moderate (GPT-4o-mini) ← $0.0008
Complex (GPT-4) ← $0.0048
Critical (Claude Sonnet) ← $0.0065
```

---

## Data Flow

### Sequential Pipeline Flow

```
User Request
    ↓
QEFleet.execute_pipeline(["agent1", "agent2", "agent3"])
    ↓
Agent 1 Execute
    ↓
Memory Store (aqe/agent1/results)
    ↓
Agent 2 Execute (retrieves aqe/agent1/results)
    ↓
Memory Store (aqe/agent2/results)
    ↓
Agent 3 Execute (retrieves aqe/agent2/results)
    ↓
Final Result
```

### Parallel Execution Flow

```
User Request
    ↓
QEFleet.execute_parallel([agent1, agent2, agent3], [task1, task2, task3])
    ↓
┌─────────────┬─────────────┬─────────────┐
│ Agent 1     │ Agent 2     │ Agent 3     │
│ Execute     │ Execute     │ Execute     │
│ task1       │ task2       │ task3       │
└─────────────┴─────────────┴─────────────┘
    ↓             ↓             ↓
Memory Store  Memory Store  Memory Store
    ↓
Collect Results [result1, result2, result3]
```

### Fan-Out/Fan-In Flow

```
User Request
    ↓
QEFleet.execute_fan_out_fan_in(coordinator, workers)
    ↓
Coordinator Agent (Fleet Commander)
    ↓
Decompose Request → [subtask1, subtask2, subtask3]
    ↓
Fan-Out: Assign to Workers
┌─────────────┬─────────────┬─────────────┐
│ Worker 1    │ Worker 2    │ Worker 3    │
│ Execute     │ Execute     │ Execute     │
│ subtask1    │ subtask2    │ subtask3    │
└─────────────┴─────────────┴─────────────┘
    ↓             ↓             ↓
Fan-In: Collect Worker Results
    ↓
Coordinator Synthesizes Results
    ↓
Final Synthesized Report
```

---

## Memory Namespace Structure

```
aqe/
├── test-plan/
│   ├── requirements          # Requirements documents
│   ├── generated-tests       # Generated test suites
│   └── execution-plan        # Test execution plans
├── coverage/
│   ├── current               # Current coverage data
│   ├── gaps                  # Identified gaps
│   └── targets               # Coverage targets
├── quality/
│   ├── metrics               # Quality metrics
│   ├── gates                 # Quality gate results
│   └── violations            # Policy violations
├── performance/
│   ├── benchmarks            # Performance benchmarks
│   ├── baselines             # Performance baselines
│   └── results               # Test results
├── security/
│   ├── scans                 # Security scan results
│   ├── vulnerabilities       # Found vulnerabilities
│   └── compliance            # Compliance status
├── patterns/
│   ├── test-patterns         # Learned test patterns
│   ├── bug-patterns          # Bug patterns
│   └── learned-patterns      # Q-learning patterns
└── swarm/
    └── coordination          # Multi-agent coordination
```

---

## Scalability Strategies

### Horizontal Scaling: Parallel Agents

```python
# Scale by adding more agents
agents = [f"test-gen-{i}" for i in range(10)]
tasks = [task for _ in range(10)]
results = await fleet.execute_parallel(agents, tasks)
```

### Vertical Scaling: Sublinear Algorithms

```python
# O(log n) coverage analysis instead of O(n) test growth
coverage = CoverageAnalyzerAgent(
    algorithm="johnson-lindenstrauss",  # Dimension reduction
    complexity="O(log n)"
)
```

### Cost Scaling: Intelligent Routing

```python
# Use cheaper models for simple tasks
fleet = QEFleet(enable_routing=True)  # up to 80% theoretical cost savings
```

---

## Security Architecture

### API Key Management

- Environment variables for secrets
- No hardcoded credentials
- Optional secrets management integration

### Memory Isolation

- Namespace-based isolation (`aqe/{agent_id}/`)
- TTL-based automatic cleanup
- No cross-agent memory leakage

### Audit Logging

- All operations logged
- Agent execution trails
- Cost tracking
- Error logging

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Single agent execution | O(1) | O(1) |
| Sequential pipeline (n agents) | O(n) | O(n) |
| Parallel execution (n agents) | O(1) amortized | O(n) |
| Coverage analysis | O(log n) | O(log n) |
| Memory store/retrieve | O(1) | O(n) |
| Pattern search | O(n) | O(1) |

---

## Integration Points

### LionAGI Core

- `Branch` for agent conversations
- `iModel` for multi-provider AI
- `Session` for state management
- `alcall` for parallel operations
- `ReAct` for advanced reasoning

### External Systems

- **CI/CD**: GitHub Actions, GitLab CI, Jenkins
- **Testing Frameworks**: pytest, Jest, Mocha, Cypress
- **Monitoring**: Prometheus, Grafana, Datadog
- **Logging**: ELK stack, Splunk, CloudWatch

---

## Design Patterns Used

### 1. Strategy Pattern
Different agents = different strategies for QE tasks

### 2. Observer Pattern
Lifecycle hooks for agent events

### 3. Factory Pattern
Agent creation and registration

### 4. Command Pattern
Tasks as commands for agents

### 5. Coordinator Pattern
Fleet Commander orchestrates workers

---

## Technology Stack

### Core
- **Python 3.10+**: Modern async/await
- **LionAGI**: Orchestration framework
- **Pydantic**: Type validation
- **aiohttp**: Async HTTP

### AI Models
- **OpenAI**: GPT-3.5, GPT-4, GPT-4o
- **Anthropic**: Claude 3.5 Sonnet
- **Local**: Ollama support

### Testing
- **pytest**: Python testing
- **hypothesis**: Property-based testing
- **coverage.py**: Coverage analysis

---

## Next Steps

**Understand the system**: [System Overview](system-overview.md)

**Learn workflows**: [Workflow Patterns](../patterns/index.md)

**Explore agents**: [Agent Catalog](../agents/index.md)

**API details**: [API Reference](../reference/index.md)

---

**See Also**: [Design Decisions](design-decisions.md) | [Performance Optimization](../guides/cost-optimization.md)
