import argparse
import sys
from importlib.metadata import distribution
from pathlib import Path
from typing import BinaryIO, List, NamedTuple, Optional

_NAME = "splitlog"


class _Arguments(NamedTuple):
    """
    Parsed command line arguments.
    """

    output_folder: Optional[Path]
    input_file: Optional[Path]
    verbose: Optional[bool]
    version: Optional[bool]


def _create_parser() -> argparse.ArgumentParser:
    def input_file(s: Optional[str]) -> Optional[Path]:
        if s is None:
            return None

        return Path(s)

    result = argparse.ArgumentParser(
        prog=_NAME,
        description="Utility to split aggregated logs from Apache Hadoop Yarn applications into a folder hierarchy",
    )
    result.add_argument(
        "-v",
        "--verbose",
        default=False,
        action="store_true",
        dest="verbose",
        help="enable debug logging",
    )
    result.add_argument(
        "-i",
        "--input-file",
        type=input_file,
        metavar="FILE",
        dest="input_file",
        help="yarn log file to split (default; stdin)",
    )
    result.add_argument(
        "-V",
        "--version",
        default=False,
        action="store_true",
        dest="version",
        help="output version information and exit",
    )
    result.add_argument(
        "output_folder",
        default="out",
        type=Path,
        metavar="DIR",
        help="folder to store split logs to (default: %(default)s)",
        nargs="?",
    )
    return result


def _bind_arguments(ns: argparse.Namespace) -> _Arguments:
    return _Arguments(**vars(ns))


def _parse_args(args: List[str]) -> _Arguments:
    parser = _create_parser()
    ns = parser.parse_args(args)
    return _bind_arguments(ns)


def _error_exit(error: Exception) -> None:
    print(error, file=sys.stderr)
    exit(1)


def _open_input(file: Optional[Path]) -> BinaryIO:
    if file is not None:
        return file.open("rb")
    else:
        return sys.stdin.buffer


def _version_exit():
    metadata = distribution(_NAME)

    version = metadata.version
    license = metadata.read_text("LICENSE")

    if license:
        print(f"{_NAME} {version}\n\n{license}")
    else:
        print(f"{_NAME} {version}")

    exit(0)


def main(cli_args: Optional[List[str]] = None) -> None:
    import sys

    if cli_args is None:
        cli_args = sys.argv[1:]

    args = _parse_args(cli_args)

    import logging

    # defer logging initialisation until arguments are being parsed
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    logger.debug("Effective arguments: %s", args)

    if args.version:
        _version_exit()

    assert args.output_folder is not None, "output_folder argument must be present"

    from splitlog import split, ParseError
    from splitlog.outputfolder import new_output_folder

    with _open_input(args.input_file) as infile:
        try:
            with new_output_folder(args.output_folder) as output_folder:
                split(infile, output_folder)
        except FileNotFoundError as e:
            _error_exit(e)
        except FileExistsError as e:
            _error_exit(e)
        except ParseError as e:
            logger.debug("Exception caught", exc_info=e)
            _error_exit(e)


if __name__ == "__main__":
    main()
