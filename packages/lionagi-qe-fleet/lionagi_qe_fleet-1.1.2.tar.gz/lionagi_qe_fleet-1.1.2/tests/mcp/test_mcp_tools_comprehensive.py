"""Comprehensive tests for MCP tools - targeting 90%+ coverage

This test suite covers all tool functions in mcp_tools.py with proper mocking
to achieve comprehensive coverage without requiring full agent implementations.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from lionagi_qe.mcp import mcp_tools
from lionagi_qe.mcp.mcp_tools import TestFramework, TestType, ScanType
from lionagi_qe.core.task import QETask


@pytest.fixture
def mock_fleet():
    """Mock QE Fleet instance with proper async methods"""
    fleet = Mock()
    fleet.execute = AsyncMock()
    fleet.execute_pipeline = AsyncMock()
    fleet.execute_parallel = AsyncMock()
    fleet.execute_fan_out_fan_in = AsyncMock()
    fleet.get_status = AsyncMock()
    fleet.get_agent = AsyncMock()
    mcp_tools.set_fleet_instance(fleet)
    return fleet


@pytest.fixture
def reset_fleet():
    """Reset fleet instance after test"""
    yield
    mcp_tools.set_fleet_instance(None)


class TestFleetInstanceManagement:
    """Test fleet instance management functions"""

    def test_set_fleet_instance(self):
        """Test setting fleet instance"""
        mock_fleet = Mock()
        mcp_tools.set_fleet_instance(mock_fleet)

        fleet = mcp_tools.get_fleet_instance()
        assert fleet is mock_fleet

    def test_get_fleet_instance_not_initialized(self):
        """Test get_fleet_instance raises error when not initialized"""
        # Explicitly set to None
        mcp_tools.set_fleet_instance(None)

        with pytest.raises(RuntimeError, match="Fleet not initialized"):
            mcp_tools.get_fleet_instance()


class TestEnums:
    """Test enum definitions"""

    def test_test_framework_enum(self):
        """Test TestFramework enum values"""
        assert TestFramework.PYTEST == "pytest"
        assert TestFramework.JEST == "jest"
        assert TestFramework.MOCHA == "mocha"
        assert TestFramework.CYPRESS == "cypress"
        assert TestFramework.PLAYWRIGHT == "playwright"
        assert TestFramework.JUNIT == "junit"

    def test_test_type_enum(self):
        """Test TestType enum values"""
        assert TestType.UNIT == "unit"
        assert TestType.INTEGRATION == "integration"
        assert TestType.E2E == "e2e"
        assert TestType.PERFORMANCE == "performance"
        assert TestType.SECURITY == "security"
        assert TestType.API == "api"

    def test_scan_type_enum(self):
        """Test ScanType enum values"""
        assert ScanType.SAST == "sast"
        assert ScanType.DAST == "dast"
        assert ScanType.DEPENDENCY == "dependency"
        assert ScanType.SECRETS == "secrets"
        assert ScanType.COMPREHENSIVE == "comprehensive"


@pytest.mark.asyncio
class TestCoreTestingTools:
    """Test core testing tools"""

    async def test_test_generate_success(self, mock_fleet):
        """Test successful test generation"""
        # Mock execute result
        mock_result = Mock()
        mock_result.test_code = "def test_example(): pass"
        mock_result.test_name = "test_example"
        mock_result.assertions = ["assert True"]
        mock_result.edge_cases = ["null input", "empty string"]
        mock_result.coverage_estimate = 85.5
        mock_result.framework = "pytest"
        mock_result.test_type = "unit"
        mock_result.dependencies = ["pytest"]

        mock_fleet.execute.return_value = mock_result

        # Execute
        result = await mcp_tools.test_generate(
            code="def add(a, b): return a + b",
            framework=TestFramework.PYTEST,
            test_type=TestType.UNIT,
            coverage_target=80.0,
            include_edge_cases=True
        )

        # Verify
        assert result["test_code"] == "def test_example(): pass"
        assert result["test_name"] == "test_example"
        assert result["assertions"] == ["assert True"]
        assert result["edge_cases"] == ["null input", "empty string"]
        assert result["coverage_estimate"] == 85.5
        assert result["framework"] == "pytest"
        assert result["test_type"] == "unit"
        assert result["dependencies"] == ["pytest"]

        # Verify fleet was called correctly
        mock_fleet.execute.assert_called_once()
        call_args = mock_fleet.execute.call_args
        assert call_args[0][0] == "test-generator"
        task = call_args[0][1]
        assert task.task_type == "test_generation"
        assert task.context["code"] == "def add(a, b): return a + b"
        assert task.context["framework"] == "pytest"
        assert task.context["test_type"] == "unit"
        assert task.context["coverage_target"] == 80.0
        assert task.context["include_edge_cases"] is True

    async def test_test_generate_different_framework(self, mock_fleet):
        """Test test generation with different framework"""
        mock_result = Mock()
        mock_result.test_code = "test('example', () => {})"
        mock_result.test_name = "example test"
        mock_result.assertions = []
        mock_result.edge_cases = []
        mock_result.coverage_estimate = 90.0
        mock_result.framework = "jest"
        mock_result.test_type = "integration"
        mock_result.dependencies = ["jest"]

        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.test_generate(
            code="function add(a, b) { return a + b; }",
            framework=TestFramework.JEST,
            test_type=TestType.INTEGRATION,
            coverage_target=90.0,
            include_edge_cases=False
        )

        assert result["framework"] == "jest"
        assert result["test_type"] == "integration"

    async def test_test_execute_success(self, mock_fleet):
        """Test successful test execution"""
        mock_fleet.execute.return_value = {
            "passed": 10,
            "failed": 2,
            "skipped": 1,
            "coverage": 85.5,
            "duration": 12.3,
            "failures": ["test_foo failed", "test_bar failed"]
        }

        result = await mcp_tools.test_execute(
            test_path="./tests",
            framework=TestFramework.PYTEST,
            parallel=True,
            coverage=True,
            timeout=300
        )

        assert result["passed"] == 10
        assert result["failed"] == 2
        assert result["skipped"] == 1
        assert result["coverage"] == 85.5
        assert result["duration"] == 12.3
        assert result["failures"] == ["test_foo failed", "test_bar failed"]
        assert result["success"] is False  # Because failed > 0

        # Verify task context
        call_args = mock_fleet.execute.call_args[0]
        task = call_args[1]
        assert task.task_type == "test_execution"
        assert task.context["test_path"] == "./tests"
        assert task.context["framework"] == "pytest"
        assert task.context["parallel"] is True
        assert task.context["coverage"] is True
        assert task.context["timeout"] == 300

    async def test_test_execute_all_passed(self, mock_fleet):
        """Test execution with all tests passing"""
        mock_fleet.execute.return_value = {
            "passed": 15,
            "failed": 0,
            "skipped": 0,
            "coverage": 95.0,
            "duration": 8.5,
            "failures": []
        }

        result = await mcp_tools.test_execute(
            test_path="./tests/unit",
            framework=TestFramework.JEST
        )

        assert result["success"] is True  # No failures
        assert result["passed"] == 15
        assert result["failed"] == 0

    async def test_test_execute_defaults(self, mock_fleet):
        """Test execution with default values"""
        mock_fleet.execute.return_value = {
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "coverage": 0.0,
            "duration": 0.0,
            "failures": []
        }

        result = await mcp_tools.test_execute(
            test_path="./empty_tests"
        )

        # Should handle missing keys gracefully
        assert result["passed"] == 0
        assert result["failed"] == 0
        assert result["skipped"] == 0
        assert result["coverage"] == 0.0
        assert result["duration"] == 0.0
        assert result["failures"] == []

    async def test_coverage_analyze_success(self, mock_fleet):
        """Test successful coverage analysis"""
        mock_result = {
            "overall_coverage": 87.5,
            "file_coverage": {
                "src/module_a.py": 95.0,
                "src/module_b.py": 80.0
            },
            "gaps": [
                {"file": "src/module_b.py", "lines": [10, 15, 20], "priority": "high"}
            ],
            "recommendations": ["Add tests for error handling"],
            "meets_threshold": True
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.coverage_analyze(
            source_path="./src",
            test_path="./tests",
            threshold=80.0,
            algorithm="sublinear"
        )

        assert result == mock_result

        # Verify task
        task = mock_fleet.execute.call_args[0][1]
        assert task.task_type == "coverage_analysis"
        assert task.context["source_path"] == "./src"
        assert task.context["test_path"] == "./tests"
        assert task.context["threshold"] == 80.0
        assert task.context["algorithm"] == "sublinear"

    async def test_coverage_analyze_different_algorithm(self, mock_fleet):
        """Test coverage analysis with different algorithm"""
        mock_fleet.execute.return_value = {"overall_coverage": 75.0}

        result = await mcp_tools.coverage_analyze(
            source_path="./src",
            test_path="./tests",
            threshold=90.0,
            algorithm="comprehensive"
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["algorithm"] == "comprehensive"
        assert task.context["threshold"] == 90.0

    async def test_quality_gate_success(self, mock_fleet):
        """Test quality gate with passing metrics"""
        mock_result = {
            "passed": True,
            "score": 95.0,
            "violations": [],
            "risks": [],
            "recommendations": ["Keep up the good work"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.quality_gate(
            metrics={"coverage": 95.0, "complexity": 5.0},
            thresholds={"coverage": 90.0, "complexity": 10.0}
        )

        assert result == mock_result
        assert result["passed"] is True
        assert result["score"] == 95.0

    async def test_quality_gate_default_thresholds(self, mock_fleet):
        """Test quality gate with default thresholds"""
        mock_fleet.execute.return_value = {"passed": False, "score": 65.0}

        result = await mcp_tools.quality_gate(
            metrics={"coverage": 70.0}
        )

        # Verify default thresholds were used
        task = mock_fleet.execute.call_args[0][1]
        assert task.context["thresholds"] == {
            "coverage": 80.0,
            "complexity": 10.0,
            "duplication": 5.0,
            "security_score": 90.0,
        }

    async def test_quality_gate_failures(self, mock_fleet):
        """Test quality gate with violations"""
        mock_result = {
            "passed": False,
            "score": 55.0,
            "violations": [
                {"metric": "coverage", "value": 65.0, "threshold": 80.0}
            ],
            "risks": [
                {"type": "low_coverage", "severity": "high"}
            ],
            "recommendations": ["Increase test coverage"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.quality_gate(
            metrics={"coverage": 65.0}
        )

        assert result["passed"] is False
        assert len(result["violations"]) > 0
        assert len(result["risks"]) > 0


@pytest.mark.asyncio
class TestPerformanceAndSecurityTools:
    """Test performance and security tools"""

    async def test_performance_test_success(self, mock_fleet):
        """Test successful performance test"""
        mock_result = {
            "requests_per_second": 1500.0,
            "response_time_p50": 25.0,
            "response_time_p95": 120.0,
            "response_time_p99": 250.0,
            "error_rate": 0.5,
            "total_requests": 90000
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.performance_test(
            endpoint="https://api.example.com/users",
            duration=60,
            users=10,
            ramp_up=5,
            tool="locust"
        )

        assert result == mock_result
        assert result["requests_per_second"] == 1500.0
        assert result["error_rate"] == 0.5

        # Verify task
        task = mock_fleet.execute.call_args[0][1]
        assert task.task_type == "performance_test"
        assert task.context["endpoint"] == "https://api.example.com/users"
        assert task.context["duration"] == 60
        assert task.context["users"] == 10
        assert task.context["ramp_up"] == 5
        assert task.context["tool"] == "locust"

    async def test_performance_test_different_tool(self, mock_fleet):
        """Test performance test with different tool"""
        mock_fleet.execute.return_value = {
            "requests_per_second": 2000.0,
            "response_time_p50": 15.0,
            "response_time_p95": 80.0,
            "response_time_p99": 150.0,
            "error_rate": 0.1,
            "total_requests": 120000
        }

        result = await mcp_tools.performance_test(
            endpoint="https://api.example.com/products",
            duration=120,
            users=50,
            ramp_up=10,
            tool="k6"
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["tool"] == "k6"
        assert task.context["users"] == 50

    async def test_security_scan_comprehensive(self, mock_fleet):
        """Test comprehensive security scan"""
        mock_result = {
            "vulnerabilities": [
                {"type": "SQL Injection", "severity": "high", "file": "app.py"}
            ],
            "severity_counts": {"low": 5, "medium": 3, "high": 1, "critical": 0},
            "risk_score": 75.0,
            "recommendations": ["Fix SQL injection vulnerability"],
            "compliance_status": {"OWASP": "partial", "PCI-DSS": "fail"}
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.security_scan(
            path="./src",
            scan_type=ScanType.COMPREHENSIVE,
            severity_threshold="medium"
        )

        assert result == mock_result
        assert len(result["vulnerabilities"]) > 0

        # Verify task
        task = mock_fleet.execute.call_args[0][1]
        assert task.task_type == "security_scan"
        assert task.context["path"] == "./src"
        assert task.context["scan_type"] == "comprehensive"
        assert task.context["severity_threshold"] == "medium"

    async def test_security_scan_sast_only(self, mock_fleet):
        """Test SAST-only security scan"""
        mock_result = {
            "vulnerabilities": [],
            "severity_counts": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "risk_score": 95.0,
            "recommendations": [],
            "compliance_status": {}
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.security_scan(
            path="./src/secure_module.py",
            scan_type=ScanType.SAST,
            severity_threshold="high"
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["scan_type"] == "sast"
        assert task.context["severity_threshold"] == "high"

    async def test_security_scan_dependency_check(self, mock_fleet):
        """Test dependency security scan"""
        mock_result = {
            "vulnerabilities": [
                {"package": "requests", "version": "2.25.0", "severity": "medium"}
            ],
            "severity_counts": {"low": 0, "medium": 1, "high": 0, "critical": 0},
            "risk_score": 85.0,
            "recommendations": ["Update requests to version 2.31.0"],
            "compliance_status": {}
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.security_scan(
            path="./requirements.txt",
            scan_type=ScanType.DEPENDENCY
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["scan_type"] == "dependency"


@pytest.mark.asyncio
class TestFleetOrchestrationTools:
    """Test fleet orchestration tools"""

    async def test_fleet_orchestrate_pipeline(self, mock_fleet):
        """Test pipeline orchestration"""
        mock_result = {
            "results": [{"agent": "test-generator", "output": "success"}],
            "agents_used": ["test-generator", "test-executor"],
            "duration": 45.2,
            "success": True
        }
        mock_fleet.execute_pipeline.return_value = mock_result

        result = await mcp_tools.fleet_orchestrate(
            workflow="pipeline",
            context={"test_type": "unit"},
            agents=["test-generator", "test-executor"]
        )

        assert result == mock_result
        mock_fleet.execute_pipeline.assert_called_once_with(
            pipeline=["test-generator", "test-executor"],
            context={"test_type": "unit"}
        )

    async def test_fleet_orchestrate_parallel(self, mock_fleet):
        """Test parallel orchestration"""
        mock_result = {
            "results": [
                {"agent": "security-scanner", "output": "no issues"},
                {"agent": "performance-tester", "output": "passed"}
            ],
            "agents_used": ["security-scanner", "performance-tester"],
            "duration": 30.0,
            "success": True
        }
        mock_fleet.execute_parallel.return_value = mock_result

        result = await mcp_tools.fleet_orchestrate(
            workflow="parallel",
            context={"tasks": ["scan", "load_test"]},
            agents=["security-scanner", "performance-tester"]
        )

        assert result == mock_result
        mock_fleet.execute_parallel.assert_called_once()

    async def test_fleet_orchestrate_fan_out_fan_in(self, mock_fleet):
        """Test fan-out-fan-in orchestration"""
        mock_result = {
            "results": {"aggregated": "data"},
            "agents_used": ["worker-1", "worker-2", "worker-3"],
            "duration": 60.0,
            "success": True
        }
        mock_fleet.execute_fan_out_fan_in.return_value = mock_result

        result = await mcp_tools.fleet_orchestrate(
            workflow="fan-out-fan-in",
            context={"coordinator": "fleet-commander", "data": "test"},
            agents=["worker-1", "worker-2", "worker-3"]
        )

        assert result == mock_result
        mock_fleet.execute_fan_out_fan_in.assert_called_once()

    async def test_fleet_orchestrate_invalid_workflow(self, mock_fleet):
        """Test invalid workflow type"""
        with pytest.raises(ValueError, match="Unknown workflow type"):
            await mcp_tools.fleet_orchestrate(
                workflow="invalid_workflow",
                context={},
                agents=[]
            )

    async def test_get_fleet_status(self, mock_fleet):
        """Test getting fleet status"""
        mock_status = {
            "initialized": True,
            "agents": ["test-generator", "test-executor", "fleet-commander"],
            "memory_stats": {"total_keys": 42, "size_mb": 1.2},
            "routing_stats": {"enabled": True, "total_calls": 100},
            "performance_metrics": {"avg_latency_ms": 50}
        }
        mock_fleet.get_status.return_value = mock_status

        result = await mcp_tools.get_fleet_status()

        assert result == mock_status
        assert result["initialized"] is True
        assert len(result["agents"]) == 3
        mock_fleet.get_status.assert_called_once()


@pytest.mark.asyncio
class TestAdvancedTools:
    """Test advanced QE tools"""

    async def test_requirements_validate_success(self, mock_fleet):
        """Test requirements validation"""
        mock_result = {
            "valid_requirements": ["User can login", "User can logout"],
            "invalid_requirements": [
                {"req": "System works", "issues": ["too vague"]}
            ],
            "bdd_scenarios": [
                "Given a user\nWhen they login\nThen they see dashboard"
            ],
            "invest_scores": {"User can login": {"I": 0.9, "N": 0.8}}
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.requirements_validate(
            requirements=["User can login", "User can logout", "System works"],
            format="user_story"
        )

        assert result == mock_result
        task = mock_fleet.execute.call_args[0][1]
        assert task.task_type == "requirements_validation"
        assert task.context["format"] == "user_story"

    async def test_requirements_validate_different_format(self, mock_fleet):
        """Test requirements validation with different format"""
        mock_fleet.execute.return_value = {
            "valid_requirements": [],
            "invalid_requirements": [],
            "bdd_scenarios": [],
            "invest_scores": {}
        }

        await mcp_tools.requirements_validate(
            requirements=["UC1: User logs in"],
            format="use_case"
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["format"] == "use_case"

    async def test_flaky_test_hunt_success(self, mock_fleet):
        """Test flaky test detection"""
        mock_result = {
            "flaky_tests": [
                {"name": "test_random_failure", "flakiness": 0.3}
            ],
            "stability_scores": {"test_random_failure": 0.7, "test_stable": 1.0},
            "root_causes": ["Race condition in async code"],
            "fixes": ["Add proper async synchronization"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.flaky_test_hunt(
            test_path="./tests",
            iterations=10,
            detect_threshold=0.1
        )

        assert result == mock_result
        assert len(result["flaky_tests"]) > 0

        task = mock_fleet.execute.call_args[0][1]
        assert task.task_type == "flaky_test_detection"
        assert task.context["iterations"] == 10
        assert task.context["detect_threshold"] == 0.1

    async def test_flaky_test_hunt_more_iterations(self, mock_fleet):
        """Test flaky test detection with more iterations"""
        mock_fleet.execute.return_value = {
            "flaky_tests": [],
            "stability_scores": {},
            "root_causes": [],
            "fixes": []
        }

        await mcp_tools.flaky_test_hunt(
            test_path="./tests/integration",
            iterations=100,
            detect_threshold=0.05
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["iterations"] == 100
        assert task.context["detect_threshold"] == 0.05

    async def test_api_contract_validate_single_version(self, mock_fleet):
        """Test API contract validation for single version"""
        mock_result = {
            "valid": True,
            "breaking_changes": [],
            "warnings": [],
            "recommendations": ["Add rate limiting headers"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.api_contract_validate(
            spec_path="./openapi.yaml",
            version_a="v1.0.0",
            version_b=None
        )

        assert result == mock_result
        assert result["valid"] is True

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["version_b"] is None

    async def test_api_contract_validate_breaking_changes(self, mock_fleet):
        """Test API contract validation detecting breaking changes"""
        mock_result = {
            "valid": False,
            "breaking_changes": [
                {"type": "removed_endpoint", "path": "/api/v1/old"}
            ],
            "warnings": ["Response time increased"],
            "recommendations": ["Maintain backward compatibility"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.api_contract_validate(
            spec_path="./openapi.yaml",
            version_a="v1.0.0",
            version_b="v2.0.0"
        )

        assert result["valid"] is False
        assert len(result["breaking_changes"]) > 0

    async def test_regression_risk_analyze_with_ml(self, mock_fleet):
        """Test regression risk analysis with ML enabled"""
        mock_result = {
            "high_risk_tests": ["test_payment", "test_auth"],
            "medium_risk_tests": ["test_profile"],
            "low_risk_tests": ["test_ui_colors"],
            "risk_scores": {"test_payment": 0.95, "test_auth": 0.88},
            "estimated_time_saved": 300.0
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.regression_risk_analyze(
            changes=["src/payment.py", "src/auth.py"],
            test_suite="./tests",
            ml_enabled=True
        )

        assert result == mock_result
        assert len(result["high_risk_tests"]) == 2

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["ml_enabled"] is True

    async def test_regression_risk_analyze_without_ml(self, mock_fleet):
        """Test regression risk analysis without ML"""
        mock_fleet.execute.return_value = {
            "high_risk_tests": [],
            "medium_risk_tests": [],
            "low_risk_tests": [],
            "risk_scores": {},
            "estimated_time_saved": 0.0
        }

        await mcp_tools.regression_risk_analyze(
            changes=["src/utils.py"],
            test_suite="./tests",
            ml_enabled=False
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["ml_enabled"] is False

    async def test_test_data_generate_realistic(self, mock_fleet):
        """Test realistic test data generation"""
        mock_result = {
            "data": [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}],
            "record_count": 2,
            "generation_time": 0.002,
            "records_per_second": 1000.0
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.test_data_generate(
            schema={"id": "integer", "name": "string"},
            count=1000,
            realistic=True
        )

        assert result["record_count"] == 2
        assert result["records_per_second"] == 1000.0

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["realistic"] is True
        assert task.context["count"] == 1000

    async def test_test_data_generate_random(self, mock_fleet):
        """Test random test data generation"""
        mock_fleet.execute.return_value = {
            "data": [],
            "record_count": 0,
            "generation_time": 0.0,
            "records_per_second": 0.0
        }

        await mcp_tools.test_data_generate(
            schema={"field": "type"},
            count=100,
            realistic=False
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["realistic"] is False

    async def test_visual_test_success(self, mock_fleet):
        """Test visual regression testing"""
        mock_result = {
            "matches": 8,
            "differences": 2,
            "diff_details": [
                {"file": "screenshot1.png", "similarity": 0.85}
            ],
            "similarity_scores": {"screenshot1.png": 0.85}
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.visual_test(
            baseline_path="./screenshots/baseline",
            current_path="./screenshots/current",
            threshold=0.95
        )

        assert result["matches"] == 8
        assert result["differences"] == 2

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["threshold"] == 0.95

    async def test_visual_test_different_threshold(self, mock_fleet):
        """Test visual testing with different threshold"""
        mock_fleet.execute.return_value = {
            "matches": 10,
            "differences": 0,
            "diff_details": [],
            "similarity_scores": {}
        }

        await mcp_tools.visual_test(
            baseline_path="./baseline",
            current_path="./current",
            threshold=0.8
        )

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["threshold"] == 0.8

    async def test_chaos_test_success(self, mock_fleet):
        """Test chaos engineering"""
        mock_result = {
            "resilience_score": 85.0,
            "fault_results": {
                "latency": {"passed": True, "recovery_time": 2.5},
                "errors": {"passed": False, "recovery_time": 10.0}
            },
            "recovery_times": {"latency": 2.5, "errors": 10.0},
            "recommendations": ["Improve error handling"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.chaos_test(
            target="https://api.example.com",
            fault_types=["latency", "errors"],
            duration=300
        )

        assert result["resilience_score"] == 85.0
        assert len(result["fault_results"]) == 2

        task = mock_fleet.execute.call_args[0][1]
        assert task.context["duration"] == 300

    async def test_chaos_test_multiple_faults(self, mock_fleet):
        """Test chaos engineering with multiple fault types"""
        mock_fleet.execute.return_value = {
            "resilience_score": 70.0,
            "fault_results": {},
            "recovery_times": {},
            "recommendations": []
        }

        await mcp_tools.chaos_test(
            target="https://service.example.com",
            fault_types=["latency", "errors", "resource_exhaustion"],
            duration=600
        )

        task = mock_fleet.execute.call_args[0][1]
        assert len(task.context["fault_types"]) == 3

    async def test_deployment_readiness_ready(self, mock_fleet):
        """Test deployment readiness check - ready to deploy"""
        mock_result = {
            "ready": True,
            "risk_level": "low",
            "factors": {
                "tests": "passed",
                "coverage": "above_threshold",
                "security": "no_issues"
            },
            "blockers": [],
            "recommendations": ["Schedule deployment"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.deployment_readiness(
            version="v2.1.0",
            environment="production"
        )

        assert result["ready"] is True
        assert result["risk_level"] == "low"
        assert len(result["blockers"]) == 0

    async def test_deployment_readiness_not_ready(self, mock_fleet):
        """Test deployment readiness check - not ready"""
        mock_result = {
            "ready": False,
            "risk_level": "high",
            "factors": {
                "tests": "failed",
                "coverage": "below_threshold"
            },
            "blockers": ["Test failures", "Low coverage"],
            "recommendations": ["Fix test failures before deployment"]
        }
        mock_fleet.execute.return_value = mock_result

        result = await mcp_tools.deployment_readiness(
            version="v2.0.0-beta",
            environment="staging"
        )

        assert result["ready"] is False
        assert result["risk_level"] == "high"
        assert len(result["blockers"]) > 0


@pytest.mark.asyncio
class TestStreamingTools:
    """Test streaming tool implementations"""

    async def test_test_execute_stream_progress(self, mock_fleet):
        """Test streaming test execution with progress"""
        events = []

        async for event in mcp_tools.test_execute_stream(
            test_path="./tests",
            framework=TestFramework.PYTEST,
            parallel=True,
            coverage=True
        ):
            events.append(event)

        # Should have progress events
        progress_events = [e for e in events if e["type"] == "progress"]
        assert len(progress_events) == 10

        # Check progress percentages increase
        for i, event in enumerate(progress_events):
            assert event["percent"] == (i + 1) * 10
            assert "message" in event
            assert "current_test" in event

        # Should have final result
        result_events = [e for e in events if e["type"] == "result"]
        assert len(result_events) == 1
        assert "data" in result_events[0]

    async def test_test_execute_stream_different_framework(self, mock_fleet):
        """Test streaming with different framework"""
        events = []

        async for event in mcp_tools.test_execute_stream(
            test_path="./tests/e2e",
            framework=TestFramework.CYPRESS,
            parallel=False,
            coverage=False
        ):
            events.append(event)

        # Should still have events
        assert len(events) > 0

        # Final result should exist
        assert events[-1]["type"] == "result"

    async def test_test_execute_stream_can_break_early(self, mock_fleet):
        """Test that streaming can be cancelled early"""
        event_count = 0

        async for event in mcp_tools.test_execute_stream(
            test_path="./tests",
            framework=TestFramework.PYTEST
        ):
            event_count += 1
            if event_count == 3:
                break  # Stop early

        # Should have stopped early
        assert event_count == 3
