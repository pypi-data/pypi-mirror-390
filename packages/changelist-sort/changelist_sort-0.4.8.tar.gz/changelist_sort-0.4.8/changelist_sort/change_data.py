""" Dataclass containing Fields describing a File Change.
"""
from os.path import basename
from dataclasses import dataclass, field

from changelist_data.file_change import FileChange


@dataclass(frozen=True)
class ChangeData(FileChange):
    """ The Change Information that is associated with a single file.
 - This DataClass extends the Common FileChange dataclass, in order to memoize key sorting path components.

**Properties:**
 - before_path (str | None): The initial path of the file.
 - before_dir (bool | None): Whether the initial file is a directory.
 - after_path (str | None): The final path of the file.
 - after_dir (bool | None): Whether the final path is a directory.
 - sort_path (str | None): The Path to use for sorting.
 - first_dir (str | None): The First Directory in the file sort path.
 - file_basename (str | None): The basename of the file sort path.
 - file_ext (str | None): The File Extension.
    """
    sort_path: str | None = field(init=False)
    first_dir: str | None = field(init=False, default=None)
    file_basename: str | None = field(init=False, default=None)
    file_ext: str | None = field(init=False, default=None)

    def __post_init__(self):
        object.__setattr__(self, 'sort_path', self._get_sort_path())
        if self.sort_path is not None:
            object.__setattr__(self, 'first_dir', self._get_first_dir())
            object.__setattr__(self, 'file_basename', basename(self.sort_path))
            object.__setattr__(self, 'file_ext', self._get_file_ext())

    def _get_sort_path(self) -> str | None:
        """ Determine the Path to use for sorting.
        - Prefer AfterPath.
        """
        return self.after_path if self.after_path is not None else self.before_path

    def _get_first_dir(self) -> str | None:
        """ Obtain the First Directory in the file sort path.
        """
        start_idx = 1 if self.sort_path.startswith('/') else 0
        try:
            end_idx = self.sort_path.index('/', start_idx)
            return self.sort_path[start_idx:end_idx]
        except ValueError:
            return None

    def _get_file_ext(self) -> str | None:
        """ Obtain the File Extension, or None.
        """
        try:
            return self.file_basename[self.file_basename.index('.', 1) + 1:]
        except ValueError:
            return None


def expand(fc: FileChange) -> ChangeData:
    return ChangeData(
        before_path=fc.before_path,
        before_dir=fc.before_dir,
        after_path=fc.after_path,
        after_dir=fc.after_dir,
    )


def simplify(cd: ChangeData) -> FileChange:
    return FileChange(
        before_path=cd.before_path,
        before_dir=cd.before_dir,
        after_path=cd.after_path,
        after_dir=cd.after_dir,
    )
