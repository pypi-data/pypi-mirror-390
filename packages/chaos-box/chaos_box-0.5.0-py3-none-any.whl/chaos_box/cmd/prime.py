"""Generate prime numbers in a given range using parallel processing."""

# PYTHON_ARGCOMPLETE_OK

import argparse
import concurrent.futures
import math

import argcomplete


def print_matrix_formatted(lst: list[int], cols: int) -> None:
    """Print numbers in a formatted matrix.

    Args:
        lst: List of numbers to print
        cols: Number of columns
    """
    max_width = len(str(max(lst)))

    for i in range(0, len(lst), cols):
        row = lst[i : i + cols]
        formatted_row = [str(x).rjust(max_width) for x in row]
        print(" ".join(formatted_row))


def is_prime(n: int) -> bool:
    """Check if a number is prime.

    Args:
        n: Number to check

    Returns:
        True if number is prime
    """
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False

    sqrt_n = int(math.floor(math.sqrt(n)))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "end",
        nargs="?",
        default=3000,
        type=int,
        help="end point for range(start, end+1), default is %(default)s",
    )
    parser.add_argument(
        "start",
        nargs="?",
        default=1,
        type=int,
        help="start point for range(start, end+1), default is %(default)s",
    )
    parser.add_argument(
        "-j",
        "--max-workers",
        default=4,
        type=int,
        help="max workers for ProcessPoolExecutor",
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    PRIMES = []
    NUMBERS = range(args.start, args.end + 1)
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=args.max_workers
    ) as executor:
        for num, ret in zip(NUMBERS, executor.map(is_prime, NUMBERS)):
            if ret:
                PRIMES.append(num)

    print_matrix_formatted(PRIMES, 10)


if __name__ == "__main__":
    main()
