# Tools and Utilities
List of handy tools and utilities

## scripts/run_scripts.py
Run scripts with various arguments and process console output, then store results in CSV.

```
usage: run_scripts.py [-h] --scripts_file SCRIPTS_FILE --patterns_file PATTERNS_FILE [-o OUTPUT_FILE]

Run scripts with various arguments and process console output, then store results in CSV.

options:
  -h, --help            show this help message and exit
  --scripts_file SCRIPTS_FILE
                        JSON file containing script configuration
  --patterns_file PATTERNS_FILE
                        JSON file containing result and error patterns
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        Output CSV file path (default: results.csv)
```