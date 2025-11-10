import logging
import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import BinaryIO, Optional, Set

from dateutil.parser import parse as parse_date

from splitlog.outputfolder import OutputFolder

logger = logging.getLogger(__name__)


class _State(Enum):
    NEW_CONTAINER = 1
    CONTAINER_LOGS = 2
    NON_EMPTY_LOG = 3
    EMPTY_LOG = 4
    FINAL = 5


class ParseError(Exception):
    pass


class _Splitter(object):
    _CONTAINER_LOG_HEADER = re.compile(
        r"""^Container: (?P<container>[^ ]+) on (?P<host>[^_]+)_(?P<port>\d+)$"""
    )
    _LOG_AGGREGATION_TYPE = "LogAggregationType: AGGREGATED"
    _CONTAINER_LOGS_DELIMITER = re.compile(
        r"""^======================================+$"""
    )
    _LOG_TYPE_START = re.compile(r"""^LogType:(?P<filename>.+)$""")
    _LOG_LAST_MODIFIED_TIME = re.compile(
        r"""^LogLastModifiedTime:(?P<date_string>.+)$"""
    )
    _LOG_LENGTH = re.compile(r"""^LogLength:(?P<length>\d+)$""")
    _LOG_CONTENTS = r"LogContents:"
    _EMPTY_LINE = ""
    _LOG_TYPE_END = re.compile(r"""^End of LogType:(?P<filename>.+)$""")
    _CONTAINER_LOG_DELIMITER = re.compile(
        r"""^\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*+$"""
    )

    def __init__(
        self: "_Splitter", infile: BinaryIO, output_folder: OutputFolder
    ) -> None:
        self.container: Optional[str] = None
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.filename: Optional[str] = None
        self.last_modified: Optional[datetime] = None
        self.length: Optional[int] = None
        self.dirs_created: Set[Path] = set()
        self.infile: BinaryIO = infile
        self.output_folder: OutputFolder = output_folder
        self.offset: int = 0
        self.line: Optional[str] = None
        self.eof: bool = False
        self.state: _State = _State.NEW_CONTAINER
        self.push_back: bool = False

    def split(self: "_Splitter"):
        while not self.state == _State.FINAL:
            self._parse()

    def _parse(self: "_Splitter") -> None:
        if self.state == _State.NEW_CONTAINER:
            new_state = self._new_container()
        elif self.state == _State.CONTAINER_LOGS:
            new_state = self._container_logs()
        elif self.state == _State.NON_EMPTY_LOG:
            new_state = self._non_empty_log()
        elif self.state == _State.EMPTY_LOG:
            new_state = self._empty_log()
        else:
            raise Exception(f"Unhandled state {self.state}")

        logger.debug(
            "Transition from %s to %s (offset: %d, input: %r)",
            self.state,
            new_state,
            self.offset,
            self.line,
        )

        if new_state == _State.NEW_CONTAINER:
            self.container = None
            self.host = None
            self.port = None
            self.last_modified = None
            self.filename = None
            self.length = None
        elif new_state == _State.CONTAINER_LOGS:
            self.last_modified = None
            self.filename = None
            self.length = None
        elif new_state == _State.NON_EMPTY_LOG:
            self.last_modified = None
            self.filename = None
            self.length = None
        elif new_state == _State.EMPTY_LOG:
            self.last_modified = None
            self.filename = None
            self.length = None
        elif new_state == _State.FINAL:
            self.container = None
            self.host = None
            self.port = None
            self.last_modified = None
            self.filename = None
            self.length = None
        else:
            raise Exception(f"Unknown state {new_state}")

        self.state = new_state

    def _new_container(self: "_Splitter") -> _State:
        line = self._next_line()
        matched = _Splitter._CONTAINER_LOG_HEADER.match(line)
        if not matched:
            raise self._parse_error("Was expecting container log header")
        self.container = matched.group("container")
        self.host = matched.group("host")
        self.port = int(matched.group("port"))
        line = self._next_line()
        if _Splitter._LOG_AGGREGATION_TYPE != line.rstrip():
            raise self._parse_error("Was expecting log aggregation type")
        line = self._next_line()
        matched = _Splitter._CONTAINER_LOGS_DELIMITER.match(line)
        if not matched:
            raise self._parse_error(
                "Was expecting container logs delimiter: ================"
            )
        return _State.CONTAINER_LOGS

    def _container_logs(self: "_Splitter") -> _State:
        line = self._optional_next_line()
        if line is None:
            return _State.FINAL
        log_type_start_matched = _Splitter._LOG_TYPE_START.match(line)
        log_type_end_matched = _Splitter._LOG_TYPE_END.match(line)
        container_log_header_matched = _Splitter._CONTAINER_LOG_HEADER.match(line)
        if log_type_start_matched:
            self._push_back()
            return _State.NON_EMPTY_LOG
        elif container_log_header_matched:
            self._push_back()
            return _State.NEW_CONTAINER
        elif log_type_end_matched:
            self._push_back()
            return _State.EMPTY_LOG
        elif _Splitter._EMPTY_LINE == line.rstrip():
            return _State.EMPTY_LOG
        else:
            raise self._parse_error("Was expecting a container log or a new container")

    def _non_empty_log(self: "_Splitter") -> _State:
        line = self._next_line()
        matched = _Splitter._LOG_TYPE_START.match(line)
        if matched:
            self.filename = matched.group("filename")

        line = self._next_line()
        matched = _Splitter._LOG_LAST_MODIFIED_TIME.match(line)
        if not matched:
            raise self._parse_error("Was expecting log last modified time")
        date_string = matched.group("date_string")
        try:
            self.last_modified = parse_date(date_string)
        except ValueError as e:
            raise self._parse_error(
                'Could not parse last modified time "%s"', date_string
            ) from e
        except OverflowError as e:
            raise self._parse_error(
                'Last modified time "%s" cannot be expressed on this machine',
                date_string,
            ) from e

        line = self._next_line()
        matched = _Splitter._LOG_LENGTH.match(line)
        if not matched:
            raise self._parse_error("Was expecting log length")
        self.length = int(matched.group("length"))

        line = self._next_line()
        if _Splitter._LOG_CONTENTS != line.rstrip():
            raise self._parse_error("Was expecting log contents")

        self._copy()
        logger.info(
            "Created logfile %s for container %s, running on host %s",
            self.filename,
            self.container,
            self.host,
        )

        line = self._next_line()
        if _Splitter._EMPTY_LINE == line.rstrip():
            line = self._next_line()

        matched = _Splitter._LOG_TYPE_END.match(line)
        if not matched:
            raise self._parse_error(f"Was expecting end of log but got {line.rstrip()}")
        filename = matched.group("filename")
        if not self.filename == filename:
            raise self._parse_error(
                "Was expecting filename %s but got %s", self.filename, filename
            )

        line = self._next_line()
        matched = _Splitter._CONTAINER_LOG_DELIMITER.match(line)
        if not matched:
            raise self._parse_error(
                "Was expecting container log delimiter (**************** line)"
            )

        line = self._next_line()
        if _Splitter._EMPTY_LINE != line.rstrip():
            raise self._parse_error("Was expecting empty line")

        return _State.CONTAINER_LOGS

    def _empty_log(self: "_Splitter") -> _State:
        line = self._next_line()
        matched = _Splitter._LOG_TYPE_END.match(line)
        if not matched:
            raise self._parse_error("Was expecting end of log")
        self.filename = matched.group("filename")
        self._create_empty()

        line = self._next_line()
        matched = _Splitter._CONTAINER_LOG_DELIMITER.match(line)
        if not matched:
            raise self._parse_error(
                "Was expecting container log delimiter (**************** line)"
            )

        line = self._next_line()
        if _Splitter._EMPTY_LINE != line.rstrip():
            raise self._parse_error("Was expecting empty line")

        return _State.CONTAINER_LOGS

    def _create_hierarchy(self: "_Splitter") -> Path:
        assert self.host is not None, "host must be present"
        host_dir = self.output_folder.root / self.host
        if host_dir not in self.dirs_created:
            self.output_folder.mkdir(host_dir)
            self.dirs_created.add(host_dir)
        assert self.container is not None, "container must be present"
        container_dir = host_dir / self.container
        if container_dir not in self.dirs_created:
            self.output_folder.mkdir(container_dir)
            self.dirs_created.add(container_dir)
        return container_dir

    def _create_empty(self: "_Splitter") -> None:
        container_dir = self._create_hierarchy()
        assert self.filename, "filename must be present"
        log_path = container_dir / self.filename

        with self.output_folder.create(log_path) as outfile:
            logger.debug("Created empty log file %s", log_path)

    def _copy(self: "_Splitter") -> None:
        container_dir = self._create_hierarchy()
        assert self.filename, "filename must be present"
        log_path = container_dir / self.filename
        with self.output_folder.create(log_path) as outfile:
            assert self.length is not None, "length must be present"
            logger.debug("Created log file %s, size: %d", log_path, self.length)
            remaining = self.length
            while remaining > 0:
                data = self.infile.read(remaining)
                if len(data) == 0:
                    raise self._parse_error("Unexpected end-of-file while copying log")
                while len(data) > 0:
                    written = outfile.write(data)
                    remaining -= written
                    self.offset += written
                    data = data[written:]
            logger.debug("Copied %d bytes", self.length)

    def _readline(self: "_Splitter") -> None:
        line = self.infile.readline()
        self.offset += len(line)
        if line == b"":
            self.eof = True
            self.line = None
            logger.debug("End of file detected at offset %d", self.offset)
        else:
            self.line = line.decode(encoding="utf-8", errors="strict")
            logger.log(5, "Read line ending at %d, eof: %s", self.offset, self.eof)

    def _push_back(self: "_Splitter") -> None:
        self.push_back = True
        logger.debug("Pushed line before offset %d back", self.offset)

    def _next_line(self: "_Splitter") -> str:
        line = self._optional_next_line()
        if line is None:
            raise self._parse_error("Unexpected end of file")
        return line

    def _optional_next_line(self: "_Splitter") -> Optional[str]:
        if self.push_back:
            self.push_back = False
            return self.line
        else:
            self._readline()
            return self.line if not self.eof else self.line

    def _parse_error(self: "_Splitter", fmt: str, *args):
        plain_msg = fmt % args
        msg = f"Could not parse log file (offset: {self.offset}, input: {self.line!r}): {plain_msg}"
        parse_error = ParseError(msg)
        return parse_error


def split(infile: BinaryIO, output_folder: OutputFolder) -> None:
    splitter = _Splitter(infile=infile, output_folder=output_folder)

    splitter.split()
