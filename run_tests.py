#!/usr/bin/env python3
"""
Simple test runner for PDF consistency tests.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --baseline-only    # Generate baselines only
    python run_tests.py --quick            # Run quick subset of tests
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Main test runner function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF Consistency Test Runner")
    parser.add_argument("--baseline-only", action="store_true",
                       help="Only generate baseline PDFs")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick subset of tests")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Check if test directory exists
    tests_dir = project_dir / "tests"
    if not tests_dir.exists():
        print("Error: Tests directory not found!")
        return 1
    
    print("CIT0001 PDF Consistency Test Runner")
    print("=" * 40)
    
    try:
        if args.baseline_only:
            print("Generating baseline PDFs...")
            result = subprocess.run([
                sys.executable, "tests/test_pdf_consistency.py", "--generate-baselines"
            ], check=True)
            print("✅ Baseline PDFs generated successfully!")
            return 0
        
        # Check if baselines exist
        baseline_dir = tests_dir / "baseline_pdfs"
        if not baseline_dir.exists() or not any(baseline_dir.glob("baseline_*.pdf")):
            print("📋 No baseline PDFs found. Generating them first...")
            subprocess.run([
                sys.executable, "tests/test_pdf_consistency.py", "--generate-baselines"
            ], check=True)
            print("✅ Baseline PDFs generated!")
        
        # Run tests
        print("\n🧪 Running PDF consistency tests...")
        test_args = [sys.executable, "tests/test_pdf_consistency.py", "--run-tests"]
        
        if args.verbose:
            test_args.append("-v")
        
        result = subprocess.run(test_args, check=True)
        
        print("\n✅ All tests completed successfully!")
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return e.returncode
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())