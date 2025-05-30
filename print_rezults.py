import argparse
import json


def print_steps(json_data, indent=0, prefix='', file=None):
    """Recursively print steps from nested JSON."""
    keys = list(json_data.keys())
    for i, key in enumerate(keys):
        value = json_data[key]
        is_last = i == len(keys) - 1
        new_prefix = prefix + ('└── ' if is_last else '├── ')
        print(prefix + new_prefix + value["step"], file=file)
        if value.get("need_futher_breakdown"):
            next_prefix = prefix + ('    ' if is_last else '│   ')
            print_steps(value["SubSteps"], indent=indent + 4, prefix=next_prefix, file=file)


def main():
    parser = argparse.ArgumentParser(description="Print task tree from JSON file")
    parser.add_argument("json_file", help="Path to results JSON file")
    parser.add_argument("-o", "--output", help="Optional path to save text output")
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out:
            print_steps(data, file=out)
    else:
        print_steps(data)


if __name__ == "__main__":
    main()
