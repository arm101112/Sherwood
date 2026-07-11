.PHONY: install test lint typecheck backtest paper clean

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=src/sherwood --cov-report=term-missing

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

typecheck:
	mypy src/sherwood

backtest:
	python scripts/backtest.py --strategy $(STRATEGY) --start $(START) --end $(END)

paper:
	python scripts/paper.py --config config/default.yaml

live:
	python scripts/live.py --config config/default.yaml

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache dist build
