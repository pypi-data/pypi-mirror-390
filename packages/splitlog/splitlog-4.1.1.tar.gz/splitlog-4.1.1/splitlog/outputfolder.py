import abc
import contextlib
import logging
import os
import stat
import types
import typing as t
from pathlib import Path


_logger = logging.getLogger(__name__)


class BinWriter(contextlib.AbstractContextManager, metaclass=abc.ABCMeta):
    """Abstract base class for writing binary data into an output file."""

    @abc.abstractmethod
    def write(self, b: bytes) -> int:
        """Writes bytes into a file and returns how many bytes were written successfully.

        :returns: number of bytes written successfully
        """
        raise NotImplementedError()


class OutputFolder(contextlib.AbstractContextManager, metaclass=abc.ABCMeta):
    """Abstract base class for output folder IO."""

    @property
    @abc.abstractmethod
    def root(self) -> Path:
        """Root path of the output folder to construct paths inside the output folder.

        :returns: root path
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def mkdir(self, path: Path) -> None:
        """Creates a subdirectory."""
        raise NotImplementedError()

    @abc.abstractmethod
    def create(self, path: Path) -> BinWriter:
        """Creates a new file and returns a writer to write to it.

        :returns: writer to write binary data into the file
        """
        raise NotImplementedError()


class FileWrapper(BinWriter):
    def __init__(self, file: t.BinaryIO):
        self._file = file

    def write(self, b: bytes) -> int:
        return self._file.write(b)

    def __enter__(self) -> "FileWrapper":
        return self

    def __exit__(
        self,
        exc: t.Union[t.Type[BaseException], None],
        value: t.Union[BaseException, None],
        tb: t.Union[types.TracebackType, None],
    ) -> t.Union[bool, None]:
        return self._file.__exit__(exc, value, tb)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    else:
        return True


class DefaultLocalFilesystemOutputFolder(OutputFolder, metaclass=abc.ABCMeta):
    """Encapsulates filesystem IO on output folders.

    This implementation is portable but unsafe to use when invoking splitlog with privileges.
    """

    FILE_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
    DIR_MODE = (
        stat.S_IRUSR
        | stat.S_IWUSR
        | stat.S_IXUSR
        | stat.S_IRGRP
        | stat.S_IXGRP
        | stat.S_IROTH
        | stat.S_IXOTH
    )

    def __init__(self, path: Path):
        self._path: Path = path.resolve()

    def __enter__(self) -> OutputFolder:
        self._path.mkdir(mode=self.DIR_MODE, exist_ok=False)
        return self

    def __exit__(
        self,
        exc: t.Union[t.Type[BaseException], None],
        value: t.Union[BaseException, None],
        tb: t.Union[types.TracebackType, None],
    ) -> t.Union[bool, None]:
        return None

    def mkdir(self, path: Path) -> None:
        real_path = self._check_paths(path)
        os.mkdir(real_path, mode=self.DIR_MODE)

    def _check_paths(self, path: Path) -> Path:
        assert not path.is_absolute(), f"Path {path} must be relative"
        real_path = Path(os.path.normpath(self._path / path))
        assert _is_relative_to(
            real_path, self._path
        ), f"Path {path} outside {self._path}"
        return real_path

    def create(self, path: Path) -> BinWriter:
        real_path = self._check_paths(path)
        return FileWrapper(open(real_path, "xb"))

    @property
    def root(self) -> Path:
        return Path()


class LinuxLocalFilesystemOutputFolder(OutputFolder):
    """Encapsulates filesystem IO on output folders.

    This implementation avoids TOCTTOU attacks using modern Linux APIs.
    """

    DIR_MODE = (
        stat.S_IRUSR
        | stat.S_IWUSR
        | stat.S_IXUSR
        | stat.S_IRGRP
        | stat.S_IXGRP
        | stat.S_IROTH
        | stat.S_IXOTH
    )
    FILE_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

    @staticmethod
    def is_supported() -> bool:
        for flag in ("O_PATH", "O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC"):
            if not hasattr(os, flag):
                _logger.debug(f"os.{flag} not supported")
                return False

        for needs_dir_fd_support in (os.open, os.mkdir):
            if needs_dir_fd_support not in os.supports_dir_fd:
                _logger.debug(f"{needs_dir_fd_support} does not support dir fds")
                return False

        return True

    def __init__(self, path: Path):
        assert (
            self.is_supported()
        ), "File system semantics are not supported by runtime environment"
        self._path: Path = path.resolve()
        self._dir_fd: t.Union[int, None] = None

    def __enter__(
        self,
    ) -> OutputFolder:
        # split path
        parent = self._path.parent
        name = self._path.name

        # allow parent folder to be a symlink
        parent_dir_fd = self._open_dir_fd(parent, no_follow=False)

        try:
            os.mkdir(name, mode=self.DIR_MODE, dir_fd=parent_dir_fd)
            self._dir_fd = self._open_dir_fd(name, no_follow=True, dir_fd=parent_dir_fd)
            return self
        finally:
            os.close(parent_dir_fd)

    def __exit__(
        self,
        exc: t.Union[t.Type[BaseException], None],
        value: t.Union[BaseException, None],
        tb: t.Union[types.TracebackType, None],
    ) -> t.Union[bool, None]:
        if self._dir_fd is not None:
            saved, self._dir_fd = self._dir_fd, None
            os.close(saved)
        return None

    @property
    def root(self) -> Path:
        return Path()

    def mkdir(self, path: Path) -> None:
        real_path = self._ensure_path_under_root(path)
        os.mkdir(real_path, mode=self.DIR_MODE, dir_fd=self._dir_fd)

    def _opener(self, path: str, flags: int) -> int:
        return os.open(
            path,
            flags | getattr(os, "O_NOFOLLOW") | getattr(os, "O_CLOEXEC"),
            mode=self.FILE_MODE,
            dir_fd=self._dir_fd,
        )

    def create(self, path: Path) -> BinWriter:
        real_path = self._ensure_path_under_root(path)
        return FileWrapper(open(path, "xb", opener=self._opener))

    def _ensure_path_under_root(self, path: Path) -> Path:
        assert not path.is_absolute(), f"Path {path} must be relative"

        # remove all ".." and "." components
        real_path = Path(os.path.normpath(self._path / path))

        # assert resulting absolute path is still inside self._path
        assert _is_relative_to(
            real_path, self._path
        ), f"Path {path} outside {self._path}"
        return real_path.relative_to(self._path)

    @staticmethod
    def _open_dir_fd(
        path: t.Union[Path, str], no_follow: bool, dir_fd: t.Optional[int] = None
    ) -> int:
        flags = (
            getattr(os, "O_PATH")
            | getattr(os, "O_DIRECTORY")
            | getattr(os, "O_CLOEXEC")
        )

        if no_follow:
            flags |= getattr(os, "O_NOFOLLOW")

        return os.open(path, flags, dir_fd=dir_fd)


def new_output_folder(path: Path) -> OutputFolder:
    """Chooses an output folder implementation and creates an instance."""
    if LinuxLocalFilesystemOutputFolder.is_supported():
        return LinuxLocalFilesystemOutputFolder(path=path)
    else:
        return DefaultLocalFilesystemOutputFolder(path=path)
