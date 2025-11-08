"""Generate checksums for all files in a directory.

This module provides functionality to recursively calculate file hashes
for all files in a directory, supporting multiple hash algorithms and
parallel processing.
"""

# PYTHON_ARGCOMPLETE_OK

import argparse
import hashlib
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Optional, Tuple

import argcomplete
from chaos_utils.gitignore import iter_files_with_respect_gitignore
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)

DEFAULT_DIGEST = "sha256"
SUPPORTED_DIGESTS = {
    "sha1": hashlib.sha1,
    "sha224": hashlib.sha224,
    "sha256": hashlib.sha256,
    "sha384": hashlib.sha384,
    "sha512": hashlib.sha512,
}


def file_digest(file_path: Path, digest: str) -> Optional[Tuple[str, Path]]:
    """Calculate the hash digest of a file.

    Args:
        file_path: Path to the file to hash
        digest: Name of the hash algorithm to use

    Returns:
        Tuple of (hash_value, file_path) if successful, None on error
    """
    try:
        with open(file_path, "rb") as f:
            hasher = SUPPORTED_DIGESTS[digest]()
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
            hexdigest = hasher.hexdigest()
        return (hexdigest, file_path)
    except Exception as err:
        logger.error("Error processing %s: %s", file_path, err)
        return None  # Explicitly return None for later filtering


def process_directory(
    directory: Path,
    digest: str = DEFAULT_DIGEST,
    respect_gitignore: bool = False,
    workers: Optional[int] = None,
) -> None:
    """Process all files in a directory to calculate their hashes.

    Args:
        directory: Path to the directory to process
        digest: Hash algorithm to use
        respect_gitignore: Whether to respect .gitignore files
        workers: Number of parallel worker processes
    """
    files = list(iter_files_with_respect_gitignore(directory, respect_gitignore))
    if not files:
        logger.warning("No files found in directory: %s", directory)
        return

    logger.info("Processing %d files with %s...", len(files), digest)
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            results = executor.map(
                file_digest,
                files,
                [digest] * len(files),
                chunksize=10,
            )

        filtered_results = [r for r in results if r is not None]
        # Sort results by file path
        sorted_results = sorted(filtered_results, key=lambda x: str(x[1]))

        # Write to output file
        output_file = directory.with_name(f"{directory.name}.{digest}")
        with open(output_file, "w", encoding="utf-8") as f:
            for hash_value, file_path in sorted_results:
                relpath = file_path.relative_to(directory)
                f.write(f"{hash_value}  {relpath}\n")

        logger.info("Results written to: %s", output_file)

    except Exception as err:
        logger.error("Error during processing: %s", err)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Calculate file hashes for all files in a directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=os.getcwd(),
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-d",
        "--digest",
        choices=SUPPORTED_DIGESTS.keys(),
        default=DEFAULT_DIGEST,
        help=f"Hash algorithm to use (default: {DEFAULT_DIGEST})",
    )
    parser.add_argument(
        "-g",
        "--respect-gitignore",
        action="store_true",
        help="Respect .gitignore files when listing files",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=None,
        help="Number of parallel workers (default: number of CPU cores)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main() -> None:
    """Main function to process directory and generate hash file."""
    args = parse_args()

    try:
        directory = Path(args.directory).resolve()
        if not directory.is_dir():
            raise ValueError("Not a directory: %s" % directory)

        logger.debug("Processing directory: %s", directory)
        logger.debug("Using hash algorithm: %s", args.digest)
        logger.debug("Using %s workers", args.workers or "auto")
        logger.debug("Respect .gitignore: %s", args.respect_gitignore)

        process_directory(
            directory,
            args.digest,
            args.respect_gitignore,
            args.workers,
        )

    except Exception as err:
        logger.error(err)


if __name__ == "__main__":
    main()
