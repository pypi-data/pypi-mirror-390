# Project Structure

```
purreal/
├── purreal/                    # Main package
│   ├── __init__.py            # Package exports
│   ├── pooler.py              # Connection pool implementation
│   └── shutdown.py            # Graceful shutdown utilities
│
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration
│   ├── test_pooler.py         # Pool unit tests
│   └── test_connectivity.py   # Integration tests
│
├── benchmarks/                 # Performance benchmarks
│   ├── __init__.py
│   ├── README.md
│   ├── high_throughput.py     # Sustained load, burst, churn tests
│   └── benchmark_configs.py   # Configuration comparison
│
├── examples/                   # Usage examples
│   ├── __init__.py
│   ├── README.md
│   ├── stress_test.py         # Simple stress test
│   ├── monitor_pool.py        # Real-time monitoring
│   └── load_test.py           # Comprehensive load test
│
├── test.bat                    # Windows test runner
├── test.sh                     # Unix test runner
├── pytest.ini                  # Pytest configuration
├── pyproject.toml             # Package metadata
├── LICENSE                     # GPL-3.0 license
├── README.md                   # Main documentation
└── PERFORMANCE_TESTING.md     # Performance guide
```

## Directory Purpose

### `purreal/`
Core package code. **Production-ready** connection pool implementation.

**Import:**
```python
from purreal import SurrealDBConnectionPool
```

### `tests/`
Unit and integration tests using pytest. **Required for CI/CD**.

**Run:**
```bash
pytest tests/
# or
./test.bat connectivity
```

### `benchmarks/`
Performance validation under high-throughput conditions. **Use before production deployment**.

**Run:**
```bash
python benchmarks/high_throughput.py
# or
./test.bat throughput
```

### `examples/`
Reference implementations and usage patterns. **Start here for learning**.

**Run:**
```bash
python examples/stress_test.py 500
# or
./test.bat stress
```

## Key Files

- **`purreal/pooler.py`**: Main connection pool (918 lines, production-ready)
- **`tests/test_pooler.py`**: Comprehensive unit tests
- **`benchmarks/high_throughput.py`**: Performance validation
- **`README.md`**: API documentation and usage guide
- **`PERFORMANCE_TESTING.md`**: Tuning and monitoring guide

## Test Runner

```bash
# Windows
./test.bat [connectivity|stress|monitor|benchmark|throughput|load|all]

# Linux/Mac
./test.sh [connectivity|stress|monitor|benchmark|throughput|load|all]
```

## Development Workflow

1. **Make changes** to `purreal/pooler.py`
2. **Run unit tests**: `pytest tests/test_pooler.py`
3. **Run connectivity test**: `./test.bat connectivity`
4. **Validate performance**: `./test.bat throughput`
5. **Check examples still work**: `./test.bat stress`

## CI/CD Integration

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pytest tests/
    python tests/test_connectivity.py
```

## Installation

```bash
# Development mode
pip install -e .

# Production
pip install purreal
```

## Packaging

```bash
# Build
python -m build

# Publish
python -m twine upload dist/*
```
