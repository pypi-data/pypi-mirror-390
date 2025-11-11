# DataCleanerPro

A lightweight Python library for cleaning CSV datasets quickly and efficiently.

## Features
- Remove duplicate rows
- Fill missing values (mean, median, mode, zero)
- Drop unnecessary columns
- Save cleaned datasets easily

## Installation
```bash
pip install datacleanerpro
```

## Usage
```python
from datacleanerpro import DataCleaner

cleaner = DataCleaner("data.csv")
cleaner.remove_duplicates()
cleaner.fill_missing("mean")
cleaner.drop_columns(["unnecessary_column"])
cleaner.save_cleaned_data("cleaned.csv")
```
