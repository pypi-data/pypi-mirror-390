# Agent Catalog

Complete catalog of all 18 specialized QE agents in the LionAGI QE Fleet.

## Quick Reference

| Agent | Purpose | Key Capability |
|-------|---------|----------------|
| [TestGeneratorAgent](#testgeneratoragent) | Generate tests | AI-powered edge case detection |
| [TestExecutorAgent](#testexecutoragent) | Execute tests | Parallel async execution |
| [CoverageAnalyzerAgent](#coverageanalyzeragent) | Analyze coverage | O(log n) gap detection |
| [QualityGateAgent](#qualitygateagent) | Quality decisions | Multi-factor risk assessment |
| [QualityAnalyzerAgent](#qualityanalyzeragent) | Quality metrics | Predictive analytics |
| [CodeComplexityAgent](#codecomplexityagent) | Complexity analysis | AI refactoring suggestions |
| [PerformanceTesterAgent](#performancetesteragent) | Load testing | K6/JMeter/Gatling support |
| [SecurityScannerAgent](#securityscanneragent) | Security scanning | SAST/DAST/SCA layers |
| [RequirementsValidatorAgent](#requirementsvalidatoragent) | Validate requirements | INVEST criteria analysis |
| [ProductionIntelligenceAgent](#productionintelligenceagent) | Production insights | Incident replay as tests |
| [FleetCommanderAgent](#fleetcommanderagent) | Fleet coordination | Hierarchical orchestration |
| [RegressionRiskAnalyzerAgent](#regressionriskanalyzeragent) | Smart test selection | 90% test reduction |
| [TestDataArchitectAgent](#testdataarchitectagent) | Test data generation | 10k+ records/sec |
| [APIContractValidatorAgent](#apicontractvalidatoragent) | API contracts | Breaking change detection |
| [FlakyTestHunterAgent](#flakytesthunteragent) | Find flaky tests | 98% detection accuracy |
| [DeploymentReadinessAgent](#deploymentreadinessagent) | Deployment decisions | 6-dimensional risk scoring |
| [VisualTesterAgent](#visualtesteragent) | Visual regression | AI-powered screenshot diff |
| [ChaosEngineerAgent](#chaosengineera gent) | Chaos testing | Controlled fault injection |

## Agent Categories

### Core Testing (6 agents)
Foundation agents for test generation, execution, and quality analysis.

### Performance & Security (2 agents)
Specialized agents for non-functional testing.

### Strategic Planning (3 agents)
High-level coordination and requirements validation.

### Advanced Testing (4 agents)
Sophisticated agents for specialized testing needs.

### Specialized (3 agents)
Niche agents for specific quality domains.

---

## Core Testing Agents

### TestGeneratorAgent

**Purpose**: Generate comprehensive test suites with edge case detection

**Capabilities**:
- Property-based testing patterns
- Boundary value analysis
- Edge case detection
- Multi-framework support (pytest, Jest, Mocha, Cypress)
- TDD and BDD pattern generation
- Test pattern learning and reuse

**Input**: Source code + framework
**Output**: `GeneratedTest` (test code, assertions, edge cases)

**Example**:
```python
from lionagi_qe.agents import TestGeneratorAgent

agent = TestGeneratorAgent(
    agent_id="test-gen",
    model=iModel(provider="openai", model="gpt-4o-mini"),
    memory=fleet.memory
)

result = await fleet.execute("test-gen", QETask(
    task_type="generate_tests",
    context={"code": source_code, "framework": "pytest"}
))
```

**Best For**: Unit tests, integration tests, edge case coverage

---

### TestExecutorAgent

**Purpose**: Execute tests across multiple frameworks in parallel

**Capabilities**:
- Multi-framework execution (pytest, Jest, Mocha, Cypress)
- Parallel test execution with async operations
- Coverage reporting (line, branch, function)
- Failure analysis and categorization
- Performance metrics (duration, memory)

**Input**: Test files + framework
**Output**: `TestExecutionResult` (pass/fail, coverage, duration)

**Example**:
```python
from lionagi_qe.agents import TestExecutorAgent

agent = TestExecutorAgent(
    agent_id="test-exec",
    model=iModel(provider="openai", model="gpt-4o-mini"),
    memory=fleet.memory
)

result = await fleet.execute("test-exec", QETask(
    task_type="execute_tests",
    context={"test_path": "./tests", "framework": "pytest", "parallel": True}
))
```

**Best For**: Fast test execution, CI/CD pipelines, coverage collection

---

### CoverageAnalyzerAgent

**Purpose**: Real-time gap detection with sublinear algorithms

**Capabilities**:
- Johnson-Lindenstrauss dimension reduction (O(log n))
- Spectral sparsification for large codebases
- Temporal prediction for future coverage needs
- Critical path identification
- Gap prioritization by risk

**Input**: Code + test coverage data
**Output**: `CoverageAnalysisResult` (gaps, metrics, recommendations)

**Example**:
```python
from lionagi_qe.agents import CoverageAnalyzerAgent

agent = CoverageAnalyzerAgent(
    agent_id="coverage-analyzer",
    model=iModel(provider="openai", model="gpt-4"),
    memory=fleet.memory
)

result = await fleet.execute("coverage-analyzer", QETask(
    task_type="analyze_coverage",
    context={"coverage_data": coverage_json, "code_path": "./src"}
))
```

**Best For**: Finding coverage gaps, prioritizing tests, scaling coverage

---

### QualityGateAgent

**Purpose**: Intelligent go/no-go decision making

**Capabilities**:
- Multi-factor risk assessment
- Policy violation detection
- Dynamic threshold adjustment
- AI-driven decision trees
- Deployment readiness scoring

**Input**: Quality metrics + policies
**Output**: `QualityGateResult` (decision, risk scores, violations)

**Example**:
```python
from lionagi_qe.agents import QualityGateAgent

agent = QualityGateAgent(
    agent_id="quality-gate",
    model=iModel(provider="openai", model="gpt-4"),
    memory=fleet.memory
)

result = await fleet.execute("quality-gate", QETask(
    task_type="evaluate_quality",
    context={"metrics": quality_metrics, "policies": deployment_policies}
))
```

**Best For**: Deployment decisions, quality enforcement, risk management

---

### QualityAnalyzerAgent

**Purpose**: Comprehensive quality metrics collection

**Capabilities**:
- Code quality scoring (maintainability, complexity)
- Test quality evaluation (coverage, assertions)
- Technical debt quantification
- Predictive analytics (quality trends)
- Anomaly detection

**Input**: Codebase + test suite
**Output**: `QualityAnalysisResult` (scores, debt, trends)

**Best For**: Quality dashboards, trend analysis, technical debt tracking

---

### CodeComplexityAgent

**Purpose**: Cyclomatic and cognitive complexity analysis

**Capabilities**:
- Cyclomatic complexity measurement
- Cognitive complexity analysis
- File size and function metrics
- AI-powered refactoring recommendations
- Quality scoring (0-100)

**Input**: Source code
**Output**: `CodeComplexityResult` (metrics, recommendations)

**Best For**: Code reviews, refactoring priorities, maintainability tracking

---

## Performance & Security Agents

### PerformanceTesterAgent

**Purpose**: Load testing with k6, JMeter, Gatling integration

**Capabilities**:
- Multi-tool support (JMeter, K6, Gatling)
- Load patterns (ramp-up, steady state, stress)
- P50/P95/P99 response time metrics
- SLA validation
- Bottleneck detection

**Input**: API endpoints + load profile
**Output**: `PerformanceTestResult` (metrics, bottlenecks)

**Best For**: Performance baselines, SLA validation, scalability testing

---

### SecurityScannerAgent

**Purpose**: Multi-layer security scanning (SAST/DAST)

**Capabilities**:
- SAST (static analysis)
- DAST (dynamic analysis)
- SCA (dependency scanning)
- Vulnerability detection (OWASP Top 10)
- Compliance validation (PCI-DSS, HIPAA, SOC2)
- CVE/CWE tracking with CVSS scoring

**Input**: Codebase + running application
**Output**: `SecurityScanResult` (vulnerabilities, compliance)

**Best For**: Security audits, compliance checks, vulnerability management

---

## Strategic Planning Agents

### RequirementsValidatorAgent

**Purpose**: Testability analysis with INVEST criteria

**Capabilities**:
- INVEST validation (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- BDD scenario generation
- Risk assessment per requirement
- SMART criteria validation
- Traceability mapping
- Edge case detection from requirements

**Input**: Requirements documents
**Output**: `RequirementValidationResult` (issues, scenarios, risks)

**Best For**: Requirements review, test planning, BDD scenarios

---

### ProductionIntelligenceAgent

**Purpose**: Convert production data to test scenarios

**Capabilities**:
- Incident replay as tests
- RUM (Real User Monitoring) analysis
- Anomaly detection in production
- Load pattern analysis
- Feature usage analytics
- Error pattern mining

**Input**: Production logs + monitoring data
**Output**: `ProductionIntelligenceResult` (scenarios, insights)

**Best For**: Production bug reproduction, realistic load testing, usage-driven testing

---

### FleetCommanderAgent

**Purpose**: Hierarchical coordination of 50+ QE agents

**Capabilities**:
- Intelligent task decomposition
- Agent assignment and coordination
- Multi-agent workflow orchestration
- Progress monitoring
- Result synthesis
- Dynamic re-assignment on failure

**Input**: High-level QE request
**Output**: Synthesized multi-agent results

**Best For**: Complex QA workflows, multi-agent coordination, comprehensive QA

---

## Advanced Testing Agents

### RegressionRiskAnalyzerAgent

**Purpose**: Smart test selection via ML patterns

**Capabilities**:
- Change impact analysis
- Intelligent test selection (90% reduction possible)
- Risk heat mapping
- Dependency tracking
- Historical pattern learning

**Input**: Code changes + test history
**Output**: `RegressionRiskResult` (risk score, test selection)

**Best For**: CI/CD optimization, selective testing, risk-based testing

---

### TestDataArchitectAgent

**Purpose**: Generate realistic test data (10k+ records/sec)

**Capabilities**:
- Schema-aware generation
- Relationship preservation (foreign keys)
- Edge case coverage in data
- Data anonymization (GDPR/HIPAA)
- High-speed generation (10,000+ records/sec)

**Input**: Database schema + constraints
**Output**: `TestDataResult` (generated data, schema)

**Best For**: Database testing, integration testing, data-driven testing

---

### APIContractValidatorAgent

**Purpose**: Detect breaking changes in APIs

**Capabilities**:
- Schema validation (OpenAPI, GraphQL)
- Breaking change detection
- Semantic versioning validation
- Consumer impact analysis
- 95% breaking change prevention

**Input**: API schemas (old + new)
**Output**: `APIContractResult` (breaking changes, impact)

**Best For**: API versioning, microservices testing, consumer-driven contracts

---

### FlakyTestHunterAgent

**Purpose**: Statistical flaky test detection

**Capabilities**:
- Statistical flaky test detection (98% accuracy)
- Root cause analysis with ML
- Auto-stabilization (65% success rate)
- Quarantine management
- 95%+ test reliability

**Input**: Test execution history
**Output**: `FlakyTestResult` (flaky tests, root causes, fixes)

**Best For**: Test suite stability, CI/CD reliability, developer productivity

---

## Specialized Agents

### DeploymentReadinessAgent

**Purpose**: Multi-factor deployment risk assessment

**Capabilities**:
- 6-dimensional risk scoring (tests, coverage, security, performance, complexity, history)
- Bayesian release confidence
- Deployment checklist validation
- Rollback risk prediction
- Deployment gate enforcement

**Input**: Quality metrics + deployment context
**Output**: `DeploymentDecision` (go/no-go, risk scores)

**Best For**: Deployment decisions, release gates, risk management

---

### VisualTesterAgent

**Purpose**: AI-powered visual regression testing

**Capabilities**:
- 3 comparison algorithms (pixel-diff, SSIM, AI)
- WCAG 2.1/2.2 accessibility validation
- Cross-browser testing
- Responsive design testing
- Visual performance metrics

**Input**: Screenshots (baseline + current)
**Output**: `VisualTestResult` (regressions, accessibility issues)

**Best For**: UI testing, accessibility compliance, visual consistency

---

### ChaosEngineerAgent

**Purpose**: Resilience testing with controlled chaos

**Capabilities**:
- Systematic fault injection
- Blast radius control
- Hypothesis-driven experiments
- Safety validation before execution
- Resilience scoring (0-100)

**Input**: System topology + failure scenarios
**Output**: `ChaosExperimentResult` (resilience score, observations)

**Best For**: Resilience testing, disaster recovery validation, SRE practices

---

## Usage Patterns

### Single Agent
```python
agent = TestGeneratorAgent(agent_id="test-gen", model=model, memory=fleet.memory)
fleet.register_agent(agent)
result = await fleet.execute("test-gen", task)
```

### Sequential Pipeline
```python
pipeline = ["test-generator", "test-executor", "coverage-analyzer"]
result = await fleet.execute_pipeline(pipeline, context)
```

### Parallel Execution
```python
agents = ["test-gen-1", "test-gen-2", "test-gen-3"]
results = await fleet.execute_parallel(agents, tasks)
```

### Hierarchical Coordination
```python
result = await fleet.execute_fan_out_fan_in(
    coordinator="fleet-commander",
    workers=["test-gen", "security", "performance"],
    context=context
)
```

## Agent Metrics

Each agent tracks:
- Tasks completed
- Tasks failed
- Total cost (via multi-model routing)
- Patterns learned (if learning enabled)

Access metrics:
```python
metrics = await agent.get_metrics()
print(f"Tasks: {metrics['tasks_completed']}")
print(f"Cost: ${metrics['total_cost']:.4f}")
```

## Cost Optimization

Agents automatically use optimal models via routing:
- **Simple tasks** → GPT-3.5 ($0.0004)
- **Moderate tasks** → GPT-4o-mini ($0.0008)
- **Complex tasks** → GPT-4 ($0.0048)
- **Critical tasks** → Claude Sonnet 4.5 ($0.0065)

**Result**: up to 80% theoretical cost savings

Enable routing:
```python
fleet = QEFleet(enable_routing=True)
```

## Next Steps

- [Core Testing Details](core-testing.md) - Deep dive into core testing agents
- [Performance & Security Details](performance-security.md) - Performance and security agents
- [Strategic Planning Details](strategic-planning.md) - Strategic and coordination agents
- [Advanced Testing Details](advanced-testing.md) - Advanced and specialized agents

---

**Total Fleet Capacity**: 18 specialized agents ready for comprehensive quality engineering
