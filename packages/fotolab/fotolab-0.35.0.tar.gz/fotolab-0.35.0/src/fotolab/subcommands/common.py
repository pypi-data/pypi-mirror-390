# Copyright (C) 2024,2025 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
#
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Common argument parsing for subcommands."""

import argparse
import logging
from functools import wraps
from typing import Callable

log = logging.getLogger(__name__)


def log_args_decorator(func: Callable) -> Callable:
    """Decorator to log the arguments passed to a function."""

    @wraps(func)
    def wrapper(args: argparse.Namespace) -> None:
        log.debug(args)
        return func(args)

    return wrapper


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    """Add common arguments to a subparser.

    Args:
        parser (argparse.ArgumentParser): The subparser to add arguments to.
    """
    parser.add_argument(
        dest="image_paths",
        help="set the image filenames",
        nargs="+",
        type=str,
        default=None,
        metavar="IMAGE_PATHS",
    )

    parser.add_argument(
        "-op",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help="open the image using default program (default: '%(default)s')",
    )

    parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )
