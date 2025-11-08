"""Demonstration of streaming progress updates"""

import asyncio
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, MagicMock

# Add src to path
import sys
sys.path.insert(0, '/workspaces/lionagi-qe-fleet/src')

from lionagi_qe.agents.test_generator import TestGeneratorAgent
from lionagi_qe.agents.coverage_analyzer import CoverageAnalyzerAgent
from lionagi_qe.core.task import QETask
from lionagi_qe.core.memory import QEMemory


class MockStreamingModel:
    """Mock model that simulates streaming responses"""

    async def stream(self, messages):
        """Simulate streaming chunks"""
        # Simulate streaming 5 test cases
        test_chunks = [
            '{"test_name": "test_add_positive_numbers", "test_code": "def test_add_positive_numbers(): assert add(2, 3) == 5", '
            '"framework": "pytest", "test_type": "unit", "assertions": ["assert add(2, 3) == 5"], '
            '"edge_cases": ["positive numbers"], "dependencies": [], "coverage_estimate": 85.0}',

            '{"test_name": "test_add_negative_numbers", "test_code": "def test_add_negative_numbers(): assert add(-2, -3) == -5", '
            '"framework": "pytest", "test_type": "unit", "assertions": ["assert add(-2, -3) == -5"], '
            '"edge_cases": ["negative numbers"], "dependencies": [], "coverage_estimate": 90.0}',

            '{"test_name": "test_add_zero", "test_code": "def test_add_zero(): assert add(0, 5) == 5", '
            '"framework": "pytest", "test_type": "unit", "assertions": ["assert add(0, 5) == 5"], '
            '"edge_cases": ["zero"], "dependencies": [], "coverage_estimate": 88.0}',

            '{"test_name": "test_add_large_numbers", "test_code": "def test_add_large_numbers(): assert add(1000000, 2000000) == 3000000", '
            '"framework": "pytest", "test_type": "unit", "assertions": ["assert add(1000000, 2000000) == 3000000"], '
            '"edge_cases": ["large numbers"], "dependencies": [], "coverage_estimate": 87.0}',

            '{"test_name": "test_add_float_numbers", "test_code": "def test_add_float_numbers(): assert abs(add(1.5, 2.5) - 4.0) < 0.001", '
            '"framework": "pytest", "test_type": "unit", "assertions": ["assert abs(add(1.5, 2.5) - 4.0) < 0.001"], '
            '"edge_cases": ["float numbers"], "dependencies": [], "coverage_estimate": 92.0}',
        ]

        for chunk_text in test_chunks:
            # Simulate gradual streaming
            for i in range(0, len(chunk_text), 50):
                chunk = MagicMock()
                chunk.choices = [MagicMock()]
                chunk.choices[0].delta = MagicMock()
                chunk.choices[0].delta.content = chunk_text[i:i+50]

                yield chunk
                await asyncio.sleep(0.05)


async def demo_test_generator_streaming():
    """Demonstrate test generator streaming"""
    print("\n" + "="*80)
    print("TEST GENERATOR STREAMING DEMO")
    print("="*80 + "\n")

    # Setup mock memory
    memory = Mock(spec=QEMemory)
    memory.retrieve = AsyncMock(return_value=None)
    memory.store = AsyncMock()
    memory.search = AsyncMock(return_value={})

    # Create agent with mock streaming model
    model = MockStreamingModel()
    agent = TestGeneratorAgent(
        agent_id="test-generator",
        model=model,
        memory=memory,
        skills=["test-generation"],
        enable_learning=False
    )

    # Create task
    task = QETask(
        task_type="test_generation",
        context={
            "code": """
def add(a: int, b: int) -> int:
    '''Add two numbers together'''
    return a + b
""",
            "framework": "pytest",
            "test_type": "unit",
            "coverage_target": 85,
            "target_count": 5,
        }
    )

    print("Starting test generation with streaming...\n")

    # Stream test generation
    progress_count = 0
    test_count = 0
    complete_count = 0

    async for event in agent.generate_tests_streaming(task):
        event_type = event.get("type")

        if event_type == "progress":
            progress_count += 1
            print(f"[PROGRESS] {event['percent']:5.1f}% - {event['message']}")

        elif event_type == "test":
            test_count += 1
            test_case = event["test_case"]
            print(f"\n[TEST #{test_count}] {test_case['test_name']}")
            print(f"  - Code: {test_case['test_code'][:60]}...")
            print(f"  - Framework: {test_case['framework']}")
            print(f"  - Coverage: {test_case['coverage_estimate']}%")

        elif event_type == "complete":
            complete_count += 1
            print(f"\n[COMPLETE] Generated {event['total']} tests")
            print(f"  - Average Coverage: {event['coverage_estimate']}%")
            print(f"  - Framework: {event['framework']}")
            print(f"  - Type: {event['test_type']}")

        elif event_type == "error":
            print(f"\n[ERROR] {event['message']}")

    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  - Progress events: {progress_count}")
    print(f"  - Test events: {test_count}")
    print(f"  - Complete events: {complete_count}")
    print(f"{'='*80}\n")


