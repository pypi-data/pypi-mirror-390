from __future__ import annotations

import re
from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from fspacker.packers._entry import EntryPacker  # noqa: PLC2701
from fspacker.packers.factory import PackerFactory
from fspacker.parsers.project import Project


class TestEntryPacker:
    """Test EntryPacker class."""

    @pytest.fixture
    def mock_project(self) -> Project:
        """Create a mock project for testing.

        Returns:
            Project: A mock project instance.
        """
        project = MagicMock(spec=Project)
        project.ast_modules = set()
        project.dist_dir = Path("/fake/project/dist")
        project.project_dir = Path("/fake/project")
        project.source_file = MagicMock(spec=Path)
        project.source_file.exists.return_value = True
        project.source_file.stem = "main"
        project.normalized_name = "test_project"

        # Use configure_mock to set properties
        type(project).is_normal_project = property(lambda _: True)
        type(project).is_gui = property(lambda _: False)
        return project

    @pytest.fixture
    def mock_factory(self, mock_project: Project) -> PackerFactory:
        """Create a mock factory for testing.

        Returns:
            PackerFactory: A mock factory instance.
        """
        factory = MagicMock(spec=PackerFactory)
        factory.info = mock_project
        return factory

    @pytest.fixture
    def mock_entry_packer(self, mock_factory: PackerFactory) -> EntryPacker:
        """Create a EntryPacker instance for testing.

        Returns:
            EntryPacker: An EntryPacker instance.
        """
        return EntryPacker(mock_factory)

    def test_entry_packer_initialization(
        self,
        mock_entry_packer: EntryPacker,
    ) -> None:
        """Test EntryPacker initialization."""
        assert mock_entry_packer.NAME == "入口程序打包"
        assert isinstance(mock_entry_packer, EntryPacker)

    @patch("shutil.copy")
    @patch("pathlib.Path.open", create=True)
    @patch("pathlib.Path.exists", lambda _: True)
    @patch("platform.system", lambda: "Windows")
    @patch("pathlib.Path.chmod", lambda _, __: None)
    def test_pack_normal_project(
        self,
        mock_path_open: MagicMock,
        mock_shutil_copy: MagicMock,
        mock_entry_packer: EntryPacker,
    ) -> None:
        """Test pack method for normal project."""
        # Setup project info using configure_mock
        type(mock_entry_packer.info).is_normal_project = property(
            lambda _: False,
        )  # type: ignore  # noqa: PGH003
        type(mock_entry_packer.info).is_gui = property(lambda _: False)  # type: ignore  # noqa: PGH003

        # Re-assign source_file with a new mock that has stem
        mock_entry_packer.info.source_file = MagicMock(spec=Path)
        mock_entry_packer.info.source_file.stem = "main"
        mock_entry_packer.info.normalized_name = property(
            lambda _: "test_project",
        )  # type: ignore  # noqa: PGH003

        # Execute pack method
        mock_entry_packer.pack()

        # Assertions
        mock_shutil_copy.assert_called_once()
        mock_path_open.assert_called()  # Check that the int file was written

    @patch("shutil.copy")
    @patch("pathlib.Path.open", create=True)
    @patch("pathlib.Path.chmod", lambda _, __: None)
    def test_pack_with_qt_library(
        self,
        mock_path_open: MagicMock,
        mock_shutil_copy: MagicMock,
        mock_entry_packer: EntryPacker,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test pack method when Qt library is detected."""
        # Setup project info with Qt library
        mock_entry_packer.info.ast_modules = {"PySide2"}
        type(mock_entry_packer.info).is_gui = property(lambda _: True)  # type: ignore  # noqa: PGH003
        type(mock_entry_packer.info).is_normal_project = property(
            lambda _: True,
        )  # type: ignore  # noqa: PGH003
        # Re-assign source_file with a new mock that has stem
        mock_entry_packer.info.source_file = MagicMock(spec=Path)
        mock_entry_packer.info.source_file.stem = "main"
        mock_entry_packer.info.normalized_name = property(
            lambda _: "test_project",
        )  # type: ignore  # noqa: PGH003

        # Setup mock path exists
        monkeypatch.setattr("pathlib.Path.exists", lambda _: True)
        # Setup platform mock
        monkeypatch.setattr("platform.system", lambda: "Windows")

        # Execute pack method
        mock_entry_packer.pack()

        # Assertions
        mock_shutil_copy.assert_called_once()
        mock_path_open.assert_called()  # Check that the int file was written

    @patch("shutil.copy")
    def test_pack_without_source_file(
        self,
        mock_shutil_copy: MagicMock,
        mock_entry_packer: EntryPacker,
    ) -> None:
        """Test pack method when source file doesn't exist."""
        # Setup project info with missing source file
        mock_entry_packer.info.source_file = MagicMock(spec=Path)
        mock_entry_packer.info.source_file.exists.return_value = False

        # Execute pack method
        mock_entry_packer.pack()

        # Assertions - shutil.copy should not be called when
        # source file is invalid
        mock_shutil_copy.assert_not_called()

    @patch("shutil.copy")
    @patch("pathlib.Path.exists")
    def test_copy_os_error(
        self,
        mock_exists: MagicMock,
        mock_copy: MagicMock,
        mock_entry_packer: EntryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test copy method when shutil.copy raises an OSError."""
        mock_exists.return_value = True
        # Setup mock copy to raise an OSError
        mock_copy.side_effect = OSError("OSError")

        # Execute copy method
        with pytest.raises(OSError, match="No such file or directory"):
            mock_entry_packer.pack()

        # Assertions
        assert "复制文件失败" in caplog.text

    @patch("pathlib.Path.open")
    @patch("pathlib.Path.exists")
    def test_copy_file_not_found(
        self,
        mock_exist: MagicMock,
        mock_open: MagicMock,
        mock_entry_packer: EntryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test copy method when source file doesn't exist."""
        # Setup mock exists to return False
        mock_exist.return_value = False

        mock_entry_packer.pack()

        # Assertions
        assert re.search(r"可执行文件.*fsloader-cli.*不存在", caplog.text)
        mock_open.assert_called_once()
