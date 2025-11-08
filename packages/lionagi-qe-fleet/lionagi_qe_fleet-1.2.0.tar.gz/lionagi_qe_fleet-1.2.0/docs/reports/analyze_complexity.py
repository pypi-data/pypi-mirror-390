#!/usr/bin/env python3
"""
Code Complexity Analyzer for LionAGI QE Fleet

Analyzes Python code files for:
- Cyclomatic Complexity (McCabe)
- Cognitive Complexity
- Method/Function length
- Class complexity
- Maintainability Index
- Code smells (deep nesting, long parameter lists, etc.)
"""

import ast
import sys
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class MethodMetrics:
    """Metrics for a single method/function"""
    name: str
    line_start: int
    line_end: int
    lines: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    nesting_depth: int
    parameter_count: int
    return_points: int
    is_async: bool = False

    @property
    def complexity_score(self) -> float:
        """Combined complexity score"""
        return (self.cyclomatic_complexity * 0.6) + (self.cognitive_complexity * 0.4)


@dataclass
class ClassMetrics:
    """Metrics for a class"""
    name: str
    line_start: int
    line_end: int
    lines: int
    method_count: int
    total_complexity: int
    avg_complexity: float
    methods: List[MethodMetrics] = field(default_factory=list)


@dataclass
class FileMetrics:
    """Metrics for an entire file"""
    file_path: str
    lines: int
    functions: List[MethodMetrics]
    classes: List[ClassMetrics]
    maintainability_index: float
    total_complexity: int
    avg_complexity: float

    @property
    def method_count(self) -> int:
        return len(self.functions) + sum(c.method_count for c in self.classes)