async def demo_coverage_analyzer_streaming():
    """Demonstrate coverage analyzer streaming"""
    print("\n" + "="*80)
    print("COVERAGE ANALYZER STREAMING DEMO")
    print("="*80 + "\n")

    # Setup mock memory
    memory = Mock(spec=QEMemory)
    memory.retrieve = AsyncMock(return_value=None)
    memory.store = AsyncMock()
    memory.search = AsyncMock(return_value={})

    # Create agent
    model = Mock()
    agent = CoverageAnalyzerAgent(
        agent_id="coverage-analyzer",
        model=model,
        memory=memory,
        skills=["coverage-analysis"],
        enable_learning=False
    )

    # Mock the operate method
    from lionagi_qe.agents.coverage_analyzer import CoverageAnalysisResult
    mock_result = CoverageAnalysisResult(
        overall_coverage=78.5,
        line_coverage=80.2,
        branch_coverage=75.8,
        function_coverage=82.1,
        gaps=[],
        critical_paths=["src/payment/processor.py::charge_card", "src/auth/validator.py::validate_token"],
        framework="pytest",
        analysis_time_ms=1250.0,
        optimization_suggestions=[
            "Add more unit tests for payment processor",
            "Improve branch coverage in auth validator",
            "Add integration tests for critical paths"
        ]
    )
    agent.operate = AsyncMock(return_value=mock_result)

    # Create task
    task = QETask(
        task_type="coverage_analysis",
        context={
            "coverage_data": {
                "files": {
                    "src/utils.py": {"coverage": 85.0},
                    "src/models.py": {"coverage": 92.0},
                    "src/handlers.py": {"coverage": 78.0},
                    "src/validators.py": {"coverage": 88.0},
                    "src/formatters.py": {"coverage": 75.0},
                }
            },
            "framework": "pytest",
            "codebase_path": "./src",
            "target_coverage": 85,
        }
    )

    print("Starting coverage analysis with streaming...\n")

    # Stream coverage analysis
    progress_count = 0
    gap_count = 0
    critical_path_count = 0
    complete_count = 0

    async for event in agent.analyze_coverage_streaming(task):
        event_type = event.get("type")

        if event_type == "progress":
            progress_count += 1
            print(f"[PROGRESS] {event['percent']:5.1f}% - {event['message']}")

        elif event_type == "gap":
            gap_count += 1
            gap = event["gap"]
            print(f"\n[GAP #{gap_count}] {gap['file_path']} (lines {gap['line_start']}-{gap['line_end']})")
            print(f"  - Type: {gap['gap_type']}")
            print(f"  - Severity: {gap['severity']}")
            print(f"  - Critical Path: {gap['critical_path']}")

        elif event_type == "critical_path":
            critical_path_count += 1
            print(f"\n[CRITICAL PATH] {event['path']} (impact: {event['impact']})")

        elif event_type == "complete":
            complete_count += 1
            print(f"\n[COMPLETE] Coverage Analysis Results:")
            print(f"  - Overall Coverage: {event['overall_coverage']}%")
            print(f"  - Line Coverage: {event['line_coverage']}%")
            print(f"  - Branch Coverage: {event['branch_coverage']}%")
            print(f"  - Function Coverage: {event['function_coverage']}%")
            print(f"  - Gaps Found: {event['gaps_count']}")
            print(f"  - Critical Paths: {event['critical_paths_count']}")
            print(f"  - Meets Threshold: {event['meets_threshold']}")
            print(f"  - Analysis Time: {event['analysis_time_ms']}ms")

        elif event_type == "error":
            print(f"\n[ERROR] {event['message']}")

    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"  - Progress events: {progress_count}")
    print(f"  - Gap events: {gap_count}")
    print(f"  - Critical path events: {critical_path_count}")
    print(f"  - Complete events: {complete_count}")
    print(f"{'='*80}\n")


async def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("STREAMING PROGRESS DEMO - Agentic QE Fleet")
    print("="*80)

    # Run test generator demo
    await demo_test_generator_streaming()

    # Wait a bit between demos
    await asyncio.sleep(1)

    # Run coverage analyzer demo
    await demo_coverage_analyzer_streaming()

    print("\n" + "="*80)
    print("ALL DEMOS COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
