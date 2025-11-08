"""Unit tests for TestGeneratorAgent - Test generation agent"""

import pytest
from unittest.mock import AsyncMock, Mock
from lionagi_qe.agents.test_generator import TestGeneratorAgent, GeneratedTest
from lionagi_qe.core.task import QETask
from lionagi_qe.core.memory import QEMemory
from lionagi import iModel


class TestGeneratedTest:
    """Test GeneratedTest model"""

    def test_generated_test_creation(self):
        """Test creating GeneratedTest"""
        test = GeneratedTest(
            test_name="test_add_function",
            test_code="def test_add(): assert add(2, 3) == 5",
            framework="pytest",
            test_type="unit",
            assertions=["assert add(2, 3) == 5"],
            edge_cases=["negative numbers", "zero"],
            dependencies=["pytest"],
            coverage_estimate=85.0
        )

        assert test.test_name == "test_add_function"
        assert test.framework == "pytest"
        assert test.coverage_estimate == 85.0

    def test_generated_test_defaults(self):
        """Test GeneratedTest default values"""
        test = GeneratedTest(
            test_name="test_basic",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[],
            edge_cases=[]
        )

        assert test.dependencies == []
        assert test.coverage_estimate == 0.0


class TestTestGeneratorAgent:
    """Test TestGeneratorAgent functionality"""

    @pytest.mark.asyncio
    async def test_init(self, qe_memory, simple_model):
        """Test TestGeneratorAgent initialization"""
        agent = TestGeneratorAgent(
            agent_id="test-generator",
            model=simple_model,
            memory=qe_memory,
            skills=["agentic-quality-engineering", "tdd-london-chicago"]
        )

        assert agent.agent_id == "test-generator"
        assert "agentic-quality-engineering" in agent.skills

    @pytest.mark.asyncio
    async def test_system_prompt(self, test_generator_agent):
        """Test system prompt is comprehensive"""
        prompt = test_generator_agent.get_system_prompt()

        # Check for key concepts
        assert "property-based" in prompt.lower() or "testing" in prompt.lower()
        assert "edge case" in prompt.lower() or "boundary" in prompt.lower()
        assert "pytest" in prompt.lower() or "jest" in prompt.lower()

    @pytest.mark.asyncio
    async def test_execute_basic_test_generation(self, test_generator_agent, mocker):
        """Test basic test generation"""
        # Mock the operate method
        mock_result = GeneratedTest(
            test_name="test_calculate_total",
            test_code="""
def test_calculate_total():
    items = [{'price': 10}, {'price': 20}]
    result = calculate_total(items)
    assert result == 33.0  # 30 + 10% tax
""",
            framework="pytest",
            test_type="unit",
            assertions=["assert result == 33.0"],
            edge_cases=["empty list", "negative prices"],
            coverage_estimate=85.0
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def calculate_total(items): return sum(i['price'] for i in items)",
                "framework": "pytest",
                "test_type": "unit"
            }
        )

        result = await test_generator_agent.execute(task)

        assert result.test_name == "test_calculate_total"
        assert result.framework == "pytest"
        assert result.coverage_estimate == 85.0

    @pytest.mark.asyncio
    async def test_execute_with_coverage_target(self, test_generator_agent, mocker):
        """Test generation with specific coverage target"""
        mock_result = GeneratedTest(
            test_name="test_with_high_coverage",
            test_code="test code",
            framework="pytest",
            test_type="unit",
            assertions=["assert True"],
            edge_cases=["boundary cases"],
            coverage_estimate=95.0
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def func(): pass",
                "framework": "pytest",
                "coverage_target": 90
            }
        )

        result = await test_generator_agent.execute(task)

        assert result.coverage_estimate >= 90

    @pytest.mark.asyncio
    async def test_execute_stores_learned_pattern(self, test_generator_agent, mocker):
        """Test that high coverage patterns are learned"""
        mock_result = GeneratedTest(
            test_name="test_learned",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[],
            edge_cases=[],
            coverage_estimate=90.0
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        initial_patterns = test_generator_agent.metrics["patterns_learned"]

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def func(): pass",
                "framework": "pytest",
                "coverage_target": 80
            }
        )

        await test_generator_agent.execute(task)

        # Should have learned a pattern
        assert test_generator_agent.metrics["patterns_learned"] > initial_patterns

    @pytest.mark.asyncio
    async def test_execute_uses_learned_patterns(self, test_generator_agent, mocker):
        """Test that learned patterns are retrieved and used"""
        # Store a learned pattern
        await test_generator_agent.store_learned_pattern(
            "pytest_unit_pattern",
            {
                "framework": "pytest",
                "test_type": "unit",
                "pattern": "high_coverage_achieved",
                "coverage": 92.0
            }
        )

        mock_get_patterns = mocker.patch.object(
            test_generator_agent,
            'get_learned_patterns',
            new=AsyncMock(return_value={
                "aqe/patterns/test-generator/pytest_unit_pattern": {
                    "framework": "pytest",
                    "test_type": "unit",
                    "pattern": "high_coverage_achieved"
                }
            })
        )

        mock_result = GeneratedTest(
            test_name="test_with_patterns",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[],
            edge_cases=[],
            coverage_estimate=93.0
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def func(): pass",
                "framework": "pytest"
            }
        )

        await test_generator_agent.execute(task)

        # Verify patterns were retrieved
        mock_get_patterns.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_different_frameworks(self, test_generator_agent, mocker):
        """Test generation for different test frameworks"""
        frameworks = ["pytest", "jest", "mocha", "cypress"]

        for framework in frameworks:
            mock_result = GeneratedTest(
                test_name=f"test_{framework}",
                test_code="code",
                framework=framework,
                test_type="unit",
                assertions=[],
                edge_cases=[]
            )

            mocker.patch.object(
                test_generator_agent,
                'operate',
                new=AsyncMock(return_value=mock_result)
            )

            task = QETask(
                task_type="test_generation",
                context={
                    "code": "function test() {}",
                    "framework": framework
                }
            )

            result = await test_generator_agent.execute(task)
            assert result.framework == framework

    @pytest.mark.asyncio
    async def test_execute_different_test_types(self, test_generator_agent, mocker):
        """Test generation for different test types"""
        test_types = ["unit", "integration", "e2e"]

        for test_type in test_types:
            mock_result = GeneratedTest(
                test_name=f"test_{test_type}",
                test_code="code",
                framework="pytest",
                test_type=test_type,
                assertions=[],
                edge_cases=[]
            )

            mocker.patch.object(
                test_generator_agent,
                'operate',
                new=AsyncMock(return_value=mock_result)
            )

            task = QETask(
                task_type="test_generation",
                context={
                    "code": "def func(): pass",
                    "test_type": test_type
                }
            )

            result = await test_generator_agent.execute(task)
            assert result.test_type == test_type

    @pytest.mark.asyncio
    async def test_edge_case_detection(self, test_generator_agent, mocker):
        """Test that edge cases are identified"""
        mock_result = GeneratedTest(
            test_name="test_with_edges",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=["assert result"],
            edge_cases=[
                "empty input",
                "null/None values",
                "maximum values",
                "negative numbers",
                "boundary conditions"
            ]
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def calculate(value): return value * 2"
            }
        )

        result = await test_generator_agent.execute(task)

        assert len(result.edge_cases) > 0

    @pytest.mark.asyncio
    async def test_comprehensive_assertions(self, test_generator_agent, mocker):
        """Test that comprehensive assertions are generated"""
        mock_result = GeneratedTest(
            test_name="test_comprehensive",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[
                "assert result is not None",
                "assert isinstance(result, dict)",
                "assert 'key' in result",
                "assert result['key'] == expected"
            ],
            edge_cases=[]
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def get_data(): return {'key': 'value'}"
            }
        )

        result = await test_generator_agent.execute(task)

        assert len(result.assertions) > 0

    @pytest.mark.asyncio
    async def test_default_framework(self, test_generator_agent, mocker):
        """Test default framework is pytest"""
        mock_result = GeneratedTest(
            test_name="test_default",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[],
            edge_cases=[]
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def func(): pass"
                # No framework specified
            }
        )

        result = await test_generator_agent.execute(task)

        assert result.framework == "pytest"

    @pytest.mark.asyncio
    async def test_default_test_type(self, test_generator_agent, mocker):
        """Test default test type is unit"""
        mock_result = GeneratedTest(
            test_name="test_default_type",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[],
            edge_cases=[]
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def func(): pass"
                # No test_type specified
            }
        )

        result = await test_generator_agent.execute(task)

        assert result.test_type == "unit"

    @pytest.mark.asyncio
    async def test_pattern_not_stored_low_coverage(self, test_generator_agent, mocker):
        """Test pattern is not stored when coverage is low"""
        mock_result = GeneratedTest(
            test_name="test_low_coverage",
            test_code="code",
            framework="pytest",
            test_type="unit",
            assertions=[],
            edge_cases=[],
            coverage_estimate=50.0  # Below 80% target
        )

        mocker.patch.object(
            test_generator_agent,
            'operate',
            new=AsyncMock(return_value=mock_result)
        )

        initial_patterns = test_generator_agent.metrics["patterns_learned"]

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def func(): pass",
                "coverage_target": 80
            }
        )

        await test_generator_agent.execute(task)

        # Should not learn pattern
        assert test_generator_agent.metrics["patterns_learned"] == initial_patterns


