# jyablonski Common Modules

![Tests](https://github.com/jyablonski/jyablonski_common_modules/actions/workflows/ci_cd.yml/badge.svg) [![Coverage Status](https://coveralls.io/repos/github/jyablonski/jyablonski_common_modules/badge.svg?branch=master)](https://coveralls.io/github/jyablonski/jyablonski_common_modules?branch=master)

Version: 0.0.11

Utility Repo w/ functions and tools for data engineering, cloud infrastructure, and development workflows. Includes helpers for:

- PostgreSQL Connections + Upsert Functions
- General Python Functions
- Standard Logging & optional Opensearch Logging Functions
- AWS Helper Functions (S3, Secrets Manager, SSM)
- AWS S3 Parquet Operations (optional)

## Testing

To run tests, run `make test`

## Install

```bash
# Basic installation
uv add jyablonski_common_modules

# With Opensearch logging support
uv add jyablonski_common_modules --extra es-logging

# With S3 parquet support (includes awswrangler)
uv add jyablonski_common_modules --extra parquet

# With all optional dependencies
uv add jyablonski_common_modules --extra all
```

Or using pip:

```bash
# Basic installation
pip install jyablonski_common_modules

# With extras
pip install jyablonski_common_modules[parquet]
pip install jyablonski_common_modules[es-logging]
pip install jyablonski_common_modules[all]
```
