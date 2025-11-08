"""Archive all directories in a target directory using various compression formats."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)


def archive_dir(dir_path: Path, format: str, dry_run: bool = False) -> None:
    """Create an archive file from a directory.

    Args:
        dir_path: Path to the directory to archive
        format: Archive format to use (e.g. zip, tar, 7z)
        dry_run: If True, only show what would be done
    """
    archive_base = dir_path.parent / dir_path.name
    shutil.make_archive(
        base_name=str(archive_base), format=format, base_dir=dir_path, dry_run=dry_run
    )
    logger.info("Archive directory '%s' into '%s' format", dir_path, format)


def archive_dirs_mp(directory: Path, format: str, dry_run: bool, workers: int) -> None:
    """Archive all directories in parallel using multiple processes.

    Args:
        directory: Path containing directories to archive
        format: Archive format to use
        dry_run: If True, only show what would be done
        workers: Number of parallel worker processes
    """
    # List directories in the current directory, excluding hidden ones like .git
    dirs = [d for d in directory.iterdir() if d.is_dir() and not d.name.startswith(".")]

    with ProcessPoolExecutor(max_workers=workers) as executor:
        # list comprehension to create a mapping of futures to dir_path
        futures = {executor.submit(archive_dir, d, format, dry_run): d for d in dirs}
        for future in as_completed(futures):
            dir_path = futures[future]
            try:
                future.result()
            except Exception as err:
                logger.error("Error archiving directory '%s': %s", dir_path, err)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Archive directories in the current directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="zip",
        choices=[ar[0] for ar in shutil.get_archive_formats()],
        help="Specify the archive format.",
    )
    parser.add_argument(
        "-D",
        "--dry-run",
        action="store_true",
        help="dry_run argument for shutil.make_archive",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: %(default)s)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main():
    try:
        # Register 7z format if py7zr is installed
        # pip3 install -U py7zr || apt install python3-py7zr
        from py7zr import pack_7zarchive, unpack_7zarchive

        shutil.register_archive_format(
            "7z", function=pack_7zarchive, description="7zip archive"
        )
        shutil.register_unpack_format(
            "7z", extensions=[".7z"], function=unpack_7zarchive
        )
    except ImportError:
        pass

    args = parse_args()

    directory = Path(args.directory).resolve()
    archive_dirs_mp(directory, args.format, args.dry_run, args.workers)


if __name__ == "__main__":
    main()
