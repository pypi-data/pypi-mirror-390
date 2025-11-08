# PYTHON_ARGCOMPLETE_OK

import argparse
import fnmatch
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple

import argcomplete
import qbittorrentapi
import tomllib
from chaos_utils.logging import setup_logger

logger = setup_logger(__name__)


def filter_torrents(
    client: qbittorrentapi.Client,
    category: Optional[str] = "",
    tag: Optional[str] = "",
    name_glob: Optional[str] = "",
    name_regex: Optional[re.Pattern | None] = None,
) -> List[qbittorrentapi.TorrentDictionary]:
    """Filter torrents based on category, tag and name pattern."""
    torrents: List[qbittorrentapi.TorrentDictionary] = list(client.torrents_info())

    if category:
        torrents = [t for t in torrents if t.category == category]
    if tag:
        torrents = [t for t in torrents if tag in t.tags.split(",")]
    if name_glob:
        torrents = [t for t in torrents if fnmatch.fnmatch(t.name, name_glob)]
    if name_regex:
        torrents = [t for t in torrents if name_regex.search(t.name)]

    return torrents


def get_torrent_tracker_urls(
    torrent: qbittorrentapi.TorrentDictionary,
    tracker_regex: Optional[re.Pattern | None] = None,
) -> Set[str]:
    """Get all unique trackers for a torrent."""
    tracker_urls: Set[str] = set()
    for tracker in torrent.trackers:
        logger.debug("    tracker: %s of type %s", tracker, type(tracker))
        tracker_url = str(tracker.get("url", ""))
        if tracker_url in {"** [DHT] **", "** [PeX] **", "** [LSD] **"}:
            continue
        if isinstance(tracker_regex, re.Pattern):
            if not tracker_regex.search(tracker_url):
                continue
        tracker_urls.add(tracker_url)
    return tracker_urls


def modify_torrent_tracker(
    torrent: qbittorrentapi.TorrentDictionary,
    tracker_regex: Optional[re.Pattern | None] = None,
    tracker_replacement: Optional[str | None] = None,
    apply: bool = False,
) -> List[Tuple[str, str]]:
    """
    Modify tracker URLs using regex pattern.

    Returns:
        List of (old_tracker_url, new_tracker_url) pairs that were changed
    """
    changes = []
    tracker_urls = get_torrent_tracker_urls(torrent, tracker_regex)
    for old_tracker_url in tracker_urls:
        logger.info("  old_tracker_url: %s", old_tracker_url)
        if not tracker_replacement or tracker_regex is None:
            continue
        new_tracker_url = tracker_regex.sub(tracker_replacement, old_tracker_url)
        if new_tracker_url == old_tracker_url:
            continue
        logger.info("  new_tracker_url: %s", new_tracker_url)
        changes.append((old_tracker_url, new_tracker_url))
        if not apply:
            continue
        try:
            torrent.edit_tracker(orig_url=old_tracker_url, new_url=new_tracker_url)
        except qbittorrentapi.exceptions.APIError as e:
            logger.error("Failed to update tracker for %s: %s", torrent.name, str(e))
    return changes


def parse_args():
    parser = argparse.ArgumentParser(description="Modify qBittorrent trackers")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/qbt_tracker.toml"),
        help="TOML config file path, default is %(default)s",
    )
    parser.add_argument("--category", help="filter torrent.name by category")
    parser.add_argument("--tag", help="filter torrent.name by tag")
    parser.add_argument("--name-regex", help="filter torrent.name by regex pattern")
    parser.add_argument(
        "--name-glob",
        help="filter torrent.name by glob pattern",
    )
    parser.add_argument(
        "--tracker-regex",
        help="trackers URL regex pattern",
    )
    parser.add_argument(
        "--tracker-replacement",
        help="trackers URL replacement string (backreferences is ok)",
    )
    parser.add_argument(
        "--apply", action="store_true", help="apply trackers URL changes"
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def main():
    args = parse_args()

    # Load config
    default_conn_info = {
        "host": "localhost",
        "port": 8080,
        "username": "admin",
        "password": "adminadmin",
    }
    try:
        config_path = Path(args.config).expanduser()
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        conn_info = config.get("qbittorrent", default_conn_info)
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return

    # Connect and process
    with qbittorrentapi.Client(**conn_info) as client:
        try:
            client.auth_log_in()
        except qbittorrentapi.LoginFailed:
            logger.error("Failed to authenticate with qBittorrent")
            return

        name_regex = re.compile(args.name_regex) if args.name_regex else None
        torrents = filter_torrents(
            client=client,
            category=args.category,
            tag=args.tag,
            name_glob=args.name_glob,
            name_regex=name_regex,
        )

        if not torrents:
            logger.warning("No matching torrents found")
            return

        tracker_regex = re.compile(args.tracker_regex) if args.tracker_regex else None
        total_changes = 0
        for torrent in torrents:
            logger.info("Torrent: %s of type %s", torrent.name, type(torrent))
            changes = modify_torrent_tracker(
                torrent=torrent,
                tracker_regex=tracker_regex,
                tracker_replacement=args.tracker_replacement,
                apply=args.apply,
            )
            if not changes:
                continue
            total_changes += len(changes)
            if not args.apply:
                logger.info("  (Dry run - no changes made)")

        mode = "Applied" if args.apply else "Found"
        logger.info(
            "%s %d tracker changes in %d torrents",
            mode,
            total_changes,
            len(torrents),
        )


if __name__ == "__main__":
    main()
