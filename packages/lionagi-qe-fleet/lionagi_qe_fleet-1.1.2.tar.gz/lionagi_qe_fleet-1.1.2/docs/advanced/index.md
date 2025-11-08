# Advanced Topics

Deep dives into advanced features and integrations of the LionAGI QE Fleet.

## Available Topics

### Integrations
- [alcall Integration](alcall-integration.md) - Parallel operations with LionAGI's alcall
- [ReAct Reasoning](react-reasoning.md) - Advanced reasoning for intelligent agents
- [MCP Integration](mcp-integration.md) - Model Context Protocol integration
- [Claude Code Integration](claude-code-integration.md) - Workspace-aware development

### Systems
- [Hooks System](hooks-system.md) - AQE hooks for agent coordination
- [Streaming Progress](streaming-progress.md) - Real-time progress updates

### Migration & Features
- [Advanced Features Migration](../guides/advanced-features-migration.md) - Migrating advanced features

## Quick Links

| Topic | Description | When to Read |
|-------|-------------|--------------|
| [alcall Integration](alcall-integration.md) | Parallel operations | Building parallel workflows |
| [ReAct Reasoning](react-reasoning.md) | Advanced AI reasoning | Improving agent intelligence |
| [Hooks System](hooks-system.md) | Agent lifecycle hooks | Customizing agent behavior |
| [MCP Integration](mcp-integration.md) | External tool integration | Integrating with other tools |
| [Streaming Progress](streaming-progress.md) | Real-time updates | Long-running operations |

## Integration Summaries

### alcall: Parallel Operations

LionAGI's `alcall` enables efficient parallel execution of agents:

```python
from lionagi.ln import alcall

results = await alcall(
    items=["item1", "item2", "item3"],
    func=lambda x: process_item(x),
    max_concurrent=10
)
```

**Benefits**:
- 10x-100x faster than sequential
- Automatic concurrency management
- Error handling and retries

**Details**: [alcall Integration](alcall-integration.md)

---

### ReAct: Advanced Reasoning

ReAct (Reasoning + Acting) enables agents to:
- Think step-by-step
- Use tools dynamically
- Adapt strategies based on results

```python
from lionagi import ReActAgent

agent = ReActAgent(
    system="You are a test generation expert",
    tools=[code_analyzer, pattern_matcher],
    model=iModel(provider="openai", model="gpt-4")
)

result = await agent.chat("Generate tests with edge case analysis")
```

**Details**: [ReAct Reasoning](react-reasoning.md)

---

### Hooks: Agent Lifecycle

AQE hooks enable coordination through agent lifecycle events:

```python
class CustomAgent(BaseQEAgent):
    async def on_pre_task(self, data):
        # Load context before task
        context = await self.memory.retrieve('aqe/context')

    async def on_post_task(self, data):
        # Store results after task
        await self.memory.store('aqe/results', data.result)
```

**Benefits**:
- Zero external dependencies
- 100-500x faster than shell hooks
- Type-safe Python API

**Details**: [Hooks System](hooks-system.md)

---

### MCP: External Tools

Model Context Protocol enables agents to use external tools:

```python
# Agents can access file system, run commands, query databases
agent = TestGeneratorAgent(
    agent_id="test-gen",
    model=model,
    memory=fleet.memory,
    mcp_tools=["filesystem", "terminal", "database"]
)
```

**Details**: [MCP Integration](mcp-integration.md)

---

### Streaming: Real-time Progress

Stream progress for long-running operations:

```python
async for event in fleet.execute_stream("test-executor", task):
    if event.type == "progress":
        print(f"Progress: {event.percent}% - {event.message}")
    elif event.type == "result":
        print(f"Complete: {event.data}")
```

**Benefits**:
- Real-time visibility
- Better UX for long operations
- Progress tracking

**Details**: [Streaming Progress](streaming-progress.md)

## Architecture Deep Dives

### Memory Namespace (`aqe/*`)

Agents coordinate through shared memory:

```
aqe/
├── test-plan/          # Test planning and requirements
├── coverage/           # Coverage analysis and gaps
├── quality/            # Quality metrics and gates
├── performance/        # Performance test results
├── security/           # Security scan findings
└── swarm/coordination  # Cross-agent coordination
```

**Usage**:
```python
# Store
await fleet.memory.store("aqe/test-plan/requirements", requirements)

# Retrieve
requirements = await fleet.memory.retrieve("aqe/test-plan/requirements")

# Search
patterns = await fleet.memory.search(r"aqe/patterns/.*")
```

### Multi-Model Routing

Intelligent model selection for cost optimization:

```python
# Routing configuration
{
    "simple": "gpt-3.5-turbo",      # $0.0004
    "moderate": "gpt-4o-mini",      # $0.0008
    "complex": "gpt-4",             # $0.0048
    "critical": "claude-3-5-sonnet" # $0.0065
}
```

**How it works**:
1. Analyze task complexity
2. Select optimal model
3. Track costs and savings
4. Fallback on errors

**Result**: up to 80% theoretical cost savings

### Q-Learning Integration

Agents learn from experience:

```python
fleet = QEFleet(enable_learning=True)

# Agents automatically:
# - Track successful patterns
# - Learn from failures
# - Improve over time
```

## Performance Optimization

### Parallelization

```python
# Sequential: 30 seconds
for agent in agents:
    await fleet.execute(agent, task)

# Parallel: 10 seconds
await fleet.execute_parallel(agents, tasks)
```

### Caching

```python
# Cache expensive operations
await fleet.memory.store("aqe/cache/analysis", result, ttl=3600)

# Retrieve cached result
cached = await fleet.memory.retrieve("aqe/cache/analysis")
```

### Batching

```python
# Batch similar tasks
tasks = [task1, task2, task3, ...]
results = await fleet.execute_batch("test-generator", tasks, batch_size=10)
```

## Security Considerations

### API Key Management

```python
# ✅ Good: Environment variables
os.environ["OPENAI_API_KEY"] = get_secret("openai-key")

# ❌ Bad: Hardcoded
model = iModel(api_key="sk-hardcoded...")
```

### Memory Isolation

```python
# Use namespaces to isolate agent data
await fleet.memory.store(f"aqe/{agent_id}/private", data)
```

### Audit Logging

```python
# Enable audit logging
fleet = QEFleet(enable_audit_log=True)

# All operations logged to .agentic-qe/logs/audit.log
```

## Troubleshooting

### Issue: Slow Parallel Execution

**Cause**: Hitting rate limits
**Solution**: Adjust concurrency
```python
fleet = QEFleet(max_concurrent=5)  # Reduce from default 10
```

### Issue: High Memory Usage

**Cause**: Too many concurrent agents
**Solution**: Use streaming or batching
```python
# Stream results instead of collecting all
async for result in fleet.execute_stream(agent, task):
    process(result)
```

### Issue: Cost Overruns

**Cause**: Routing disabled or misconfigured
**Solution**: Enable and monitor routing
```python
fleet = QEFleet(enable_routing=True)
status = await fleet.get_status()
print(f"Savings: {status['routing_stats']['savings_percentage']:.1f}%")
```

## Next Steps

Choose your learning path:

**For Integration**:
- [alcall Integration](alcall-integration.md)
- [MCP Integration](mcp-integration.md)
- [Claude Code Integration](claude-code-integration.md)

**For Customization**:
- [Hooks System](hooks-system.md)
- [Streaming Progress](streaming-progress.md)

**For Architecture**:
- [System Overview](../architecture/system-overview.md)
- [Agent Catalog](../agents/index.md)

---

**See Also**: [Workflow Patterns](../patterns/index.md) | [API Reference](../reference/index.md)
