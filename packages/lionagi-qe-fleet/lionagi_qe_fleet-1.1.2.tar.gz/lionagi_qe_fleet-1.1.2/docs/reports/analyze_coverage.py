#!/usr/bin/env python3
"""
Real Coverage Analysis using LionAGI QE Fleet CoverageAnalyzerAgent

This script analyzes the actual test coverage of the LionAGI QE Fleet codebase
and provides actionable recommendations for improvement.
"""

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv
from lionagi import iModel

from lionagi_qe.core.memory import QEMemory
from lionagi_qe.core.task import QETask
from lionagi_qe.agents import CoverageAnalyzerAgent

load_dotenv()


def load_coverage_data():
    """Load coverage data from pytest-cov JSON output"""
    coverage_file = Path("coverage.json")

    if not coverage_file.exists():
        print("❌ Coverage file not found. Run: pytest --cov=src/lionagi_qe --cov-report=json")
        return None

    with open(coverage_file) as f:
        return json.load(f)


def parse_coverage_for_agent(coverage_data):
    """Parse pytest-cov JSON into agent-friendly format"""
    files_data = coverage_data.get("files", {})
    totals = coverage_data.get("totals", {})

    # Extract per-file coverage
    file_coverage = {}
    low_coverage_files = []

    for file_path, file_data in files_data.items():
        # Skip test files and __pycache__
        if "__pycache__" in file_path or "/tests/" in file_path:
            continue

        summary = file_data.get("summary", {})
        num_statements = summary.get("num_statements", 0)
        covered_lines = summary.get("covered_lines", 0)
        missing_lines = summary.get("missing_lines", 0)

        if num_statements > 0:
            coverage_percent = (covered_lines / num_statements) * 100

            file_coverage[file_path] = {
                "lines": {
                    "covered": covered_lines,
                    "total": num_statements
                },
                "coverage_percent": coverage_percent,
                "missing_lines": missing_lines
            }

            # Identify low coverage files (< 80%)
            if coverage_percent < 80:
                low_coverage_files.append({
                    "path": file_path,
                    "coverage": coverage_percent,
                    "missing": missing_lines
                })

    # Calculate overall metrics
    overall_coverage = totals.get("percent_covered", 0)

    return {
        "overall": overall_coverage,
        "files": file_coverage,
        "low_coverage_files": sorted(low_coverage_files, key=lambda x: x["coverage"]),
        "total_statements": totals.get("num_statements", 0),
        "covered_statements": totals.get("covered_lines", 0),
        "missing_statements": totals.get("missing_lines", 0)
    }


async def analyze_with_agent(coverage_data):
    """Use CoverageAnalyzerAgent to analyze the coverage"""
    print("\n" + "="*80)
    print("  🤖 LionAGI QE Fleet - Real Coverage Analysis")
    print("="*80 + "\n")

    # Initialize agent
    print("🔧 Initializing CoverageAnalyzerAgent...")
    model = iModel(provider="openai", model="gpt-4o-mini")
    memory = QEMemory()
    agent = CoverageAnalyzerAgent(
        agent_id="coverage-analyzer-real",
        model=model,
        memory=memory
    )

    # Create task with real coverage data
    print("📊 Preparing coverage data...")
    parsed_data = parse_coverage_for_agent(coverage_data)

    print(f"\n📈 Current Coverage Snapshot:")
    print(f"   Overall Coverage: {parsed_data['overall']:.1f}%")
    print(f"   Total Statements: {parsed_data['total_statements']}")
    print(f"   Covered Statements: {parsed_data['covered_statements']}")
    print(f"   Missing Statements: {parsed_data['missing_statements']}")
    print(f"   Files with <80% coverage: {len(parsed_data['low_coverage_files'])}")

    task = QETask(
        task_type="analyze_coverage",
        context={
            "coverage_data": parsed_data,
            "framework": "pytest",
            "codebase_path": "src/lionagi_qe",
            "target_coverage": 90  # Aiming for 90% coverage
        }
    )

    # Execute agent
    print("\n🔍 Running CoverageAnalyzerAgent with O(log n) gap detection...")
    result = await agent.execute(task)

    return result, parsed_data


