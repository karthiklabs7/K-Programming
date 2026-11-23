"""K 1.0 safe file handling runtime."""

from pathlib import Path


class KFileError(Exception):
    pass


class KFileSystem:
    def __init__(self, root="."):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name):
        try:
            candidate = (self.root / str(name)).resolve()
            candidate.relative_to(self.root)
        except (ValueError, OSError, RuntimeError) as error:
            raise KFileError("Path is outside the allowed directory") from error
        return candidate

    def exists(self, name):
        return self._path(name).exists()

    def read(self, name, encoding="utf-8"):
        path = self._path(name)
        if not path.is_file():
            raise KFileError(f"File not found: {name}")
        try:
            return path.read_text(encoding=encoding)
        except (OSError, UnicodeError) as error:
            raise KFileError(str(error)) from error

    def write(self, name, content, encoding="utf-8"):
        path = self._path(name)
        if path.exists() and path.is_dir():
            raise KFileError("Cannot write to a directory")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(content), encoding=encoding)
            return True
        except (OSError, UnicodeError) as error:
            raise KFileError(str(error)) from error

    def append(self, name, content, encoding="utf-8"):
        path = self._path(name)
        if path.exists() and path.is_dir():
            raise KFileError("Cannot append to a directory")
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding=encoding) as handle:
                handle.write(str(content))
            return True
        except (OSError, UnicodeError) as error:
            raise KFileError(str(error)) from error

    def mkdir(self, name):
        path = self._path(name)
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except OSError as error:
            raise KFileError(str(error)) from error

    def list_dir(self, name="."):
        path = self._path(name)
        if not path.is_dir():
            raise KFileError(f"Directory not found: {name}")
        try:
            return sorted(item.name for item in path.iterdir())
        except OSError as error:
            raise KFileError(str(error)) from error


def k_file_system(root="."):
    return KFileSystem(root)


FILE_BUILTINS = {
    "file_exists": lambda fs, name: fs.exists(name),
    "read_file": lambda fs, name: fs.read(name),
    "write_file": lambda fs, name, data: fs.write(name, data),
    "append_file": lambda fs, name, data: fs.append(name, data),
    "make_dir": lambda fs, name: fs.mkdir(name),
    "list_dir": lambda fs, name=".": fs.list_dir(name),
}
