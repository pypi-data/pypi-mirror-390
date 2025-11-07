# justcode-python

Python bindings for the justcode binary encoder/decoder library.

## Installation

```bash
pip install justcode-python
```

## Usage

```python
import justcode

# Encode data (config is optional, uses defaults)
encoded = justcode.encode("Hello, world!")

# Decode data (target_type is optional - auto-detects type)
decoded = justcode.decode(encoded)
assert decoded == "Hello, world!"

# Or specify target type explicitly
decoded = justcode.decode(encoded, target_type="str")
assert decoded == "Hello, world!"
```

### Advanced Usage

```python
import justcode

# Create a custom configuration
config = justcode.PyConfig(size_limit=1024, variable_int_encoding=False)

# Encode with custom config
encoded = justcode.encode(42, config=config)

# Decode with custom config (auto-detects type)
decoded = justcode.decode(encoded, config=config)
assert decoded == 42

# Or specify target type explicitly
decoded = justcode.decode(encoded, config=config, target_type="int")
assert decoded == 42
```

### Configuration

```python
import justcode

# Standard configuration (default)
config = justcode.PyConfig.standard()

# Custom configuration with size limit
config = justcode.PyConfig(size_limit=1024)

# Custom configuration without variable int encoding
config = justcode.PyConfig(variable_int_encoding=False)

# Chain configuration methods
config = justcode.PyConfig.standard().with_limit(2048).with_variable_int_encoding(False)
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
