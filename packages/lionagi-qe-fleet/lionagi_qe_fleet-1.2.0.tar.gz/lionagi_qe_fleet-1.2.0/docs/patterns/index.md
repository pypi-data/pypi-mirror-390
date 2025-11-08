# Workflow Patterns

Common patterns for coordinating QE agents effectively.

## Pattern Overview

| Pattern | Use Case | Agents | Execution Time |
|---------|----------|--------|----------------|
| [Sequential Pipeline](#sequential-pipeline) | Dependent tasks | 2-5 | Sum of agents |
| [Parallel Execution](#parallel-execution) | Independent tasks | 2-10 | Max of agents |
| [Fan-Out/Fan-In](#fan-outfan-in) | Complex coordination | 3-10+ | Max + synthesis |
| [Conditional Workflow](#conditional-workflow) | Dynamic routing | 2-5 | Conditional |

## Sequential Pipeline

Execute agents in order, passing results between them.

**When to Use**:
- Test generation → execution → coverage → gate
- Results from one agent feed the next
- Order matters

**Example**:
```python
pipeline = ["test-generator", "test-executor", "coverage-analyzer", "quality-gate"]
result = await fleet.execute_pipeline(pipeline, context)
```

**Details**: [Sequential Pipeline](sequential-pipeline.md)

---

## Parallel Execution

Execute multiple agents simultaneously for independent tasks.

**When to Use**:
- Unit + integration + E2E tests (all independent)
- Security + performance + visual checks
- Minimize total execution time

**Example**:
```python
agents = ["security-scanner", "performance-tester", "visual-tester"]
tasks = [security_task, perf_task, visual_task]
results = await fleet.execute_parallel(agents, tasks)
```

**Details**: [Parallel Execution](parallel-execution.md)

---

## Fan-Out/Fan-In

Coordinator decomposes work, distributes to workers, synthesizes results.

**When to Use**:
- Complex QA requests needing multiple perspectives
- Intelligent task decomposition required
- Want single synthesized report

**Example**:
```python
result = await fleet.execute_fan_out_fan_in(
    coordinator="fleet-commander",
    workers=["test-gen", "security", "performance"],
    context={"request": "Comprehensive QA for UserService"}
)
```

**Details**: [Fan-Out/Fan-In](fan-out-fan-in.md)

---

## Conditional Workflow

Route to different agents based on conditions.

**When to Use**:
- Different agents for different file types
- Complexity-based routing
- Dynamic workflow based on results

**Example**:
```python
if code_complexity > 50:
    agent = "advanced-test-generator"
else:
    agent = "simple-test-generator"

result = await fleet.execute(agent, task)
```

**Details**: [Conditional Workflow](conditional-workflow.md)

---

## Real-World Examples

### Example 1: Complete QA Pipeline

```python
async def complete_qa_pipeline(code: str):
    fleet = QEFleet(enable_routing=True)
    await fleet.initialize()

    # Step 1: Generate tests (single agent)
    tests = await fleet.execute("test-generator", QETask(
        task_type="generate_tests",
        context={"code": code, "framework": "pytest"}
    ))

    # Step 2: Run quality checks in parallel
    checks = await fleet.execute_parallel(
        agents=["test-executor", "security-scanner", "code-complexity"],
        tasks=[
            {"task_type": "execute_tests", "test_path": "./tests"},
            {"task_type": "security_scan", "code_path": "./src"},
            {"task_type": "analyze_complexity", "code_path": "./src"}
        ]
    )

    # Step 3: Sequential analysis and gate
    final = await fleet.execute_pipeline(
        pipeline=["coverage-analyzer", "quality-gate"],
        context={
            "test_results": checks[0],
            "security_results": checks[1],
            "complexity_results": checks[2]
        }
    )

    return final
```

### Example 2: Microservice Test Suite

```python
async def microservice_qa(services: list[str]):
    fleet = QEFleet(enable_routing=True)
    await fleet.initialize()

    # Fan-out: Generate tests for each service in parallel
    test_tasks = [
        QETask(task_type="generate_tests", context={"service": svc})
        for svc in services
    ]

    generated_tests = await fleet.execute_parallel(
        agents=["test-generator"] * len(services),
        tasks=test_tasks
    )

    # Sequential: Execute all tests, then analyze
    results = await fleet.execute_pipeline(
        pipeline=["test-executor", "coverage-analyzer"],
        context={"tests": generated_tests}
    )

    return results
```

### Example 3: Regression Testing Workflow

```python
async def smart_regression_test(code_changes: dict):
    fleet = QEFleet(enable_routing=True)
    await fleet.initialize()

    # Step 1: Analyze risk
    risk_analysis = await fleet.execute("regression-risk-analyzer", QETask(
        task_type="analyze_risk",
        context={"changes": code_changes}
    ))

    # Step 2: Conditional execution based on risk
    if risk_analysis.risk_score > 0.7:
        # High risk: Full test suite
        result = await fleet.execute_pipeline(
            pipeline=["test-executor", "coverage-analyzer", "quality-gate"],
            context={"scope": "full"}
        )
    else:
        # Low risk: Selected tests only
        result = await fleet.execute("test-executor", QETask(
            task_type="execute_tests",
            context={"tests": risk_analysis.selected_tests}
        ))

    return result
```

## Pattern Selection Guide

### Choose Sequential Pipeline When:
- Tasks have dependencies
- Results flow from one to the next
- Order matters for correctness

### Choose Parallel Execution When:
- Tasks are independent
- No data dependencies
- Speed is critical

### Choose Fan-Out/Fan-In When:
- Complex request needs decomposition
- Multiple perspectives required
- Single synthesized output desired

### Choose Conditional Workflow When:
- Different paths based on conditions
- Dynamic agent selection
- Adaptive workflows

## Performance Considerations

### Sequential Pipeline
- **Time**: Sum of all agent execution times
- **Memory**: Low (one agent at a time)
- **Cost**: Moderate (sequential routing)

### Parallel Execution
- **Time**: Max of all agent execution times
- **Memory**: High (all agents simultaneously)
- **Cost**: Lower (parallel routing optimizes)

### Fan-Out/Fan-In
- **Time**: Max of workers + coordinator overhead
- **Memory**: High (multiple workers)
- **Cost**: Higher (coordinator uses sophisticated model)

## Best Practices

### 1. Parallelize When Possible
```python
# ❌ Slow
await fleet.execute("agent1", task1)
await fleet.execute("agent2", task2)

# ✅ Fast
await fleet.execute_parallel(["agent1", "agent2"], [task1, task2])
```

### 2. Share Context via Memory
```python
# Agent 1 stores results
await fleet.memory.store("aqe/agent1/results", results)

# Agent 2 retrieves
data = await fleet.memory.retrieve("aqe/agent1/results")
```

### 3. Use Fleet Commander for Complexity
```python
# ❌ Manual coordination (complex, error-prone)
task1 = decompose_task(request)
task2 = decompose_task(request)
# ...

# ✅ Fleet commander (intelligent, automatic)
await fleet.execute_fan_out_fan_in(
    coordinator="fleet-commander",
    workers=["agent1", "agent2", "agent3"],
    context={"request": request}
)
```

### 4. Monitor and Optimize
```python
status = await fleet.get_status()
print(f"Workflows: {status['orchestration_metrics']['workflows_executed']}")
print(f"Cost: ${status['routing_stats']['total_cost']:.4f}")
print(f"Savings: {status['routing_stats']['savings_percentage']:.1f}%")
```

## Anti-Patterns to Avoid

### ❌ Sequential When Parallel Would Work
```python
# Bad: 30 seconds total
await fleet.execute("security", task1)  # 10s
await fleet.execute("performance", task2)  # 10s
await fleet.execute("visual", task3)  # 10s

# Good: 10 seconds total
await fleet.execute_parallel(
    ["security", "performance", "visual"],
    [task1, task2, task3]
)
```

### ❌ No Context Sharing
```python
# Bad: Agents don't share results
result1 = await fleet.execute("agent1", task)
# result1 lost, agent2 can't use it
result2 = await fleet.execute("agent2", task)

# Good: Share via memory
result1 = await fleet.execute("agent1", task)
await fleet.memory.store("aqe/shared/result1", result1)
result2 = await fleet.execute("agent2", task)
```

### ❌ Ignoring Routing
```python
# Bad: Always use expensive model
model = iModel(provider="openai", model="gpt-4")  # $0.0048 per call

# Good: Let routing optimize
fleet = QEFleet(enable_routing=True)  # up to 80% theoretical savings
```

## Next Steps

- [Sequential Pipeline](sequential-pipeline.md) - Detailed sequential workflow guide
- [Parallel Execution](parallel-execution.md) - Parallel execution patterns
- [Fan-Out/Fan-In](fan-out-fan-in.md) - Hierarchical coordination
- [Conditional Workflow](conditional-workflow.md) - Dynamic routing patterns

---

**See Also**: [Agent Catalog](../agents/index.md) | [Basic Workflows](../quickstart/basic-workflows.md)
