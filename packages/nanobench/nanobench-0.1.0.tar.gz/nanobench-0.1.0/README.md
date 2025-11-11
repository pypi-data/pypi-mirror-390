# nanobench

A simple Python package that prints "hello world".

## Installation

You can install nanobench from PyPI:

```bash
pip install nanobench
```

## Usage

### As a Python module

```python
from nanobench import hello

hello()
```

### As a command-line tool

```bash
nanobench
```

Both will output: `hello world`

## Development

To install in development mode:

```bash
pip install -e .
```

## Publishing to PyPI

1. Build the package:
   ```bash
   pip install build
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   pip install twine
   twine upload dist/*
   ```

## License

MIT