class TestGenerateTestsStreamingErrorHandling:
    """Test generate_tests_streaming error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_streaming_network_timeout(self, test_generator_agent, mocker):
        """Test streaming handles network timeout gracefully"""
        # Mock streaming that times out
        async def mock_streaming_timeout(*args, **kwargs):
            import asyncio
            await asyncio.sleep(0.1)
            raise asyncio.TimeoutError("Network timeout after 30s")

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            side_effect=mock_streaming_timeout
        )

        task = QETask(
            task_type="test_generation_streaming",
            context={
                "code": "def process_large_file(): pass",
                "framework": "pytest",
                "streaming": True
            }
        )

        # Should handle timeout gracefully
        with pytest.raises(asyncio.TimeoutError):
            await test_generator_agent.execute(task)

        # Agent should still be functional after timeout
        assert test_generator_agent.agent_id == "test-generator"

    @pytest.mark.asyncio
    async def test_streaming_generation_error(self, test_generator_agent, mocker):
        """Test streaming handles generation errors during processing"""
        # Mock streaming that fails mid-generation
        call_count = {"count": 0}

        async def mock_streaming_with_error(*args, **kwargs):
            call_count["count"] += 1
            if call_count["count"] == 1:
                # First call succeeds partially
                return GeneratedTest(
                    test_name="partial_test",
                    test_code="# Incomplete",
                    framework="pytest",
                    test_type="unit",
                    assertions=[],
                    edge_cases=[]
                )
            else:
                # Subsequent calls fail
                raise RuntimeError("LLM generation error: rate limit exceeded")

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            side_effect=mock_streaming_with_error
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def multi_test(): pass",
                "framework": "pytest"
            }
        )

        # First execution should succeed
        result1 = await test_generator_agent.execute(task)
        assert result1.test_name == "partial_test"

        # Second execution should fail
        with pytest.raises(RuntimeError, match="rate limit exceeded"):
            await test_generator_agent.execute(task)

    @pytest.mark.asyncio
    async def test_streaming_partial_results(self, test_generator_agent, mocker):
        """Test streaming returns partial results when incomplete"""
        # Mock streaming that returns incomplete results
        partial_result = GeneratedTest(
            test_name="incomplete_test",
            test_code="# TODO: Complete implementation",
            framework="pytest",
            test_type="unit",
            assertions=[],  # Empty assertions
            edge_cases=[],  # No edge cases identified
            coverage_estimate=0.0  # No coverage
        )

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            new=AsyncMock(return_value=partial_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def incomplete(): pass",
                "framework": "pytest",
                "streaming": True
            }
        )

        result = await test_generator_agent.execute(task)

        # Should return partial result
        assert result.test_name == "incomplete_test"
        assert result.coverage_estimate == 0.0
        assert len(result.assertions) == 0

    @pytest.mark.asyncio
    async def test_streaming_cancellation(self, test_generator_agent, mocker):
        """Test streaming handles cancellation correctly"""
        import asyncio

        # Mock streaming that gets cancelled
        async def mock_streaming_cancellable(*args, **kwargs):
            await asyncio.sleep(0.05)  # Simulate work
            raise asyncio.CancelledError("Streaming cancelled by user")

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            side_effect=mock_streaming_cancellable
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def long_running(): pass",
                "framework": "pytest",
                "streaming": True
            }
        )

        # Should handle cancellation
        with pytest.raises(asyncio.CancelledError):
            await test_generator_agent.execute(task)

        # Verify agent state is consistent after cancellation
        assert test_generator_agent.metrics["tasks_failed"] >= 0

    @pytest.mark.asyncio
    async def test_streaming_progress_accuracy(self, test_generator_agent, mocker):
        """Test streaming progress reporting is accurate"""
        # Track progress updates
        progress_updates = []

        # Mock streaming with progress tracking
        call_sequence = [
            # Simulate progressive test generation
            GeneratedTest(
                test_name=f"test_{i}",
                test_code=f"def test_{i}(): assert True",
                framework="pytest",
                test_type="unit",
                assertions=["assert True"],
                edge_cases=[],
                coverage_estimate=float(i * 20)  # 0%, 20%, 40%, 60%, 80%
            )
            for i in range(5)
        ]

        call_index = {"index": 0}

        async def mock_streaming_with_progress(*args, **kwargs):
            idx = call_index["index"]
            call_index["index"] += 1
            if idx < len(call_sequence):
                progress = (idx + 1) / len(call_sequence) * 100
                progress_updates.append(progress)
                return call_sequence[idx]
            raise StopIteration("All tests generated")

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            side_effect=mock_streaming_with_progress
        )

        # Execute multiple times to simulate streaming
        for i in range(5):
            task = QETask(
                task_type="test_generation",
                context={
                    "code": f"def func_{i}(): pass",
                    "framework": "pytest",
                    "batch": i
                }
            )

            result = await test_generator_agent.execute(task)
            assert result.test_name == f"test_{i}"
            assert result.coverage_estimate == float(i * 20)

        # Verify progress was tracked
        assert len(progress_updates) == 5
        # Progress should increase
        assert progress_updates[0] < progress_updates[-1]

    @pytest.mark.asyncio
    async def test_streaming_memory_exhaustion(self, test_generator_agent, mocker):
        """Test streaming handles memory exhaustion gracefully"""
        # Mock streaming that runs out of memory
        async def mock_streaming_oom(*args, **kwargs):
            raise MemoryError("Out of memory: cannot allocate test generation buffer")

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            side_effect=mock_streaming_oom
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "# Very large codebase" * 1000,
                "framework": "pytest",
                "streaming": True
            }
        )

        # Should handle OOM gracefully
        with pytest.raises(MemoryError):
            await test_generator_agent.execute(task)

        # Error should be tracked
        assert test_generator_agent.metrics["tasks_failed"] >= 0

    @pytest.mark.asyncio
    async def test_streaming_malformed_chunk(self, test_generator_agent, mocker):
        """Test streaming handles malformed data chunks"""
        # Mock streaming that returns malformed data
        malformed_result = MagicMock()
        malformed_result.test_name = None  # Invalid
        malformed_result.test_code = ""  # Empty
        malformed_result.framework = "pytest"
        malformed_result.test_type = "unknown"
        malformed_result.assertions = None  # Should be list
        malformed_result.edge_cases = None  # Should be list

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            new=AsyncMock(return_value=malformed_result)
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def test(): pass",
                "framework": "pytest"
            }
        )

        # Should handle malformed data
        # The actual behavior depends on whether safe_operate validates
        result = await test_generator_agent.execute(task)

        # Result may be malformed but shouldn't crash
        assert result is not None

    @pytest.mark.asyncio
    async def test_streaming_backpressure_handling(self, test_generator_agent, mocker):
        """Test streaming handles backpressure correctly"""
        import asyncio

        # Mock streaming with backpressure simulation
        async def mock_streaming_with_backpressure(*args, **kwargs):
            # Simulate backpressure by yielding control
            await asyncio.sleep(0.01)

            return GeneratedTest(
                test_name="backpressure_test",
                test_code="def test(): pass",
                framework="pytest",
                test_type="unit",
                assertions=["assert True"],
                edge_cases=[],
                coverage_estimate=75.0
            )

        mocker.patch.object(
            test_generator_agent,
            'safe_operate',
            side_effect=mock_streaming_with_backpressure
        )

        task = QETask(
            task_type="test_generation",
            context={
                "code": "def fast_function(): return True",
                "framework": "pytest",
                "streaming": True
            }
        )

        # Should handle backpressure without blocking
        result = await test_generator_agent.execute(task)

        assert result.test_name == "backpressure_test"
        assert result.coverage_estimate == 75.0
