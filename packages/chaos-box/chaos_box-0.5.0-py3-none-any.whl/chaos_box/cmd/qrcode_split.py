"""Split files into QR code images for fun.

This module provides functionality to split any file into a series of QR codes,
supporting parallel processing and resumable operations.
"""

# PYTHON_ARGCOMPLETE_OK

import argparse
import base64
import math
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Iterator, List, Tuple

import argcomplete
import qrcode
from chaos_utils.logging import setup_logger
from PIL import ImageDraw, ImageFont

logger = setup_logger(__name__)


def iter_file_into_chunks(
    file_path: Path, chunk_size: int
) -> Iterator[Tuple[bytes, int]]:
    """Read a file in chunks and yield each chunk with its index.

    Args:
        file_path: Path to the input file
        chunk_size: Size of each chunk in bytes

    Yields:
        Tuples of (chunk_data, chunk_index)
    """
    with open(file_path, "rb") as f:
        index = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield (chunk, index)
            index += 1


def generate_qr_code(
    chunk: bytes, index: int, total_chunks: int, output_dir: Path, prefix: str
) -> None:
    """Generate a QR code image for a chunk of data.

    Args:
        chunk: Binary data to encode
        index: Index number of this chunk
        total_chunks: Total number of chunks
        output_dir: Directory to save the QR code image
        prefix: Prefix for the output filename
    """
    qr = qrcode.QRCode(
        version=40,  # Version 40 is the largest, can store up to 2953 bytes in binary mode
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(base64.b64encode(chunk).decode("utf-8"))
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white").convert("RGB")

    # Add footer with index/total_count_of_files
    draw = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 20)
    except Exception:
        font = ImageFont.load_default()
    text = f"{index}/{total_chunks}"
    textbbox = draw.textbbox((0, 0), text, font=font)
    textwidth = textbbox[2] - textbbox[0]
    textheight = textbbox[3] - textbbox[1]
    width, height = img.size
    text_x = (width - textwidth) / 2
    text_y = height - textheight - 10  # Adjust the Y position

    draw.text((text_x, text_y), text, font=font, fill="black")

    img_path = output_dir / f"{prefix}_{index:0{len(str(total_chunks))}d}.png"
    img.save(img_path)
    logger.info("Saved QR code %s to %s", index, img_path)


def get_existing_indices(output_dir: Path, prefix: str) -> List[int]:
    """Get list of existing QR code indices in the output directory.

    Args:
        output_dir: Directory containing QR code images
        prefix: Filename prefix to match

    Returns:
        Sorted list of existing chunk indices
    """
    existing_files = output_dir.glob("*.png")
    indices = []
    for file in existing_files:
        if file.name.startswith(prefix + "_"):
            try:
                index = int(file.stem[len(prefix) + 1 :])
                indices.append(index)
            except ValueError:
                continue
    return sorted(indices)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Split a file into a series of QR code images."
    )
    parser.add_argument("file", help="Path to the input file (text or binary).")
    parser.add_argument(
        "-O",
        "--output-dir",
        default=".",
        help="Directory to save the QR code images.",
    )
    parser.add_argument(
        "-c",
        "--chunk-size",
        type=int,
        default=1900,
        help="Size of each chunk in bytes (default: 1900).",
    )
    parser.add_argument(
        "-C",
        "--calc",
        action="store_true",
        help="Calculate and print the count of QR code files needed without generating QR codes.",
    )
    parser.add_argument(
        "-r",
        "--resume",
        action="store_true",
        help="Resume generating QR codes from where it left off.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=sys.maxsize,
        help="Number of QR code images to generate.",
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
    """Main function to split a file into QR code images."""
    args = parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        logger.error("Input file does not exist: %s", file_path)
        return

    total_chunks = math.ceil(file_path.stat().st_size / args.chunk_size)

    if args.calc:
        logger.info("Total QR code files needed: %d", total_chunks)
        return

    logger.info("Splitting %s into %d QR codes.", file_path, total_chunks)

    output_dir = Path(args.output_dir) / file_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.resume:
        existing_indices = get_existing_indices(output_dir, file_path.stem)
    else:
        existing_indices = []

    last_index = existing_indices[-1] if len(existing_indices) > 0 else 0

    count = 0
    futures = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        for chunk, index in iter_file_into_chunks(file_path, args.chunk_size):
            if index <= last_index:
                continue

            count += 1
            if count > args.limit:
                break

            futures.append(
                executor.submit(
                    generate_qr_code,
                    chunk,
                    index,
                    total_chunks,
                    output_dir,
                    file_path.stem,
                )
            )

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as err:
                logger.error("QR code generation failed: %s", err)


if __name__ == "__main__":
    main()
