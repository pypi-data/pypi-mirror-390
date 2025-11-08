"""Convert vol.moe's mobi manga files into various archive formats."""

# PYTHON_ARGCOMPLETE_OK
# A helper script to convert vol.moe's mobi files to 7zip archives.
# python3 -m pip install mobi py7zr

import argparse
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Iterator

import argcomplete
import mobi
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)


FORMAT_EXT = {
    "7z": ".7z",
    "zip": ".zip",
    "tar": ".tar",
    "gztar": ".tar.gz",
    "bztar": ".tar.bz2",
    "xztar": ".tar.xz",
}


def iter_mobi_files(
    directory: Path, format: str, force: bool = False
) -> Iterator[Path]:
    """Iterate over .mobi files in a directory.

    Args:
        directory: Path to search for .mobi files
        format: Archive format extension
        force: If True, process files even if archive exists

    Yields:
        Paths to .mobi files
    """
    for mobi_file in directory.rglob("*.mobi"):
        archive = mobi_file.with_suffix(FORMAT_EXT[format])
        if archive.exists() and not force:
            logger.warning("%s exist, skip...", archive)
            continue
        yield mobi_file


def archive_mobi(file_path: Path, format: str, dry_run: bool = False) -> str:
    """Extract and archive a single mobi file.

    Args:
        file_path: Path to .mobi file
        format: Archive format to use
        dry_run: If True, only show what would be done

    Returns:
        Path to created archive file
    """
    start = time.perf_counter()
    logger.info("Processing %s to %s archive...", file_path, format)
    extract_dir, _ = mobi.extract(str(file_path))
    elapsed = time.perf_counter() - start
    logger.debug("mobi.extract(%s) finished in %0.5f seconds", file_path, elapsed)
    extract_dir = Path(extract_dir)

    # Images directory
    # HDImages = extract_dir.joinpath("HDImages")
    mobi7 = extract_dir.joinpath("mobi7/Images")
    mobi8 = extract_dir.joinpath("mobi8/OEBPS/Images")
    # 先判断目录是否存在
    if mobi8.exists() and mobi8.is_dir() and any(mobi8.iterdir()):
        root_dir = mobi8
    elif mobi7.exists() and mobi7.is_dir():
        root_dir = mobi7
    else:
        logger.warning("No images directory found in %s", extract_dir)
        shutil.rmtree(extract_dir)
        return ""

    # 这样应该没有子目录, 压缩文件保存在源文件同目录
    start = time.perf_counter()
    archive = shutil.make_archive(
        file_path.stem, format=format, root_dir=root_dir, dry_run=dry_run
    )
    elapsed = time.perf_counter() - start
    logger.info("Created archive: %s", archive)
    logger.debug("shutil.make_archive(%s) finished in %0.5f seconds", archive, elapsed)

    # clean up
    shutil.rmtree(extract_dir)
    logger.debug("Removed extract directory: %s", extract_dir)

    return archive


def archive_mobi_mp(
    directory: Path, format: str, force: bool, dry_run: bool, workers: int
) -> None:
    """Process multiple mobi files in parallel.

    Args:
        directory: Path containing .mobi files
        format: Archive format to use
        force: If True, process files even if archive exists
        dry_run: If True, only show what would be done
        workers: Number of parallel worker processes
    """
    mobi_files = list(iter_mobi_files(directory, format, force))
    if not len(mobi_files) > 0:
        return
    logger.info("Found %d mobi files in %s", len(mobi_files), directory)

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(archive_mobi, f, format, dry_run): f for f in mobi_files
        }
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as err:
                logger.warning(err)

    elapsed = time.perf_counter() - start
    logger.debug("Program finished in %0.5f seconds", elapsed)


def parse_args():
    parser = argparse.ArgumentParser()

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
        "-F",
        "--force",
        action="store_true",
        help="force to overwrite existing archive files",
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
    archive_mobi_mp(directory, args.format, args.force, args.dry_run, args.workers)


if __name__ == "__main__":
    main()
