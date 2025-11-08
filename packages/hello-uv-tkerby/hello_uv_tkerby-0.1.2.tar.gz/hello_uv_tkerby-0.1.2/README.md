# hello-uv-tkerby2

A tiny demo package for teaching Python packaging concepts.

## Description

This package demonstrates the basics of creating a Python package with:
- Basic functions (`add_one`)
- Functions with dependencies (`calculate_mean` using numpy)
- Proper project structure with tests
- Modern packaging with `uv`

## Installation

```bash
pip install hello-uv-tkerby2
```

## Usage

```python
from hello_uv_tkerby2 import add_one, calculate_mean

# Add one to a number
result = add_one(5)
print(result)  # Output: 6

# Calculate mean of a list
mean = calculate_mean([1, 2, 3, 4, 5])
print(mean)  # Output: 3.0
```

## Features

- Simple arithmetic operations
- Statistical calculations using numpy
- Well-tested with pytest
- Type hints and documentation

## Dependencies

- Python >= 3.13
- numpy >= 1.26.0
- pandas >= 2.3.3

## License

MIT
