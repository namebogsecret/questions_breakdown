# Project Structure and Instructions

This repository contains simple scripts for generating task breakdowns using the OpenAI API.

## Files
- `main.py` – main script to request a breakdown from the API and save results. The entry point is guarded by `if __name__ == "__main__"`.
- `print_rezults.py` – helper for printing saved JSON structures to a tree view.

## Usage
1. Place an API key in `.env` under `gpt_api`.
2. Run `python main.py` to generate a breakdown using the example query.
3. Use `print_rezults.py` if you need to print a saved JSON file.

## Notes for Future Edits
- `all_steps` is a `set` to ensure unique steps across recursive calls.
- Update this file whenever new modules are added or structure changes.
