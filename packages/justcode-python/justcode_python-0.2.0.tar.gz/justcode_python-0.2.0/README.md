# justcode-python

Python bindings for the justcode binary encoder/decoder library.

## Installation

```bash
pip install justcode-python
```

## Usage

```python
import justcode_python

# Create a configuration
config = justcode_python.PyConfig.standard()

# Encode data
encoded = justcode_python.encode("Hello, world!", "string", config)

# Decode data
decoded = justcode_python.decode(encoded, "string", config)
```

## Development

Build the package:

```bash
maturin develop
```

Run tests:

```bash
pytest tests/test_justcode_python.py -v
```

