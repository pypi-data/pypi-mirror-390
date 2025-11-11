# juice-json-schemas

[![PyPI](https://img.shields.io/pypi/v/juice-json-schemas?style=flat-square)](https://pypi.python.org/pypi/juice-json-schemas/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/juice-json-schemas?style=flat-square)](https://pypi.python.org/pypi/juice-json-schemas/)
[![PyPI - License](https://img.shields.io/pypi/l/juice-json-schemas?style=flat-square)](https://pypi.python.org/pypi/juice-json-schemas/)


---

**Documentation**: [https://juice-soc.io.esa.int/juice-uplink/spm/juice-json-schemas/](https://juice-soc.io.esa.int/juice-uplink/spm/juice-json-schemas/)

**Source Code**: [https://gitlab.esa.int/juice-soc/juice-uplink/spm/juice-json-schemas.git](https://gitlab.esa.int/juice-soc/juice-uplink/spm/juice-json-schemas.git)

**PyPI**: [https://pypi.org/project/juice-json-schemas/](https://pypi.org/project/juice-json-schemas/)

---

Library and utilities for validating JSON files against [JUICE mission](https://www.cosmos.esa.int/web/juice) data schemas or custom JSON Schemas.

## Installation

```sh
pip install juice-json-schemas
```

## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.9+
* Create a virtual environment and install the dependencies

```sh
poetry install
```

* Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](https://github.com//juice-json-schemas/tree/master/docs) and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Gitlab Pages page](https://pages.github.com/) automatically as part each release.

### Pre-commit

Pre-commit hooks run all the auto-formatting (`ruff format`), linters (e.g. `ruff`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```

---
