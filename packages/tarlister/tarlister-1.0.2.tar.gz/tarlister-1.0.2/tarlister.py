#!/usr/bin/env python3
# SPDX-license-identifier: EUPL-1.2
# Copyright 2025 Marcus Müller
#
"""read entries from a tape archive (or other libarchive supported format)"""

import libarchive
import pathlib

# Just to make the type annotations prettier
from typing import TypeVar, Callable


def tarlister(path: pathlib.Path, howmany: int = 0, block_size: int = 0) -> None:
    kwargs = dict()
    if block_size:
        kwargs["block_size"] = block_size
    with libarchive.file_reader(str(path), **kwargs) as archive:
        counter = 0
        for entry in archive:
            print(entry)
            counter += 1
            if howmany and counter >= howmany:
                break


# == HELPERS ==
# Just generic placeholder argument types
in_type = TypeVar("In")
out_type = TypeVar("Out")


def condition_checking_converter(
    converter: Callable[[in_type], out_type],
    predicate: Callable[[out_type], bool],
    exception_type: Exception = ValueError,
) -> Callable[[in_type], out_type]:
    """Generate converter functions that have a condition on the value
    (post-conversion)

    Example: we want to coerce things to floats, but make sure they're strictly
    positive:

    func = condition_or_value_error(float, lambda x: x > 0)
    """

    def predicate_converter(value: in_type) -> out_type:
        """Converts `value` and checks whether result fulfills `predicate`"""
        converted = converter(value)
        if not predicate(converted):
            raise exception_type()
        return converted

    return predicate_converter


nonnegative_int = condition_checking_converter(int, lambda f: f >= 0)


# == Launcher ==
def main():
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "ARCHIVE", type=pathlib.Path, help="Archive (or tape device) to read"
    )
    parser.add_argument(
        "-n",
        "--how-many",
        type=nonnegative_int,
        default=0,
        help="After how many entries stop reading? (0: don't stop before EOF)",
    )
    parser.add_argument(
        "-b",
        "--block-size",
        type=nonnegative_int,
        default=0,
        help="Archive reader block size (0: use libarchive-c default block size)",
    )
    args = parser.parse_args()
    tarlister(args.ARCHIVE, args.how_many, args.block_size)


if __name__ == "__main__":
    main()
