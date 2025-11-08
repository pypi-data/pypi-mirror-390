"""Create rotating animations from images as GIF or MP4."""

# PYTHON_ARGCOMPLETE_OK

import argparse
from pathlib import Path
from typing import List

import argcomplete
import cv2
import numpy
from chaos_utils.logging import setup_logger
from PIL import Image, ImageDraw, ImageOps

logger = setup_logger(__name__)


def gen_circle_mask(im: Image.Image, upscale: int = 3) -> Image.Image:
    """Generate a circular mask for the image.

    Args:
        im: Input image
        upscale: Upscale factor for mask generation

    Returns:
        Circular mask image
    """
    # ref: https://stackoverflow.com/a/22336005
    size = (im.size[0] * upscale, im.size[1] * upscale)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    mask = mask.resize(im.size, resample=Image.Resampling.LANCZOS)
    logger.debug("mask = %s", mask)

    return mask


def gen_rotated_frames(
    im: Image.Image, step: int = 45, trim: bool = False
) -> List[Image.Image]:
    """Generate frames of rotated images.

    Args:
        im: Input image
        step: Rotation step in degrees
        trim: Whether to trim background

    Returns:
        List of rotated image frames
    """
    mask = gen_circle_mask(im)
    mask_invert = ImageOps.invert(mask)
    circle = im.copy()
    circle.putalpha(mask)

    frames = []
    for angle in range(0, 360, step):
        frame = circle.copy().rotate(angle=angle)
        if not trim:
            frame.paste(im, mask=mask_invert)
        frames.append(frame)

    return frames


def PIL_frames_to_video(file_path: Path, frames: List[Image.Image], fps: int) -> None:
    """Convert PIL image frames to video file.

    Args:
        file_path: Output video file path
        frames: List of image frames
        fps: Frames per second
    """
    # ref: https://blog.extramaster.net/2015/07/python-pil-to-mp4.html
    videodim = frames[0].size
    forcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(file_path, forcc, fps, videodim)
    for frame in frames:
        video.write(cv2.cvtColor(numpy.array(frame), cv2.COLOR_RGB2BGR))

    video.release()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rotate images and save as GIF or MP4")
    parser.add_argument(
        "-s",
        "--step",
        type=int,
        default=45,
        help="Image.rotate angles step, default: %(default)s",
    )
    parser.add_argument(
        "-f",
        "--fps",
        type=int,
        default=50,
        help="GIF/video frame per seconds, default: %(default)s",
    )
    parser.add_argument(
        "-F",
        "--format",
        choices=("gif", "mp4"),
        default="gif",
        help="Output filename format",
    )
    parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Reverse direction of rotation, clockwise (cw) if set, counter clockwise (ccw) if not",
    )
    parser.add_argument(
        "-t",
        "--trim",
        action="store_true",
        help="Trim surrounding background",
    )
    parser.add_argument(
        "images", nargs="+", metavar="image", help="Images to processing"
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.fps > 50:
        logger.warning(
            "GIFs with a frame rate higher than 50 fps may not be handled properly by many image viewers."
        )

    for image in args.images:
        image = Path(image).expanduser().resolve()
        logger.info("Processing image: %s", image)

        with Image.open(image) as im:
            frames = gen_rotated_frames(im, step=args.step, trim=args.trim)
            logger.debug("len(frames) = %d", len(frames))

        if args.reverse:
            # clockwise (cw) if set, counter clockwise (ccw) if not
            # keep the first frame as first, and reverse the left
            first = frames.pop(0)
            frames = [first] + frames[::-1]

        # cw: clockwise, ccw: counter clockwise
        direction = "cw" if args.reverse else "ccw"
        trim = "-trim" if args.trim else ""
        file_path = (
            image.parent
            / f"{image.stem}-{len(frames)}p@{args.fps}fps-{direction}{trim}.{args.format}"
        )
        logger.info("Saving frames to: %s", file_path)
        if args.format == "gif":
            frames[0].save(
                file_path,
                save_all=True,
                append_images=frames[1:],
                duration=1000 / args.fps,
                loop=0,
            )
        elif args.format == "mp4":
            PIL_frames_to_video(file_path, frames, args.fps)


if __name__ == "__main__":
    main()
