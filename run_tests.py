#!/usr/bin/env python3
"""
Test runner for MB Secure website tests.
Starts a local server, runs pytest with Playwright, and generates reports.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --update-snapshots # Update visual regression baselines
    python run_tests.py --headed           # Run with visible browser
    python run_tests.py --browser chromium # Run with specific browser
    python run_tests.py -k "test_static"   # Run specific tests
"""
import argparse
import subprocess
import sys
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Run MB Secure website tests with Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_tests.py                           Run all tests (headless, all browsers)
    python run_tests.py --update-snapshots        Update visual regression baselines
    python run_tests.py --headed                  Run with visible browser window
    python run_tests.py --browser chromium        Run only in Chromium
    python run_tests.py -k "test_homepage"        Run tests matching pattern
    python run_tests.py --static-only             Run only static tests (no browser)
    python run_tests.py -v                        Verbose output
        """
    )
    
    parser.add_argument(
        "--update-snapshots",
        action="store_true",
        help="Update visual regression baseline screenshots"
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browsers in headed mode (visible window)"
    )
    parser.add_argument(
        "--browser",
        choices=["chromium", "firefox", "webkit", "all"],
        default="all",
        help="Browser(s) to run tests in (default: all)"
    )
    parser.add_argument(
        "-k",
        "--keyword",
        type=str,
        help="Only run tests matching the given keyword expression"
    )
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Run only static tests (no browser needed)"
    )
    parser.add_argument(
        "--visual-only",
        action="store_true",
        help="Run only visual regression tests"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--html-report",
        type=str,
        default="test-results/report.html",
        help="Path for HTML report (default: test-results/report.html)"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip HTML report generation"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    # Create test-results directory early
    test_results_dir = project_root / "test-results"
    test_results_dir.mkdir(parents=True, exist_ok=True)
    
    if args.static_only:
        cmd.append(str(tests_dir / "test_static.py"))
    elif args.visual_only:
        cmd.append(str(tests_dir / "test_visual.py"))
    else:
        cmd.append(str(tests_dir))
    
    # Browser selection
    if not args.static_only:
        if args.browser == "all":
            cmd.extend(["--browser", "chromium", "--browser", "firefox", "--browser", "webkit"])
        else:
            cmd.extend(["--browser", args.browser])
    
    # Headed mode
    if args.headed:
        cmd.append("--headed")
    
    # Update snapshots
    if args.update_snapshots:
        cmd.append("--update-snapshots")
    
    # Keyword filter
    if args.keyword:
        cmd.extend(["-k", args.keyword])
    
    # Update snapshots - use environment variable for Playwright
    env = os.environ.copy()
    if args.update_snapshots:
        env["PLAYWRIGHT_UPDATE_SNAPSHOTS"] = "1"
    
    # Verbose
    if args.verbose:
        cmd.append("-v")
    
    # HTML report (may have issues with Python 3.14, falls back gracefully)
    if not args.no_report:
        report_path = project_root / args.html_report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        # Try using pytest-html, but it may fail on some Python versions
        cmd.extend(["--html", str(report_path), "--self-contained-html"])
        # Also add JUnit XML for CI compatibility
        junit_path = report_path.parent / "junit.xml"
        cmd.extend(["--junit-xml", str(junit_path)])
    
    # Add color output
    cmd.append("--color=yes")
    
    # Print command being run
    print("=" * 60)
    print("MB Secure Website Test Runner")
    print("=" * 60)
    print(f"\nRunning command:\n  {' '.join(cmd)}\n")
    print("=" * 60)
    
    # Run pytest
    try:
        result = subprocess.run(cmd, cwd=project_root, env=env)
        
        print("\n" + "=" * 60)
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"❌ Some tests failed (exit code: {result.returncode})")
        
        if not args.no_report:
            print(f"\n📊 HTML report: {args.html_report}")
        
        if args.update_snapshots:
            print("\n📸 Visual snapshots updated in: tests/test_visual-snapshots/")
        
        print("=" * 60)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
