.PHONY: all validate test clean

all: validate

validate:
	@echo "Validating all Python scripts..."
	@find . -name "*.py" -not -path "./.venv/*" -exec python3 -m py_compile {} \; -print
	@echo "All Python scripts passed validation."

test:
	@echo "Running smoke tests..."
	@mkdir -p output
	@echo "Smoke tests placeholder complete."

clean:
	rm -rf output/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
