"""Extract control and data files from Debian package (.deb) archives."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import shutil
import tarfile
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_logger
from chaos_utils.tarfile import TarFileZstd
from debian import arfile

logger = setup_logger(__name__)


class DebExtractor:
    """Handle extraction of .deb files in a directory."""

    def __init__(self, directory: Path, delete_mode: bool = False) -> None:
        """Initialize the DebExtractor.

        Args:
            directory: Path containing .deb files
            delete_mode: If True, remove extracted directories instead of extracting
        """
        self.directory = directory
        self.delete_mode = delete_mode

    def _extract_deb(self, deb_path: Path, extract_dir: Path) -> None:
        """Extract a single .deb file.

        Args:
            deb_path: Path to .deb file
            extract_dir: Directory to extract to
        """
        if extract_dir.exists():
            logger.info("Skipping '%s' (already extracted)", deb_path.name)
            return

        try:
            with open(deb_path, "rb") as f:
                ar_file = arfile.ArFile(fileobj=f)
                self._extract_ar_members(ar_file, extract_dir)
            logger.info(
                "Successfully extracted '%s' to '%s'", deb_path.name, extract_dir
            )
        except (OSError, arfile.ArError, tarfile.TarError) as err:
            shutil.rmtree(extract_dir, ignore_errors=True)
            logger.error("Failed to process '%s': '%s'", deb_path.name, err)

    def _extract_ar_members(self, ar_file: arfile.ArFile, extract_dir: Path) -> None:
        """Extract members from an ar archive.

        Args:
            ar_file: Ar archive object
            extract_dir: Directory to extract to
        """
        for member in ar_file.getmembers():
            if member.name.startswith("control.tar"):
                self._extract_ar_member(member, extract_dir / "control")
            elif member.name.startswith("data.tar"):
                self._extract_ar_member(member, extract_dir / "data")

    def _extract_ar_member(self, member: arfile.ArMember, extract_dir: Path):
        extract_dir.mkdir(parents=True, exist_ok=True)
        with TarFileZstd.open(fileobj=member) as tar:
            tar.extractall(path=extract_dir)
        logger.debug("Extracted '%s' to '%s'", member.name, extract_dir)

    def _remove_extracted(self, extract_dir: Path):
        if extract_dir.exists() and extract_dir.is_dir():
            try:
                shutil.rmtree(extract_dir)
                logger.info("Successfully removed '%s'", extract_dir)
            except OSError as err:
                logger.error("Failed to remove '%s': '%s'", extract_dir, err)

    def process_deb(self, deb_path: Path) -> None:
        """Process a single .deb file.

        Args:
            deb_path: Path to .deb file
        """
        extract_dir = self.directory / deb_path.stem

        if self.delete_mode:
            self._remove_extracted(extract_dir)
        else:
            self._extract_deb(deb_path, extract_dir)

    def run(self) -> None:
        """Run extraction on all .deb files in the directory."""
        deb_files = sorted(self.directory.glob("*.deb"))
        if not deb_files:
            logger.warning("No .deb files found in '%s'", self.directory.resolve())
            return

        logger.info("Found %d .deb file(s) to process", len(deb_files))
        for deb_file in deb_files:
            self.process_deb(deb_file)


def main():
    parser = argparse.ArgumentParser(
        description="Debian package extractor",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Remove extracted directories instead of extracting",
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    directory = Path(args.directory)
    extractor = DebExtractor(directory, delete_mode=args.delete)
    extractor.run()


if __name__ == "__main__":
    main()
