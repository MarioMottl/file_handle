import shutil
import logging
import pathlib
import errno

from typing import Callable, Optional

logging.basicConfig(
    filename="file_handle.log",
    level=logging.INFO,
    format="%(asctime)s:%(name)s:%(message)s",
)


class SourceNotValidError(Exception):
    ...


class DestinationNotValidError(Exception):
    ...


class PermissionDeniedError(Exception):
    ...


class ReadOnlyError(Exception):
    ...


class FileHandle:
    @staticmethod
    def make_directory(path: pathlib.Path) -> Optional[bool]:
        """
        Create a directory at the specified path if it doesn't exist.

        Args:
            path: The path to the directory to create.

        Returns:
            True if the directory was created successfully or already exists, False otherwise.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except OSError as error:
            if error.errno != errno.EACCES:
                logging.error(f"{error.errno} - {error.strerror} - {error.filename}")
                raise PermissionDeniedError(
                    f"{error.errno} - {error.strerror} - {error.filename}"
                )
            elif error.errno == errno.EROFS:
                logging.error(f"{error.errno} - {error.strerror} - {error.filename}")
                raise ReadOnlyError(
                    f"{error.errno} - {error.strerror} - {error.filename}"
                )

    @staticmethod
    def remove_directory(path: pathlib.Path) -> Optional[bool]:
        """
        Remove a directory and all its contents at the specified path.

        Args:
            path: The path to the directory to remove.

        Returns:
            True if the directory was removed successfully, False otherwise.
        """
        try:
            path.rmdir()
            return True
        except OSError as error:
            if error.errno != errno.ENOTEMPTY:
                logging.error(f"{error.errno} - {error.strerror} - {error.filename}")
                raise
            else:
                for child in path.iterdir():
                    if child.is_file():
                        child.unlink()
                    else:
                        FileHandle.remove_directory(child)
                path.rmdir()
                return True

    @staticmethod
    def create_backup(path: pathlib.Path) -> Optional[bool]:
        """
        Create a backup of a file at the specified path by copying it to a new file with a .bak extension.

        Args:
            path: The path to the file to create a backup of.

        Returns:
            True if the backup was created successfully, False otherwise.
        """
        try:
            backup_path = path.with_suffix(".bak")
            FileHandle.copy(path, backup_path)
            return backup_path
        except OSError as error:
            logging.error(f"{error.errno} - {error.strerror} - {error.filename}")
            raise

    @staticmethod
    def validate_paths(source: pathlib.Path, destination: pathlib.Path) -> None:
        """
        Validate that the source and destination paths are valid for copying a file.

        Args:
            source: The path to the source file or directory.
            destination: The path to the destination file or directory.

        Returns:
            True if both paths are valid, False otherwise.
        """
        if not source.exists():
            raise SourceNotValidError(f"{source} does not exist.")
        if not destination.exists():
            raise DestinationNotValidError(f"{destination} does not exist.")

    @staticmethod
    def copy(source: pathlib.Path, destination: pathlib.Path) -> Optional[bool]:
        """
        Copy a file from the source path to the destination path.

        Args:
            source: The path to the source file.
            destination: The path to the destination file.

        Returns:
            True if the file was copied successfully, False otherwise.
        """
        try:
            shutil.copy2(source, destination)
            return True
        except OSError as error:
            logging.error(f"{error.errno} - {error.strerror} - {error.filename}")
            raise

    @staticmethod
    def transfer(
        source: pathlib.Path, destination: pathlib.Path, copy_func: Callable
    ) -> None:
        """
        Transfer a file or directory from the source path to the destination path using the specified copy function.

        Args:
            source: The path to the source file or directory.
            destination: The path to the destination file or directory.
            copy_func: The function to use for copying the file or directory.

        Raises:
            SourceNotValidError: If the source path is not valid.
            DestinationNotValidError: If the destination path is not valid and cannot be created.
            OSError: If there is an error during the file or directory copy operation.
        """
        try:
            FileHandle.validate_paths(source, destination)
        except DestinationNotValidError as error:
            try:
                FileHandle.make_directory(destination)
            except (PermissionDeniedError, ReadOnlyError) as error:
                raise DestinationNotValidError from error
        except SourceNotValidError as error:
            raise SourceNotValidError from error

        copy_func(source, destination)

    @staticmethod
    def upload(
        source: pathlib.Path, destination: pathlib.Path, copy_func: Callable = copy
    ) -> Optional[bool]:
        """
        Upload a file or directory from the source path to the destination path.

        Args:
            source: The path to the source file or directory.
            destination: The path to the destination file or directory.

        Raises:
            SourceNotValidError: If the source path is not valid.
            DestinationNotValidError: If the destination path is not valid and cannot be created.
            OSError: If there is an error during the file or directory copy operation.
        """
        FileHandle.transfer(source, destination, copy_func)
        return True

    @staticmethod
    def download(
        source: pathlib.Path, destination: pathlib.Path, copy_func: Callable = copy
    ) -> Optional[bool]:
        """
        Download a file or directory from the source path to the destination path.

        Args:
            source: The path to the source file or directory.
            destination: The path to the destination file or directory.

        Raises:
            SourceNotValidError: If the source path is not valid.
            DestinationNotValidError: If the destination path is not valid and cannot be created.
            OSError: If there is an error during the file or directory copy operation.
        """
        FileHandle.transfer(source, destination, copy_func)
        return True