class ComplexityAnalyzer:
    """Analyzes code complexity using AST parsing"""

    def __init__(self):
        self.file_metrics: List[FileMetrics] = []

    def analyze_file(self, file_path: Path) -> FileMetrics:
        """Analyze a single Python file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return None

        lines = content.count('\n') + 1
        functions = []
        classes = []

        # Analyze top-level functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Skip class methods (handled in class analysis)
                if not self._is_class_method(node, tree):
                    metrics = self._analyze_function(node, content)
                    functions.append(metrics)

            elif isinstance(node, ast.ClassDef):
                class_metrics = self._analyze_class(node, content)
                classes.append(class_metrics)

        # Calculate maintainability index
        total_complexity = sum(f.cyclomatic_complexity for f in functions)
        total_complexity += sum(c.total_complexity for c in classes)
        avg_complexity = total_complexity / (len(functions) + len(classes)) if (functions or classes) else 0

        mi = self._calculate_maintainability_index(lines, avg_complexity, len(functions) + len(classes))

        metrics = FileMetrics(
            file_path=str(file_path),
            lines=lines,
            functions=functions,
            classes=classes,
            maintainability_index=mi,
            total_complexity=total_complexity,
            avg_complexity=avg_complexity
        )

        self.file_metrics.append(metrics)
        return metrics

    def _is_class_method(self, node: ast.FunctionDef, tree: ast.AST) -> bool:
        """Check if a function is a class method"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                if node in parent.body:
                    return True
        return False

    def _analyze_function(self, node: ast.FunctionDef, content: str) -> MethodMetrics:
        """Analyze a function or method"""
        lines = content.split('\n')
        func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0

        # Cyclomatic complexity (McCabe)
        cyclomatic = self._calculate_cyclomatic_complexity(node)

        # Cognitive complexity
        cognitive = self._calculate_cognitive_complexity(node)

        # Nesting depth
        nesting = self._calculate_max_nesting_depth(node)

        # Parameter count
        param_count = len(node.args.args)

        # Return points
        returns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))

        return MethodMetrics(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            lines=func_lines,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            nesting_depth=nesting,
            parameter_count=param_count,
            return_points=returns,
            is_async=isinstance(node, ast.AsyncFunctionDef)
        )

    def _analyze_class(self, node: ast.ClassDef, content: str) -> ClassMetrics:
        """Analyze a class"""
        methods = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_metrics = self._analyze_function(item, content)
                methods.append(method_metrics)

        class_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
        total_complexity = sum(m.cyclomatic_complexity for m in methods)
        avg_complexity = total_complexity / len(methods) if methods else 0

        return ClassMetrics(
            name=node.name,
            line_start=node.lineno,
            line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            lines=class_lines,
            method_count=len(methods),
            total_complexity=total_complexity,
            avg_complexity=avg_complexity,
            methods=methods
        )

    def _calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """Calculate McCabe cyclomatic complexity"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each boolean operator adds complexity
                complexity += len(child.values) - 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)

        return complexity

    def _calculate_cognitive_complexity(self, node: ast.AST) -> int:
        """Calculate cognitive complexity (nesting aware)"""
        def calculate_recursive(node: ast.AST, nesting: int = 0) -> int:
            complexity = 0

            for child in ast.iter_child_nodes(node):
                # Base increments for control flow
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                    complexity += 1 + nesting
                    complexity += calculate_recursive(child, nesting + 1)

                elif isinstance(child, ast.ExceptHandler):
                    complexity += 1 + nesting
                    complexity += calculate_recursive(child, nesting + 1)

                elif isinstance(child, ast.BoolOp):
                    # Boolean operators in conditions
                    complexity += len(child.values) - 1
                    complexity += calculate_recursive(child, nesting)

                else:
                    complexity += calculate_recursive(child, nesting)

            return complexity

        return calculate_recursive(node)

    def _calculate_max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        def get_depth(node: ast.AST, current_depth: int = 0) -> int:
            max_depth = current_depth

            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.With, ast.Try)):
                    depth = get_depth(child, current_depth + 1)
                    max_depth = max(max_depth, depth)
                else:
                    depth = get_depth(child, current_depth)
                    max_depth = max(max_depth, depth)

            return max_depth

        return get_depth(node)

    def _calculate_maintainability_index(
        self,
        lines: int,
        avg_complexity: float,
        halstead_volume: float
    ) -> float:
        """
        Calculate Maintainability Index (simplified)
        MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)

        Simplified version without full Halstead metrics
        """
        if lines == 0 or avg_complexity == 0:
            return 100.0

        # Simplified calculation
        mi = 171 - 5.2 * math.log(halstead_volume + 1) - 0.23 * avg_complexity - 16.2 * math.log(lines)

        # Normalize to 0-100 scale
        mi = max(0, min(100, mi))

        return round(mi, 2)


class ComplexityReporter:
    """Generate complexity analysis reports"""

    def __init__(self, analyzer: ComplexityAnalyzer):
        self.analyzer = analyzer
        self.thresholds = {
            'cyclomatic_complexity': 10,
            'cognitive_complexity': 15,
            'method_lines': 50,
            'method_lines_critical': 100,
            'nesting_depth': 4,
            'parameter_count': 5,
            'maintainability_index_low': 20,
            'class_method_count': 20
        }

    def generate_report(self) -> str:
        """Generate comprehensive complexity report"""
        report = []

        report.append("=" * 80)
        report.append("CODE COMPLEXITY ANALYSIS REPORT")
        report.append("LionAGI QE Fleet - Recent Changes Analysis")
        report.append("=" * 80)
        report.append("")

        # Overall summary
        report.append(self._generate_summary())
        report.append("")

        # Files by complexity
        report.append(self._generate_file_ranking())
        report.append("")

        # Critical issues
        report.append(self._generate_critical_issues())
        report.append("")

        # Detailed metrics
        report.append(self._generate_detailed_metrics())
        report.append("")

        # Refactoring recommendations
        report.append(self._generate_recommendations())
        report.append("")

        # Code quality trends
        report.append(self._generate_trends())

        return "\n".join(report)

    def _generate_summary(self) -> str:
        """Generate overall summary"""
        total_files = len(self.analyzer.file_metrics)
        total_lines = sum(f.lines for f in self.analyzer.file_metrics)
        total_methods = sum(f.method_count for f in self.analyzer.file_metrics)
        avg_complexity = sum(f.avg_complexity for f in self.analyzer.file_metrics) / total_files if total_files > 0 else 0
        avg_mi = sum(f.maintainability_index for f in self.analyzer.file_metrics) / total_files if total_files > 0 else 0

        # Calculate overall complexity score (0-100, lower is better)
        complexity_score = 100 - min(100, (avg_complexity / 20) * 100)

        lines = [
            "OVERALL COMPLEXITY SCORE: {:.1f}/100".format(complexity_score),
            "  (100 = low complexity, excellent maintainability)",
            "",
            "Summary Statistics:",
            f"  Files Analyzed: {total_files}",
            f"  Total Lines: {total_lines:,}",
            f"  Total Methods/Functions: {total_methods}",
            f"  Average Cyclomatic Complexity: {avg_complexity:.2f}",
            f"  Average Maintainability Index: {avg_mi:.2f}",
        ]

        # Quality grade
        if complexity_score >= 80:
            grade = "A (Excellent)"
        elif complexity_score >= 70:
            grade = "B (Good)"
        elif complexity_score >= 60:
            grade = "C (Fair)"
        elif complexity_score >= 50:
            grade = "D (Poor)"
        else:
            grade = "F (Critical)"

        lines.append(f"  Quality Grade: {grade}")

        return "\n".join(lines)

    def _generate_file_ranking(self) -> str:
        """Generate ranked list of files by complexity"""
        lines = ["FILES RANKED BY COMPLEXITY:"]
        lines.append("-" * 80)

        # Sort by complexity
        sorted_files = sorted(
            self.analyzer.file_metrics,
            key=lambda f: f.avg_complexity,
            reverse=True
        )

        for i, file_metrics in enumerate(sorted_files, 1):
            file_name = Path(file_metrics.file_path).name
            lines.append(
                f"{i}. {file_name:40s} "
                f"LOC: {file_metrics.lines:4d} | "
                f"Methods: {file_metrics.method_count:3d} | "
                f"Avg Complexity: {file_metrics.avg_complexity:5.2f} | "
                f"MI: {file_metrics.maintainability_index:5.2f}"
            )

        return "\n".join(lines)

    def _generate_critical_issues(self) -> str:
        """Generate list of critical issues requiring immediate attention"""
        lines = ["CRITICAL ISSUES (Require Immediate Refactoring):"]
        lines.append("-" * 80)

        issues = []

        for file_metrics in self.analyzer.file_metrics:
            file_name = Path(file_metrics.file_path).name

            # Check all functions
            for func in file_metrics.functions:
                self._check_method_issues(func, file_name, issues)

            # Check class methods
            for cls in file_metrics.classes:
                for method in cls.methods:
                    self._check_method_issues(method, f"{file_name}::{cls.name}", issues)

        if not issues:
            lines.append("  No critical issues found!")
        else:
            # Sort by severity
            issues.sort(key=lambda x: x[0], reverse=True)

            for severity, issue in issues:
                lines.append(f"  [{severity}] {issue}")

        return "\n".join(lines)

    def _check_method_issues(self, method: MethodMetrics, location: str, issues: List[Tuple[str, str]]):
        """Check a method for complexity issues"""
        if method.cyclomatic_complexity > 15:
            issues.append((
                "CRITICAL",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Cyclomatic complexity = {method.cyclomatic_complexity} (threshold: 10)"
            ))
        elif method.cyclomatic_complexity > self.thresholds['cyclomatic_complexity']:
            issues.append((
                "HIGH",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Cyclomatic complexity = {method.cyclomatic_complexity} (threshold: 10)"
            ))

        if method.cognitive_complexity > 20:
            issues.append((
                "CRITICAL",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Cognitive complexity = {method.cognitive_complexity} (threshold: 15)"
            ))
        elif method.cognitive_complexity > self.thresholds['cognitive_complexity']:
            issues.append((
                "HIGH",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Cognitive complexity = {method.cognitive_complexity} (threshold: 15)"
            ))

        if method.lines > self.thresholds['method_lines_critical']:
            issues.append((
                "CRITICAL",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Method length = {method.lines} lines (threshold: 100)"
            ))
        elif method.lines > self.thresholds['method_lines']:
            issues.append((
                "MEDIUM",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Method length = {method.lines} lines (threshold: 50)"
            ))

        if method.nesting_depth > self.thresholds['nesting_depth']:
            issues.append((
                "HIGH",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Deep nesting = {method.nesting_depth} levels (threshold: 4)"
            ))

        if method.parameter_count > self.thresholds['parameter_count']:
            issues.append((
                "MEDIUM",
                f"{location}::{method.name} (line {method.line_start}): "
                f"Long parameter list = {method.parameter_count} params (threshold: 5)"
            ))

    def _generate_detailed_metrics(self) -> str:
        """Generate detailed per-file metrics"""
        lines = ["DETAILED METRICS BY FILE:"]
        lines.append("=" * 80)

        for file_metrics in self.analyzer.file_metrics:
            lines.append("")
            lines.append(f"File: {file_metrics.file_path}")
            lines.append(f"  Lines: {file_metrics.lines}")
            lines.append(f"  Maintainability Index: {file_metrics.maintainability_index:.2f}")
            lines.append(f"  Total Complexity: {file_metrics.total_complexity}")
            lines.append(f"  Average Complexity: {file_metrics.avg_complexity:.2f}")
            lines.append("")

            # Top complex functions
            all_methods = file_metrics.functions[:]
            for cls in file_metrics.classes:
                all_methods.extend(cls.methods)

            all_methods.sort(key=lambda m: m.complexity_score, reverse=True)

            if all_methods:
                lines.append("  Top Complex Methods:")
                for method in all_methods[:5]:  # Top 5
                    lines.append(
                        f"    - {method.name} (line {method.line_start}): "
                        f"CC={method.cyclomatic_complexity}, "
                        f"CogC={method.cognitive_complexity}, "
                        f"Lines={method.lines}, "
                        f"Nesting={method.nesting_depth}"
                    )

        return "\n".join(lines)

    def _generate_recommendations(self) -> str:
        """Generate refactoring recommendations"""
        lines = ["REFACTORING RECOMMENDATIONS:"]
        lines.append("-" * 80)

        recommendations = []

        for file_metrics in self.analyzer.file_metrics:
            file_name = Path(file_metrics.file_path).name

            # Check maintainability index
            if file_metrics.maintainability_index < self.thresholds['maintainability_index_low']:
                recommendations.append(
                    f"1. {file_name}: Low maintainability (MI={file_metrics.maintainability_index:.2f})"
                )
                recommendations.append(
                    "   Recommendation: Break down complex methods, reduce nesting, improve naming"
                )

            # Check for god classes
            for cls in file_metrics.classes:
                if cls.method_count > self.thresholds['class_method_count']:
                    recommendations.append(
                        f"2. {file_name}::{cls.name}: God class detected ({cls.method_count} methods)"
                    )
                    recommendations.append(
                        "   Recommendation: Apply Single Responsibility Principle, extract related methods into separate classes"
                    )

        # General recommendations based on patterns
        avg_complexity = sum(f.avg_complexity for f in self.analyzer.file_metrics) / len(self.analyzer.file_metrics)
        if avg_complexity > 10:
            recommendations.append("")
            recommendations.append("3. General: High average complexity across codebase")
            recommendations.append("   Recommendation: Apply Extract Method pattern to break down complex logic")

        if not recommendations:
            recommendations.append("  All files meet complexity thresholds. Great work!")

        return "\n".join(recommendations)

    def _generate_trends(self) -> str:
        """Generate code quality trends"""
        lines = ["CODE QUALITY TRENDS:"]
        lines.append("-" * 80)

        # Calculate baseline metrics
        total_methods = sum(f.method_count for f in self.analyzer.file_metrics)
        complex_methods = 0
        very_complex_methods = 0

        for file_metrics in self.analyzer.file_metrics:
            all_methods = file_metrics.functions[:]
            for cls in file_metrics.classes:
                all_methods.extend(cls.methods)

            for method in all_methods:
                if method.cyclomatic_complexity > 10:
                    complex_methods += 1
                if method.cyclomatic_complexity > 15:
                    very_complex_methods += 1

        lines.append(f"  Total Methods: {total_methods}")
        lines.append(f"  Complex Methods (CC > 10): {complex_methods} ({complex_methods/total_methods*100:.1f}%)")
        lines.append(f"  Very Complex Methods (CC > 15): {very_complex_methods} ({very_complex_methods/total_methods*100:.1f}%)")
        lines.append("")
        lines.append("  Complexity Distribution:")

        # Complexity distribution
        complexity_buckets = defaultdict(int)
        for file_metrics in self.analyzer.file_metrics:
            all_methods = file_metrics.functions[:]
            for cls in file_metrics.classes:
                all_methods.extend(cls.methods)

            for method in all_methods:
                if method.cyclomatic_complexity <= 5:
                    complexity_buckets['Low (1-5)'] += 1
                elif method.cyclomatic_complexity <= 10:
                    complexity_buckets['Medium (6-10)'] += 1
                elif method.cyclomatic_complexity <= 15:
                    complexity_buckets['High (11-15)'] += 1
                else:
                    complexity_buckets['Critical (>15)'] += 1

        for bucket, count in sorted(complexity_buckets.items()):
            pct = count / total_methods * 100 if total_methods > 0 else 0
            bar = '#' * int(pct / 2)
            lines.append(f"    {bucket:20s}: {bar:30s} {count:3d} ({pct:5.1f}%)")

        return "\n".join(lines)


def main():
    """Main entry point"""
    # Files to analyze
    files_to_analyze = [
        "src/lionagi_qe/core/orchestrator.py",
        "src/lionagi_qe/core/base_agent.py",
        "src/lionagi_qe/core/hooks.py",
        "src/lionagi_qe/agents/test_executor.py",
        "src/lionagi_qe/agents/flaky_test_hunter.py",
        "src/lionagi_qe/agents/test_generator.py",
        "src/lionagi_qe/tools/code_analyzer.py"
    ]

    print("Starting code complexity analysis...")
    print(f"Analyzing {len(files_to_analyze)} files...\n")

    analyzer = ComplexityAnalyzer()

    for file_path in files_to_analyze:
        path = Path(file_path)
        if path.exists():
            print(f"  Analyzing: {path.name}")
            analyzer.analyze_file(path)
        else:
            print(f"  Warning: {path} not found")

    print("\nGenerating report...\n")

    reporter = ComplexityReporter(analyzer)
    report = reporter.generate_report()

    print(report)

    # Save to file
    output_file = Path("complexity_analysis_report.txt")
    with open(output_file, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
