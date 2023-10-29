import pathlib
import tempfile
import pytest

from file_handle import FileHandle, SourceNotValidError, DestinationNotValidError


class TestFileHandle:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.valid_file_path = pathlib.Path(self.temp_dir.name) / "valid_file.txt"
        self.valid_dir_path = pathlib.Path(self.temp_dir.name) / "valid_dir"
        self.invalid_file_path = pathlib.Path(self.temp_dir.name) / "invalid_file.txt"
        self.invalid_dir_path = (
            pathlib.Path(self.temp_dir.name) / "invalid_dir" / "invalid_file.txt"
        )
        self.valid_file_path.touch()
        self.valid_dir_path.mkdir()
        (self.valid_dir_path / "test_file.txt").touch()
        (self.valid_dir_path / "test_subdir").mkdir()
        (self.valid_dir_path / "test_subdir" / "test_file.txt").touch()

    def teardown_method(self):
        self.temp_dir.cleanup()

    def test_make_directory(self):
        path = pathlib.Path(self.temp_dir.name) / "test_dir"
        assert FileHandle.make_directory(path)
        assert path.is_dir()

    def test_remove_directory(self):
        path = self.valid_dir_path
        assert FileHandle.remove_directory(path)
        assert not path.exists()

    def test_create_backup(self):
        source_path = self.valid_file_path
        backup_path = FileHandle.create_backup(source_path)
        assert backup_path.exists()
        assert backup_path.is_file()

    def test_validate_paths(self):
        # Test valid paths
        assert (
            FileHandle.validate_paths(self.valid_file_path, self.valid_dir_path) is None
        )
        assert (
            FileHandle.validate_paths(self.valid_dir_path, self.valid_file_path) is None
        )

        # Test invalid source paths
        with pytest.raises(SourceNotValidError):
            FileHandle.validate_paths(self.invalid_file_path, self.valid_dir_path)

        # Test invalid destination paths
        with pytest.raises(DestinationNotValidError):
            FileHandle.validate_paths(self.valid_file_path, self.invalid_dir_path)

        # Test invalid source and destination paths
        with pytest.raises(SourceNotValidError):
            FileHandle.validate_paths(self.invalid_file_path, self.invalid_dir_path)

    def test_upload(self):
        source_path = self.valid_file_path
        destination_path = pathlib.Path(self.temp_dir.name) / "test_dir"
        assert FileHandle.upload(source_path, destination_path)

        # Test invalid source path
        with pytest.raises(SourceNotValidError):
            FileHandle.upload(self.invalid_file_path, destination_path)

    def test_download(self):
        source_path = self.valid_file_path
        destination_path = pathlib.Path(self.temp_dir.name) / "test_dir"
        assert FileHandle.download(source_path, destination_path)

        # Test invalid source path
        with pytest.raises(SourceNotValidError):
            FileHandle.download(self.invalid_file_path, destination_path)
