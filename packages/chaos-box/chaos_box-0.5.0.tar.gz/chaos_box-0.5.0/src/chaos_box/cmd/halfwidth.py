"""Convert full-width punctuation to half-width in text files."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import sys
from pathlib import Path

import argcomplete

KEYMAPS = {
    "。": ".",
    "，": ",",
    "：": ":",
    "；": ";",
    "、": ",",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "（": "(",
    "）": ")",
    "【": "[",
    "】": "]",
    "｛": "{",
    "｝": "}",
    "「": "{",
    "」": "}",
    "『": "{",
    "』": "}",
    "《": "<",
    "》": ">",
    "·": "`",
    "…": "^",
    "￥": "$",
    "¥": "$",
    "？": "?",
    "！": "!",
    "—": "_",
    "｜": "|",
}

PUNCTUATIONS_NEED_SPACE = set(".:,;!?")
PUNCTUATIONS_NEXT_CHAR_EXCEPTIONS = set(" \n\r\t.,，。：；？！、")


def convert_line(line: str) -> str:
    """Convert punctuation in a line of text.

    Args:
        line: Input text line

    Returns:
        Text with converted punctuation
    """
    new_line = ""
    for i, ch in enumerate(line):
        if ch not in KEYMAPS:
            new_line += ch
            continue

        half = KEYMAPS[ch]
        is_line_end = i == len(line.strip()) - 1
        next_char = line[i + 1] if i + 1 < len(line) else ""

        if (
            half in PUNCTUATIONS_NEED_SPACE
            and not is_line_end
            and next_char not in PUNCTUATIONS_NEXT_CHAR_EXCEPTIONS
        ):
            new_line += half + " "
        else:
            new_line += half

    return new_line


def process_file(filepath: Path, inplace: bool) -> None:
    """Process a single file.

    Args:
        filepath: Path to file to process
        inplace: If True, modify file in place
    """
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    converted_lines = [convert_line(line) for line in lines]

    if inplace:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(converted_lines)
    else:
        for line in converted_lines:
            print(line, end="")


def main():
    parser = argparse.ArgumentParser(
        description="Convert full-width punctuation to half-width in text files."
    )
    parser.add_argument("files", nargs="+", metavar="FILE", help="Input text files")
    parser.add_argument(
        "-i", "--inplace", action="store_true", help="Edit the file in place"
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    for file in args.files:
        filepath = Path(file)
        if not filepath.exists():
            print(f"File not found: {filepath}", file=sys.stderr)
            sys.exit(1)

        process_file(filepath, args.inplace)


if __name__ == "__main__":
    main()
