# smart_round

A Python package that provides intelligent value rounding and formatting for better numeric readability.

## Features

- **smart_round**: Intelligently round float values, preserving significant digits for small numbers
- **format_value**: Convert float values to nicely formatted strings with appropriate precision
- **format_dataframe**: Format all float columns in a pandas DataFrame for better display

## Installation

```bash
pip install smart_round
```

## Dependencies

- NumPy (required for `format_value` and, by extension, for `format_dataframe`)
- pandas (required for `format_dataframe`)

These dependencies are optional if you only need the basic `smart_round` function.

## Usage Examples

### Basic rounding with `smart_round`

```python
from smart_round import smart_round

# Regular numbers round to the specified decimal places
smart_round(1.2345, tail=2)  # Returns 1.23

# Very small numbers keep enough decimal places to show at least one significant digit
smart_round(0.00123, tail=2)  # Returns 0.0012 instead of 0.00

# Zero is handled as a special case
smart_round(0, tail=2)  # Returns 0.0
```

### Formatting values with `format_value`

```python
from smart_round import format_value
import numpy as np

# Format regular numbers
format_value(1.2345)  # Returns '1.235'

# Format very small numbers while preserving significant digits
format_value(0.00123)  # Returns '0.001'

# Handle NaN values gracefully
format_value(np.nan)  # Returns ''

# Ensure decimal point is followed by at least one digit
format_value(1.0)  # Returns '1.0' not '1.'
```

### Working with pandas DataFrames

```python
from smart_round import format_dataframe
import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'Value': [1.23456, 0.00123, 123.45],
    'Other': ['A', 'B', 'C']
})

# Format float columns
formatted_df = format_dataframe(df)
print(formatted_df)
```

Output:
```
   Value Other
0  1.235     A
1  0.001     B
2  123.45    C
```

## How it works

The `smart_round` function works by:
1. Handling zero as a special case
2. Using standard rounding for numbers ≥ 1
3. For small numbers (< 1), finding the minimum number of decimal places needed to show a non-zero value
4. Rounding to that number of places or the requested places, whichever is larger

This makes the function particularly useful for displaying data with varying magnitudes while maintaining readability.

## License

[MIT License](LICENSE)