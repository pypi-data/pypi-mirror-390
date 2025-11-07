# sbenchmark-dependency-test-two

Minimal library exposing four functions:

Functions:
- `name() -> str`
- `version_number() -> str`
- `version() -> str`
- `dependency() -> str` (delegates to `sbenchmark-dependency-test-one.version()`)

## Usage

```python
from sbenchmark_dependency_test_two import name, version_number, version, dependency

print(name())           # "io.github.sbenchmark:python-dependency-2"
print(version_number()) # "1.0.1"
print(version())        # "io.github.sbenchmark:python-dependency-2,1.0.1"
print(dependency())     # "io.github.sbenchmark:python-dependency-1,1.0.2"
