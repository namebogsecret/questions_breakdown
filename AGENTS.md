# Project Structure and Instructions

This repository contains simple scripts for generating task breakdowns using the OpenAI API.

## Files
- `main.py` – main script to request a breakdown from the API and save results. Now accepts command line arguments for query, model and depth.
- `print_rezults.py` – helper for printing saved JSON structures to a tree view. Run with a path to a JSON file.
- `helpers/run_checks.sh` – basic syntax check script (`python -m py_compile`).
- `helpers/data/` – contains auxiliary data like `sample_query.txt`.

## Usage
1. Place an API key in `.env` under `gpt_api`.
2. Run `python main.py "your task"` to generate a breakdown. Additional options are available via `--help`.
3. Use `python print_rezults.py result.json` to print a saved JSON file.

## Notes for Future Edits
- `all_steps` is a `set` to ensure unique steps across recursive calls.
- Update this file whenever new modules are added or structure changes.
