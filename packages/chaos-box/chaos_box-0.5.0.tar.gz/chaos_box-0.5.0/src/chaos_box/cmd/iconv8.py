"""Convert text files to UTF-8 encoding with automatic encoding detection."""

# PYTHON_ARGCOMPLETE_OK

import argparse
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_logger
from chaos_utils.text_utils import detect_encoding

logger = setup_logger(__name__)


skipped_files = set()
failed_files = set()


def convert_to_utf8(
    input_path: Path, output_path: Path, apply: bool = False, force: bool = False
) -> None:
    """Convert a text file to UTF-8 encoding.

    Args:
        input_path: Path to input file
        output_path: Path to write output
        apply: Whether to actually perform the conversion
        force: If True, overwrite existing files
    """
    encoding = detect_encoding(input_path)
    if encoding.lower() in ("utf-8", "utf8"):
        skipped_files.add(input_path)
        logger.info("[SKIP   ] %s is already UTF-8 encoded", input_path)
        return

    if not encoding:
        logger.warning("Failed to detect encoding for %s", input_path)
        return

    if not apply:
        logger.info(
            "[DRY-RUN] %s (%s)\n          → %s", input_path, encoding, output_path
        )
        return

    if output_path.exists() and not force:
        logger.warning(
            "[SKIP   ] Output file %s already exists. Use --force to overwrite.",
            output_path,
        )
        return

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        chunk_size = 1024 * 1024  # 1MB
        with (
            open(input_path, "r", encoding=encoding, errors="replace") as src,
            open(output_path, "w", encoding="utf-8") as dest,
        ):
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                dest.write(chunk)
        logger.info(
            "[OK     ] %s (%s)\n          → %s", input_path, encoding, output_path
        )
    except Exception as err:
        failed_files.add(input_path)
        logger.error("[FAIL   ] %s (%s): %s", input_path, encoding, err)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Convert text files to UTF-8 encoding")
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        metavar="FILE",
        help="Files to convert",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output directory for converted files, default is the same directory as input files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="force overwrite of existing output files",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the conversion (default is dry-run)",
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main() -> None:
    """Main function to process files and convert encodings."""
    args = parse_args()
    output_dir = Path(args.output).expanduser() if args.output else None

    logger.info("Found %d files to process", len(args.files))
    if not args.apply:
        logger.info("Running in dry-run mode - no changes will be made")

    for file in args.files:
        input_path = Path(file).expanduser()
        if not input_path.exists():
            logger.error("File '%s' does not exist", input_path)
            continue

        output_path = input_path.with_stem(input_path.stem + "-utf8")
        if output_dir:
            output_path = output_dir / input_path.name

        convert_to_utf8(input_path, output_path, args.apply, args.force)

    if skipped_files:
        logger.info(
            "Skipped %d files that are already UTF-8 encoded:\n    %s",
            len(skipped_files),
            "\n    ".join(str(f) for f in skipped_files),
        )
    if failed_files:
        logger.error(
            "Failed to convert %d files:\n    %s",
            len(failed_files),
            "\n    ".join(str(f) for f in failed_files),
        )


if __name__ == "__main__":
    main()
