# Makefile for CIT0001 Grandparent Addendum Generator

# Python interpreter
PYTHON := python3

# Project directories
PROJECT_DIR := .
TESTS_DIR := tests
DOCS_DIR := documents

# Test targets
.PHONY: test test-baseline test-run test-clean check all clean help

# Default target
all: check

# Run all checks (linting, type checking, and tests)
check: test
	@echo "All checks completed successfully"

# Generate baseline PDFs and run tests
test: test-baseline test-run

# Generate baseline PDFs for comparison
test-baseline:
	@echo "Generating baseline PDFs for testing..."
	cd $(TESTS_DIR) && $(PYTHON) test_pdf_consistency.py --generate-baselines

# Run the test suite
test-run:
	@echo "Running PDF consistency tests..."
	cd $(TESTS_DIR) && $(PYTHON) test_pdf_consistency.py --run-tests

# Clean test artifacts
test-clean:
	@echo "Cleaning test artifacts..."
	rm -rf $(TESTS_DIR)/baseline_pdfs
	rm -rf $(TESTS_DIR)/temp_outputs
	rm -rf $(TESTS_DIR)/__pycache__
	find $(TESTS_DIR) -name "*.pyc" -delete

# Clean all generated files
clean: test-clean
	@echo "Cleaning all generated files..."
	rm -rf $(DOCS_DIR)/*.pdf
	rm -rf __pycache__
	find . -name "*.pyc" -delete

# Generate all production PDFs
generate:
	@echo "Generating all production PDFs..."
	$(PYTHON) generate_addendum.py

# Generate specific generation (usage: make generate-g4)
generate-g%:
	@echo "Generating G$* documents..."
	$(PYTHON) generate_addendum.py -g $*

# Install test dependencies
install-test-deps:
	@echo "Installing test dependencies..."
	pip install -r $(TESTS_DIR)/test_requirements.txt

# Show help
help:
	@echo "Available targets:"
	@echo "  test           - Generate baselines and run tests"
	@echo "  test-baseline  - Generate baseline PDFs for comparison"
	@echo "  test-run       - Run the test suite"
	@echo "  test-clean     - Clean test artifacts"
	@echo "  check          - Run all checks (same as test)"
	@echo "  generate       - Generate all production PDFs"
	@echo "  generate-gN    - Generate specific generation N (e.g., make generate-g4)"
	@echo "  clean          - Clean all generated files"
	@echo "  install-test-deps - Install test dependencies"
	@echo "  help           - Show this help message"