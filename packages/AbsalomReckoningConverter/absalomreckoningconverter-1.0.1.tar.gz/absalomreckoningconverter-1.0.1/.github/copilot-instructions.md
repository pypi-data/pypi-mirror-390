# Absalom Reckoning Converter - AI Coding Instructions

## Project Overview
A Python library that converts Gregorian dates to the Absalom Reckoning calendar system from Paizo's Pathfinder RPG. The core architecture consists of:
- **`arconverter.py`**: Main conversion logic with `convert()` function (simple +2700 year offset)
- **`ardate.py`**: Data class representing AR dates with multiple output formats
- **`constants.py`**: Lookup dictionaries mapping Gregorian calendar to AR equivalents (weekdays, months, seasons)

The package name differs from import name: install `AbsalomReckoningConverter`, import `arconverter`.

## Development Workflow

### Package Management (uv, NOT poetry)
```powershell
uv sync --all-extras --dev    # Setup dev environment
uv run pytest                  # Run tests
uv run ruff check .           # Lint code
uv run arconverter            # Run CLI (prints today's date in AR)
```

### Testing
- Use pytest with **arrange/act/assert** pattern (see `tests/test_arConverter.py`)
- Test file location: `tests/` at project root (configured in `pyproject.toml`)
- Run coverage: `uv run pytest --cov`
- Key test pattern: validate all ArDate attributes, not just formatted outputs

## Code Style & Conventions

### Type Hints & Formatting
- **Required**: Type annotations on function arguments and return values (not on `self`)
- **Quotes**: Single quotes for strings (`'Erastus'`), triple-double for docstrings
- **Line length**: 120 chars (wider than PEP 8's 79 to avoid excessive wrapping)
- **Imports**: Sorted per ruff (E, F, I rules enabled in `.ruff.toml`)
- **Docstrings**: Minimal, usually single-line. Include usage examples in module/function docstrings

### Calendar Constants Pattern
All lookup dictionaries in `constants.py` use **1-based indexing** (months 1-12, weekdays 1-7) to match calendar conventions. Moonday is weekday #1, not Sunday.

### Error Handling
- Use `ArConverterError` for all domain-specific errors
- Validate inputs early in `convert()` via `validate_date()`
- Year range limits: 1970-2099 (see `MIN_YEAR`/`MAX_YEAR` constants)

### Public API
Only `convert()` and `ArConverterError` are exported in `__init__.py`. The `ArDate` class is returned but not directly instantiated by users.

## Project-Specific Patterns

### ArDate Output Methods
Five formatted output methods follow this naming convention:
- `short_date()` → "Era 10, 4723" (abbreviated month)
- `long_date()` → "Erastus 10, 4723" (full religious month)
- `weekday_date()` → "Moonday Erastus 10, 4723" (includes weekday)
- `common_long_month()` → "Fletch 10, 4723" (common folk month name)
- `month_season()` → "Summer" (returns season string)

### Dual Month Systems
AR calendar has two month naming systems:
1. **Religious months** (arMonths): "Abadius", "Erastus", etc. - used in `long_date()`
2. **Common folk months** (arCommonMonths): "Prima", "Fletch", etc. - used in `common_long_month()`

Both map to the same Gregorian months but serve different cultural contexts in Pathfinder lore.

## Key Files
- `src/AbsalomReckoningConverter/constants.py` - All calendar mappings (modify for festivals/holidays)
- `pyproject.toml` - Package metadata (PEP 621 format) and pytest config
- `tests/test_arConverter.py` - Comprehensive test suite with edge cases (leap years, season changes)

## Common Tasks
- **Adding new output format**: Add method to `ArDate` class, follow existing naming pattern
- **Supporting holidays**: Extend `constants.py` with date-specific mappings, update `convert()`
- **Extending year range**: Modify `MIN_YEAR`/`MAX_YEAR` and test edge cases

- test pattern use the arrange/act/assert pattern
- I prefer concise explanations and minimal comments in the code itself.
- use powershell for code snippets related to command line usage.