# bigdata-helper

**Version:** 0.1.0  
**Author:** Satyam Kale

A lightweight library that stores ready-to-use Big Data practical codes and lets you retrieve them instantly as strings.

> ⚠️ This package is intended for learning, practice, and revision. Use responsibly and follow your institution's academic policies.

## Install

```bash
pip install bigdata-helper
```

## Quick Start

```python
from bigdata_helper import get_code, list_codes

print(list_codes())
print(get_code("mini"))
print(get_code("forestfire"))
```

## Available Codes

- `mini` — Multiple regressors benchmark on a synthetic Graduate Admissions dataset (prints model performance and a sample prediction).
- `forestfire` — MapReduce-like analysis pipeline for forest fire dataset with SQLite, correlation, and monthly summaries.

## Add More

You can contribute more codes by adding functions to `bigdata_helper/codes.py` and mapping them in `get_code_map()`.
