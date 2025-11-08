"""Sort keys in JSON files and save them back."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import json
from typing import List

import argcomplete
from chaos_utils.text_utils import save_json


def sort_keys(filenames: List[str]) -> None:
    """Sort keys in JSON files and save them back.

    Args:
        filenames: List of JSON files to process
    """
    for filename in filenames:
        with open(filename) as f:
            data = json.loads(f.read())
        save_json(filename, data)


def main() -> None:
    """Main function to process JSON files."""
    parser = argparse.ArgumentParser(
        description="read .json files then save it with sort_keys"
    )
    parser.add_argument(
        "filenames",
        nargs="+",
        metavar="JSON_FILE",
        help=".json filenames",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    sort_keys(args.filenames)


if __name__ == "__main__":
    main()
