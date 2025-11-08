"""Display network interface statistics like bytes and packets transferred."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import re

import argcomplete
import psutil


def convert_bytes(bytes: int) -> str:
    """Convert bytes to human readable format.

    Args:
        bytes: Number of bytes

    Returns:
        Formatted string with units
    """
    if bytes >= 2**40:
        return f"{bytes / 2**40:7.2f} TiB"
    else:
        return f"{bytes / 2**30:7.2f} GiB"


def format_packets(packets: int) -> str:
    """Format packet count with scientific notation.

    Args:
        packets: Number of packets

    Returns:
        Formatted packet count string
    """
    if packets >= 1000000:
        return f"{packets:8.2e} packets"
    else:
        return f"{packets:8d} packets"


def get_net_stats(pattern: re.Pattern) -> None:
    """Get and display network interface statistics.

    Args:
        pattern: Regex pattern to filter interfaces
    """
    net_io_counters = psutil.net_io_counters(pernic=True)
    filtered_interfaces = [
        interface for interface in net_io_counters if pattern.search(interface)
    ]
    if len(filtered_interfaces) <= 0:
        return

    max_interface_len = max(len(interface) for interface in filtered_interfaces)
    for interface, stats in net_io_counters.items():
        if pattern.search(interface):
            print(
                f"{interface:{max_interface_len}} : RX {convert_bytes(stats.bytes_recv)}, {format_packets(stats.packets_recv)}, TX {convert_bytes(stats.bytes_sent)}, {format_packets(stats.packets_sent)}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Display network interface statistics."
    )
    parser.add_argument(
        "pattern", nargs="?", default=".*", help="Filter interfaces by regex"
    )
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    pattern = re.compile(args.pattern)
    get_net_stats(pattern)


if __name__ == "__main__":
    main()
