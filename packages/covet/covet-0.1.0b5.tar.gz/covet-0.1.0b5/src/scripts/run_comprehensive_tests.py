#!/usr/bin/env python3
"""
Comprehensive Test Runner for CovetPy Framework

This script runs the complete test suite with coverage analysis, performance
benchmarks, security scans, and generates detailed reports. It validates
all functionality against real backends to ensure production readiness.

Usage:
    python scripts/run_comprehensive_tests.py [options]

Options:
    --fast          Run only fast tests (skip performance and stress tests)
    --security      Run only security tests
    --performance   Run only performance tests
    --coverage      Run with coverage analysis
    --parallel      Run tests in parallel
    --real-backend  Use real backend services (default)
    --mock-backend  Use mocked backends (for CI environments)
    --report        Generate comprehensive HTML report
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Comprehensive test runner for CovetPy framework."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.results = {}
        self.start_time = None
        self.end_time = None

    def run_tests(
        self,
        test_categories: list[str],
        parallel: bool = True,
        coverage: bool = True,
        real_backend: bool = True,
        generate_report: bool = True,
    ) -> dict[str, any]:
        """Run comprehensive test suite."""

        print("🧪 CovetPy Comprehensive Test Suite")
        print("=" * 50)

        self.start_time = time.time()

        # Setup test environment
        self._setup_test_environment(real_backend)

        # Run test categories
        for category in test_categories:
            print(f"\n📋 Running {category} tests...")
            result = self._run_test_category(category, parallel, coverage, real_backend)
            self.results[category] = result

            if not result["success"]:
                print(f"❌ {category} tests failed!")
                break
            else:
                print(f"✅ {category} tests passed!")

        self.end_time = time.time()

        # Generate reports
        if generate_report:
            self._generate_comprehensive_report()

        # Print summary
        self._print_summary()

        return self.results

    def _setup_test_environment(self, real_backend: bool):
        """Setup test environment and dependencies."""
        print("🔧 Setting up test environment...")

        # Set environment variables
        env_vars = {
            "COVET_TESTING": "true",
            "COVET_LOG_LEVEL": "WARNING",
            "COVET_DATABASE_URL": (
                "postgresql://test_user:test_password@localhost/covet_test"
                if real_backend
                else "sqlite:///test.db"
            ),
            "COVET_REDIS_URL": (
                "redis://localhost:6379/1" if real_backend else "memory://localhost"
            ),
            "COVET_CLEANUP_TESTS": "true",
            "PYTEST_FAST_ONLY": "false",
        }

        for key, value in env_vars.items():
            os.environ[key] = value

        # Ensure test directories exist
        test_dirs = ["tests/reports", "coverage", "logs"]

        for test_dir in test_dirs:
            (self.project_root / test_dir).mkdir(parents=True, exist_ok=True)

        # Check dependencies
        self._check_test_dependencies(real_backend)

    def _check_test_dependencies(self, real_backend: bool):
        """Check that required test dependencies are available."""
        required_packages = [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-html",
            "pytest-timeout",
            "pytest-mock",
        ]

        if real_backend:
            required_packages.extend(["asyncpg", "redis", "httpx"])

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            sys.exit(1)

        print("✅ All test dependencies available")

    def _run_test_category(
        self, category: str, parallel: bool, coverage: bool, real_backend: bool
    ) -> dict[str, any]:
        """Run a specific test category."""

        # Define test paths for each category
        test_paths = {
            "unit": ["tests/unit/", "covet/testing/test_*.py"],
            "integration": [
                "tests/integration/",
                "covet/database/tests/",
            ],
            "security": ["tests/security/", "covet/security/tests/"],
            "performance": ["tests/performance/"],
            "api": ["covet/api/tests/", "covet/websocket/tests/"],
            "all": ["tests/", "covet/*/tests/"],
        }

        if category not in test_paths:
            return {"success": False, "error": f"Unknown test category: {category}"}

        # Build pytest command
        cmd = ["python", "-m", "pytest"]

        # Add test paths
        for path in test_paths[category]:
            if (self.project_root / path).exists():
                cmd.append(str(path))

        # Add pytest options
        pytest_args = [
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            f"--junitxml=tests/reports/junit_{category}.xml",  # JUnit XML
        ]

        # Coverage options
        if coverage:
            pytest_args.extend(
                [
                    "--cov=covet",
                    f"--cov-report=html:coverage/html_{category}",
                    f"--cov-report=json:coverage/coverage_{category}.json",
                    "--cov-report=term-missing",
                ]
            )

        # Parallel execution
        if (
            parallel and category != "performance"
        ):  # Don't parallelize performance tests
            pytest_args.extend(["-n", "auto"])

        # Category-specific options
        if category == "security":
            pytest_args.extend(
                [
                    "-m",
                    "security",
                    "--timeout=300",  # 5 minute timeout for security tests
                ]
            )
        elif category == "performance":
            pytest_args.extend(
                [
                    "-m",
                    "performance",
                    "--timeout=600",  # 10 minute timeout for performance tests
                    "-s",  # Don't capture output for performance tests
                ]
            )
        elif category == "integration":
            pytest_args.extend(["-m", "integration", "--timeout=300"])
        elif category == "unit":
            pytest_args.extend(["-m", "unit", "--timeout=60"])

        # Backend selection
        if real_backend:
            pytest_args.extend(["-m", "not mock_safe or real_backend"])
        else:
            pytest_args.extend(["-m", "mock_safe"])

        cmd.extend(pytest_args)

        print(f"Running: {' '.join(cmd)}")

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minute overall timeout
            )

            end_time = time.time()
            duration = end_time - start_time

            return {
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test execution timed out",
                "duration": 1800,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration": time.time() - start_time,
            }

    def _generate_comprehensive_report(self):
        """Generate comprehensive test report."""
        print("\n📊 Generating comprehensive test report...")

        report_data = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": self.end_time - self.start_time,
                "categories_tested": list(self.results.keys()),
            },
            "results": self.results,
            "coverage": self._collect_coverage_data(),
            "performance": self._collect_performance_data(),
            "security": self._collect_security_data(),
            "summary": self._generate_summary(),
        }

        # Save JSON report
        report_path = self.project_root / "tests/reports/comprehensive_report.json"
        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2, default=str)

        # Generate HTML report
        html_report = self._generate_html_report(report_data)
        html_path = self.project_root / "tests/reports/comprehensive_report.html"
        with open(html_path, "w") as f:
            f.write(html_report)

        print("✅ Reports generated:")
        print(f"  📄 JSON: {report_path}")
        print(f"  🌐 HTML: {html_path}")

    def _collect_coverage_data(self) -> dict[str, any]:
        """Collect coverage data from all test runs."""
        coverage_data = {}

        coverage_files = list((self.project_root / "coverage").glob("coverage_*.json"))

        for coverage_file in coverage_files:
            category = coverage_file.stem.replace("coverage_", "")

            try:
                with open(coverage_file) as f:
                    data = json.load(f)

                coverage_data[category] = {
                    "total_statements": data["totals"]["num_statements"],
                    "covered_statements": data["totals"]["covered_lines"],
                    "missing_statements": data["totals"]["missing_lines"],
                    "coverage_percentage": data["totals"]["percent_covered"],
                }

            except Exception as e:
                coverage_data[category] = {"error": str(e)}

        return coverage_data

    def _collect_performance_data(self) -> dict[str, any]:
        """Collect performance test data."""
        performance_data = {}

        # Look for performance test outputs
        perf_files = list((self.project_root / "tests/reports").glob("*performance*"))

        for perf_file in perf_files:
            try:
                with open(perf_file) as f:
                    if perf_file.suffix == ".json":
                        data = json.load(f)
                        performance_data[perf_file.stem] = data
            except Exception:
                pass

        return performance_data

    def _collect_security_data(self) -> dict[str, any]:
        """Collect security test data."""
        security_data = {}

        # Look for security test outputs
        security_files = list((self.project_root / "tests/reports").glob("*security*"))

        for security_file in security_files:
            try:
                with open(security_file) as f:
                    if security_file.suffix == ".json":
                        data = json.load(f)
                        security_data[security_file.stem] = data
            except Exception:
                pass

        return security_data

    def _generate_summary(self) -> dict[str, any]:
        """Generate test summary."""
        total_duration = self.end_time - self.start_time

        categories_passed = sum(
            1 for result in self.results.values() if result.get("success", False)
        )
        total_categories = len(self.results)

        return {
            "total_duration_seconds": total_duration,
            "categories_tested": total_categories,
            "categories_passed": categories_passed,
            "categories_failed": total_categories - categories_passed,
            "success_rate": (
                categories_passed / total_categories if total_categories > 0 else 0
            ),
            "overall_success": categories_passed == total_categories,
        }

    def _generate_html_report(self, report_data: dict) -> str:
        """Generate HTML report."""
        summary = report_data["summary"]

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CovetPy Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .success {{ color: green; font-weight: bold; }}
                .failure {{ color: red; font-weight: bold; }}
                .summary {{ margin: 20px 0; }}
                .category {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
                .category.passed {{ border-left: 5px solid green; }}
                .category.failed {{ border-left: 5px solid red; }}
                pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CovetPy Comprehensive Test Report</h1>
                <p>Generated: {report_data['test_run']['timestamp']}</p>
                <p>Duration: {summary['total_duration_seconds']:.1f} seconds</p>
            </div>

            <div class="summary">
                <h2>Summary</h2>
                <p class="{'success' if summary['overall_success'] else 'failure'}">
                    Overall Status: {'PASSED' if summary['overall_success'] else 'FAILED'}
                </p>
                <p>Categories Tested: {summary['categories_tested']}</p>
                <p>Categories Passed: {summary['categories_passed']}</p>
                <p>Categories Failed: {summary['categories_failed']}</p>
                <p>Success Rate: {summary['success_rate']:.1%}</p>
            </div>

            <div class="results">
                <h2>Test Results by Category</h2>
        """

        for category, result in report_data["results"].items():
            status_class = "passed" if result.get("success", False) else "failed"
            status_text = "PASSED" if result.get("success", False) else "FAILED"

            html += f"""
                <div class="category {status_class}">
                    <h3>{category.title()} Tests - {status_text}</h3>
                    <p>Duration: {result.get('duration', 0):.1f} seconds</p>
                    {f'<p>Error: {result["error"]}</p>' if "error" in result else ""}
                </div>
            """

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def _print_summary(self):
        """Print test execution summary."""
        print("\n" + "=" * 50)
        print("🎯 TEST EXECUTION SUMMARY")
        print("=" * 50)

        total_duration = self.end_time - self.start_time

        print(f"⏱️  Total Duration: {total_duration:.1f} seconds")
        print(f"📊 Categories Tested: {len(self.results)}")

        passed = 0
        failed = 0

        for category, result in self.results.items():
            if result.get("success", False):
                print(f"✅ {category}: PASSED ({result.get('duration', 0):.1f}s)")
                passed += 1
            else:
                print(f"❌ {category}: FAILED ({result.get('duration', 0):.1f}s)")
                if "error" in result:
                    print(f"   Error: {result['error']}")
                failed += 1

        print("\n" + "=" * 50)

        success_rate = passed / (passed + failed) if (passed + failed) > 0 else 0

        if success_rate == 1.0:
            print("🎉 ALL TESTS PASSED!")
        elif success_rate >= 0.8:
            print(f"⚠️  MOSTLY SUCCESSFUL ({success_rate:.1%} passed)")
        else:
            print(f"❌ TESTS FAILED ({success_rate:.1%} passed)")

        print("=" * 50)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CovetPy Comprehensive Test Runner")

    parser.add_argument("--fast", action="store_true", help="Run only fast tests")
    parser.add_argument(
        "--security", action="store_true", help="Run only security tests"
    )
    parser.add_argument(
        "--performance", action="store_true", help="Run only performance tests"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        default=True,
        help="Run with coverage analysis",
    )
    parser.add_argument(
        "--parallel", action="store_true", default=True, help="Run tests in parallel"
    )
    parser.add_argument(
        "--real-backend",
        action="store_true",
        default=True,
        help="Use real backend services",
    )
    parser.add_argument(
        "--mock-backend", action="store_true", help="Use mocked backends"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        default=True,
        help="Generate comprehensive HTML report",
    )

    args = parser.parse_args()

    # Determine test categories to run
    if args.security:
        test_categories = ["security"]
    elif args.performance:
        test_categories = ["performance"]
    elif args.fast:
        test_categories = ["unit"]
    else:
        test_categories = ["unit", "integration", "security", "performance"]

    # Determine backend type
    real_backend = args.real_backend and not args.mock_backend

    # Get project root
    project_root = Path(__file__).parent.parent

    # Run tests
    runner = TestRunner(str(project_root))

    results = runner.run_tests(
        test_categories=test_categories,
        parallel=args.parallel,
        coverage=args.coverage,
        real_backend=real_backend,
        generate_report=args.report,
    )

    # Exit with appropriate code
    overall_success = all(result.get("success", False) for result in results.values())
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
