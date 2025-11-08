.PHONY: test clean build publish install dev lint

# Default target
all: lint test build

# Run tests
test:
	uv run pytest

# Clean build artifacts
clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/

# Build package
build: clean
	uv build

# Publish to PyPI (requires PYPI_TOKEN environment variable)
publish: build
	uv publish --token ${PYPI_TOKEN}

# Install the package locally for development
dev:
	uv pip install -e ".[dev]"

# Install the package from the built distribution
install: build
	uv pip install dist/*.whl

# Create a version tag and push it
release:
	@if [ -z "$(VERSION)" ]; then echo "VERSION is required. Use: make release VERSION=x.y.z"; exit 1; fi
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	git push origin v$(VERSION)

# Bump version using UV
bump:
	@if [ -z "$(VERSION)" ]; then echo "VERSION is required. Use: make bump VERSION=x.y.z"; exit 1; fi
	uv project bump $(VERSION)

lint:
	uv run pylint masto_mailo_inator

help:
	@echo "Available targets:"
	@echo "  test      - Run tests with UV"
	@echo "  lint      - Run pylint on the code"
	@echo "  clean     - Remove build artifacts"
	@echo "  build     - Build the package with UV"
	@echo "  publish   - Upload to PyPI using UV (requires PYPI_TOKEN env var)"
	@echo "  dev       - Install package in development mode using UV"
	@echo "  install   - Install the package locally using UV"
	@echo "  bump      - Bump package version using UV (requires VERSION=x.y.z)"
	@echo "  release   - Tag a new version (requires VERSION=x.y.z)"
	@echo "  help      - Show this help message"
