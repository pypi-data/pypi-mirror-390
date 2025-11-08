"""URL encode or decode text from files or standard input."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import fileinput
from urllib.parse import quote, unquote

import argcomplete


def main() -> None:
    """Main function to process input text."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--decode",
        action="store_true",
        default=False,
        help="urldecode lines from files",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="files to read, if empty, stdin is used",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    url_processor = unquote if args.decode else quote

    try:
        for line in fileinput.input(files=args.files):
            print(url_processor(line.rstrip()))
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
