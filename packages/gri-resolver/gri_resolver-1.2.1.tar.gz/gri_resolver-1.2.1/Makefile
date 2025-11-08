.DEFAULT_GOAL := help

help:
	@echo "make venv           - create virtualenv (.venv)"
	@echo "make install        - install package in editable mode"
	@echo "make lint           - run flake8 linter"
	@echo "make test           - run tests with pytest"
	@echo "make build          - build sdist and wheel"
	@echo "make clean          - remove build artifacts and cache files"
	@echo "make clean-all      - clean + remove user data (cache, outputs)"
	@echo "make publish-test   - upload to TestPyPI"
	@echo "make publish        - upload to PyPI"
	@echo "make publish-gael   - upload to custom 'gael' repo from ~/.pypirc"
	@echo "make version        - show version derived from git tags (setuptools_scm)"

venv:
	python3 -m venv .venv
	. .venv/bin/activate; python -m pip install -U pip build twine

install:
	. .venv/bin/activate; python -m pip install -e .

lint:
	. .venv/bin/activate; python -m pip install -q flake8; flake8 gri_resolver --max-line-length=120

test:
	. .venv/bin/activate; python -m pip install -q pytest pytest-cov; pytest -q --cov=gri_resolver --cov-report=term-missing

build:
	. .venv/bin/activate; python -m build

publish-test:
	. .venv/bin/activate; python -m twine upload --repository testpypi dist/*

publish:
	. .venv/bin/activate; python -m twine upload dist/*

publish-gael:
	. .venv/bin/activate; python -m twine upload --repository gael dist/*

version:
	. .venv/bin/activate; python -c 'from setuptools_scm import get_version; print(get_version())'

clean:
	@echo "Cleaning build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .eggs/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.so" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "Clean complete."

clean-all: clean
	@echo "Cleaning user data (cache and outputs)..."
	rm -rf gri_resolver/cache/
	rm -rf gri_resolver/outputs/
	rm -rf cache/
	rm -rf outputs/
	@echo "Clean-all complete."