def display_results(result, parsed_data):
    """Display analysis results in a readable format"""
    print("\n" + "="*80)
    print("  ✅ Coverage Analysis Complete!")
    print("="*80 + "\n")

    # Overall metrics
    print("📊 Coverage Metrics:")
    print(f"   Overall Coverage: {result.overall_coverage:.1f}%")
    print(f"   Line Coverage: {result.line_coverage:.1f}%")
    print(f"   Branch Coverage: {result.branch_coverage:.1f}%")
    print(f"   Function Coverage: {result.function_coverage:.1f}%")

    # Gaps detected
    print(f"\n🔍 Gaps Detected: {len(result.gaps)}")
    if result.gaps:
        print("\n📍 Top Coverage Gaps (sorted by severity):")
        gaps_by_severity = sorted(result.gaps,
                                   key=lambda x: (x.severity == "critical",
                                                  x.severity == "high",
                                                  x.severity == "medium"),
                                   reverse=True)

        for i, gap in enumerate(gaps_by_severity[:10], 1):
            print(f"\n   {i}. {gap.file_path}")
            print(f"      Lines: {gap.line_start}-{gap.line_end}")
            print(f"      Severity: {gap.severity.upper()}")
            print(f"      Critical Path: {'Yes ⚠️' if gap.critical_path else 'No'}")
            if gap.suggested_tests:
                print(f"      Suggested Tests:")
                for test in gap.suggested_tests[:2]:
                    print(f"        • {test}")

    # Critical paths
    if result.critical_paths:
        print(f"\n🎯 Critical Paths Identified: {len(result.critical_paths)}")
        for i, path in enumerate(result.critical_paths[:5], 1):
            print(f"   {i}. {path}")

    # Optimization suggestions
    if result.optimization_suggestions:
        print(f"\n💡 Optimization Suggestions:")
        for i, suggestion in enumerate(result.optimization_suggestions, 1):
            print(f"   {i}. {suggestion}")

    # Trends
    if result.trends:
        print(f"\n📈 Coverage Trends:")
        for key, value in result.trends.items():
            if isinstance(value, (int, float)):
                print(f"   {key}: {value:.1f}%")
            else:
                print(f"   {key}: {value}")

    # Performance
    print(f"\n⚡ Performance:")
    print(f"   Analysis Time: {result.analysis_time_ms:.1f}ms")
    print(f"   Algorithm: O(log n) sublinear gap detection")

    # Files needing attention
    print(f"\n📁 Files Needing Attention (< 80% coverage):")
    for i, file_info in enumerate(parsed_data['low_coverage_files'][:10], 1):
        print(f"   {i}. {Path(file_info['path']).name}")
        print(f"      Path: {file_info['path']}")
        print(f"      Coverage: {file_info['coverage']:.1f}%")
        print(f"      Missing Lines: {file_info['missing']}")

    # Summary
    coverage_gap = 90 - result.overall_coverage
    if coverage_gap > 0:
        print(f"\n🎯 To Reach 90% Coverage:")
        print(f"   Current: {result.overall_coverage:.1f}%")
        print(f"   Target: 90%")
        print(f"   Gap: {coverage_gap:.1f}%")
        print(f"   Estimated Tests Needed: {len(result.gaps)}")
    else:
        print(f"\n🎉 Excellent! You've exceeded the 90% coverage target!")


async def main():
    """Main execution"""
    try:
        # Load coverage data
        coverage_data = load_coverage_data()
        if not coverage_data:
            return

        # Analyze with agent
        result, parsed_data = await analyze_with_agent(coverage_data)

        # Display results
        display_results(result, parsed_data)

        print("\n" + "="*80)
        print("  📚 Next Steps:")
        print("="*80)
        print("\n  1. Review the gaps listed above")
        print("  2. Prioritize critical path coverage")
        print("  3. Focus on files with < 80% coverage")
        print("  4. Use the suggested tests as starting points")
        print("  5. Run: pytest --cov=src/lionagi_qe --cov-report=html")
        print("  6. Open htmlcov/index.html to see detailed line-by-line coverage")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
