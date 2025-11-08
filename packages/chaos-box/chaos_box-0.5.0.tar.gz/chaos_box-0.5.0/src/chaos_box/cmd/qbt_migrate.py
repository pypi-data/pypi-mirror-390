"""Migrate qBittorrent BT_backup directory save paths and categories."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import json
import re
from pathlib import Path

import argcomplete
from chaos_utils.logging import setup_logger
from fastbencode import bdecode, bencode

logger = setup_logger(__name__)


def qbt_migrate(
    file: Path,
    pattern: str,
    repl: str,
    auto_managed: int = -1,
    private: int = -1,
    apply: bool = False,
) -> None:
    """Migrate paths in qBittorrent fastresume files.

    Args:
        file: Path to fastresume file
        pattern: Regex pattern to match in paths
        repl: Replacement string
        auto_managed: Filter by auto_managed flag (-1=any, 0=false, 1=true)
        private: Filter by private flag (-1=any, 0=public, 1=private)
        apply: Whether to actually modify files
    """
    try:
        with open(file, "rb") as f:
            fastresume = bdecode(f.read())
    except Exception as e:
        logger.warning("Failed to decode fastresume: %s (%s)", file, e)
        return

    # auto_managed 过滤
    if auto_managed in (0, 1):
        if fastresume.get(b"auto_managed", 0) != auto_managed:
            return

    # private 过滤
    if private in (0, 1):
        torrent_file = file.with_suffix(".torrent")
        try:
            with open(torrent_file, "rb") as f:
                torrent = bdecode(f.read())
            if torrent.get(b"info", {}).get(b"private", 0) != private:
                return
        except Exception as e:
            logger.warning("Failed to decode torrent: %s (%s)", torrent_file, e)
            return

    name = fastresume.get(b"name", b"").decode(errors="replace")
    save_path = fastresume.get(b"save_path", b"").decode(errors="replace")
    qBt_category = fastresume.get(b"qBt-category", b"").decode(errors="replace")

    if not re.search(pattern, save_path):
        return

    new_save_path = re.sub(pattern, repl, save_path)
    new_qBt_category = re.sub(pattern, repl, qBt_category)

    # pretty diff 输出
    diff = {
        "file": file.name,
        "name": name,
        "save_path": {"old": save_path, "new": new_save_path},
        "qBt-category": {"old": qBt_category, "new": new_qBt_category},
        "apply": apply,
    }
    logger.info("\n%s", json.dumps(diff, indent=2, ensure_ascii=False))

    if apply:
        try:
            fastresume[b"save_path"] = new_save_path.encode()
            fastresume[b"qBt-category"] = new_qBt_category.encode()
            with open(file, "wb") as f:
                f.write(bencode(fastresume))
        except Exception as e:
            logger.error("Failed to write fastresume: %s (%s)", file, e)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--BT_backup",
        default="./BT_backup",
        help="qBittorrent BT_backup directory, default: '%(default)s'",
    )
    parser.add_argument(
        "--pattern",
        default=r"main/",
        help="save_path re.search pattern for .fastresume files, default: '%(default)s'",
    )
    parser.add_argument(
        "--repl",
        default=r"tank/",
        help="save_path re.sub replacement for .fastresume files, default: '%(default)s'",
    )
    parser.add_argument(
        "--auto_managed",
        choices=(-1, 0, 1),
        default=-1,
        type=int,
        help="filter auto_managed(1) or not(0) tasks, -1 for not filtering",
    )
    parser.add_argument(
        "--private",
        choices=(-1, 0, 1),
        default=-1,
        type=int,
        help="filter private(1) or public(0) tasks, -1 for not filtering",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually perform the renaming (default is dry-run)",
    )
    argcomplete.autocomplete(parser)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    BT_backup = Path(args.BT_backup).resolve()
    if not BT_backup.exists():
        logger.warning("BT_backup: %s does not exist", BT_backup)
        return

    for file in BT_backup.glob("*.fastresume"):
        qbt_migrate(
            file, args.pattern, args.repl, args.auto_managed, args.private, args.apply
        )


if __name__ == "__main__":
    main()
