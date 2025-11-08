"""Rename files to include their last modified date as a prefix."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import argcomplete
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)

# Regex pattern for existing date prefixes
DATE_PREFIX_REGEX = re.compile(r"^(([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2})-)?")


def get_dest_filename(src_path: Path) -> Tuple[Path, bool]:
    """Generate new filename with last modified date prefix.

    Args:
        src_path: Source file path

    Returns:
        Tuple of (new path, should rename)
    """
    mtime = src_path.stat().st_mtime
    date_prefix = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    # Remove any existing date prefix
    dest_basename_no_prefix = DATE_PREFIX_REGEX.sub("", src_path.name)

    dest_basename = f"{date_prefix}-{dest_basename_no_prefix}"
    dest_path = src_path.parent / dest_basename

    return dest_path, (dest_path != src_path)


def process_files(files: List[Path], apply: bool = False) -> None:
    """Process files by either renaming them or logging the changes.

    Args:
        files: List of files to process
        apply: Whether to actually rename files
    """
    for src in files:
        if not src.exists():
            logger.error("File '%s' does not exist", src)
            continue

        dest, should_rename = get_dest_filename(src)
        if not should_rename:
            continue

        if not apply:
            logger.info("[DRY-RUN] src:  %s\n          dest: %s\n", src, dest)
            continue

        try:
            src.rename(dest)
            logger.info("src:  %s\ndest: %s\n", src, dest)
        except OSError as err:
            logger.error("Error renaming %s: %s", src, err)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Rename files with last modified date prefix"
    )
    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        metavar="FILE",
        help="Files to process",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the renaming (default is dry-run)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main() -> None:
    """Main function to process files."""
    args = parse_args()

    logger.info("Found %d files to process", len(args.files))
    if not args.apply:
        logger.info("Running in dry-run mode - no changes will be made")

    process_files(args.files, args.apply)
    logger.info("Processing complete")


if __name__ == "__main__":
    main()
