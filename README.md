# ZAP junit converter

Convert OWASP ZAP JSON output to JUnit XML format.

## Installation

```shell
pip install zap-junit
```

## Usage

```bash
zap-junit input.json -o output.xml
```

## Testing

```bash
poetry run pytest -v
```

## Coverage Report

```bash
poetry run pytest --cov
```
