# sbenchmark-dependency-test-one

Minimal library exposing three functions:

- `name() -> str`
- `version_number() -> str`
- `version() -> str`

## Usage

```python
from sbenchmark_dependency_test_one import name, version_number, version

print(name())          # "io.github.sbenchmark:python-dependency-1"
print(version_number()) # "1.0.2"
print(version())       # "io.github.sbenchmark:python-dependency-1,1.0.2"
