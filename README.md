# ZAP junit converter

![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue) [![Tests & Coverage](https://github.com/Digitalist-Open-Cloud/ZAP-JUnit-converter/actions/workflows/tests.yaml/badge.svg)](https://github.com/Digitalist-Open-Cloud/ZAP-JUnit-converter/actions/workflows/tests.yaml)
[![CodeQL](https://github.com/Digitalist-Open-Cloud/ZAP-JUnit-converter/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/Digitalist-Open-Cloud/ZAP-JUnit-converter/actions/workflows/github-code-scanning/codeql)
[![Bandit](https://github.com/Digitalist-Open-Cloud/ZAP-JUnit-converter/actions/workflows/bandit.yaml/badge.svg)](https://github.com/Digitalist-Open-Cloud/ZAP-JUnit-converter/actions/workflows/bandit.yaml)

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
