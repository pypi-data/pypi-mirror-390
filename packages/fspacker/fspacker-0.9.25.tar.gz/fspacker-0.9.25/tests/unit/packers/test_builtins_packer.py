from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from fspacker.packers._builtins import BuiltinsPacker  # noqa: PLC2701
from fspacker.packers.factory import PackerFactory
from fspacker.parsers.project import Project


class TestBuiltinsPacker:
    """Test BuiltinsPacker class."""

    @pytest.fixture
    def mock_project(self) -> Project:
        """Create a mock project for testing.

        Returns:
            Project: A mock project instance.
        """
        project = MagicMock(spec=Project)
        project.ast_modules = set()
        project.dist_dir = Path("/fake/dist")
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
    def builtins_packer(self, mock_factory: PackerFactory) -> BuiltinsPacker:
        """Create a BuiltinsPacker instance for testing.

        Returns:
            BuiltinsPacker: A BuiltinsPacker instance.
        """
        return BuiltinsPacker(mock_factory)

    def test_builtins_packer_initialization(
        self,
        builtins_packer: BuiltinsPacker,
    ) -> None:
        """Test BuiltinsPacker initialization."""
        assert builtins_packer.NAME == "内置依赖库打包"
        assert isinstance(builtins_packer, BuiltinsPacker)

    @patch("fspacker.packers._builtins.get_settings")
    @patch("fspacker.packers._builtins.shutil.unpack_archive")
    def test_pack_with_use_tk_true(
        self,
        mock_unpack_archive: MagicMock,
        mock_get_settings: MagicMock,
        builtins_packer: BuiltinsPacker,
    ) -> None:
        """Test pack method when use_tk mode is True."""
        # Setup mock settings
        mock_settings = MagicMock()
        mock_settings.mode.use_tk = True
        mock_settings.assets_dir = Path("/fake/assets")
        mock_settings.tk_libs = {"tkinter"}
        mock_get_settings.return_value = mock_settings

        # Execute pack method
        builtins_packer.pack()

        # Assertions
        assert mock_unpack_archive.call_count == 2  # noqa: PLR2004
        mock_unpack_archive.assert_any_call(
            Path("/fake/assets/tkinter-lib.zip"),
            builtins_packer.info.dist_dir,
            "zip",
        )
        mock_unpack_archive.assert_any_call(
            Path("/fake/assets/tkinter.zip"),
            builtins_packer.info.dist_dir / "site-packages",
            "zip",
        )

    @patch("fspacker.packers._builtins.get_settings")
    @patch("fspacker.packers._builtins.shutil.unpack_archive")
    def test_pack_without_tk(
        self,
        mock_unpack_archive: MagicMock,
        mock_get_settings: MagicMock,
        builtins_packer: BuiltinsPacker,
    ) -> None:
        """Test pack method when no tkinter dependency or mode."""
        # Setup mock settings
        mock_settings = MagicMock()
        mock_settings.mode.use_tk = False
        mock_settings.assets_dir = Path("/fake/assets")
        mock_settings.tk_libs = {"tkinter"}
        mock_get_settings.return_value = mock_settings

        # Execute pack method
        builtins_packer.pack()

        # Assertions
        mock_unpack_archive.assert_not_called()

    @patch("fspacker.packers._builtins.get_settings")
    @patch("fspacker.packers._builtins.shutil.unpack_archive")
    def test_pack_with_tkinter_dependency(
        self,
        mock_unpack_archive: MagicMock,
        mock_get_settings: MagicMock,
        builtins_packer: BuiltinsPacker,
        mock_project: Project,
    ) -> None:
        """Test pack method when tkinter dependency is detected."""
        # Setup mock project with tkinter dependency
        mock_project.ast_modules = {"tkinter"}

        # Setup mock settings
        mock_settings = MagicMock()
        mock_settings.mode.use_tk = False
        mock_settings.assets_dir = Path("/fake/assets")
        mock_settings.tk_libs = {"tkinter"}
        mock_get_settings.return_value = mock_settings

        # Execute pack method
        builtins_packer.pack()

        # Assertions
        assert mock_unpack_archive.call_count == 2  # noqa: PLR2004
        mock_unpack_archive.assert_any_call(
            Path("/fake/assets/tkinter-lib.zip"),
            builtins_packer.info.dist_dir,
            "zip",
        )
        mock_unpack_archive.assert_any_call(
            Path("/fake/assets/tkinter.zip"),
            builtins_packer.info.dist_dir / "site-packages",
            "zip",
        )

    @patch("fspacker.packers._builtins.get_settings")
    @patch("fspacker.packers._builtins.shutil.unpack_archive")
    def test_pack_with_matplotlib_dependency(
        self,
        mock_unpack_archive: MagicMock,
        mock_get_settings: MagicMock,
        builtins_packer: BuiltinsPacker,
        mock_project: Project,
    ) -> None:
        """Test pack method when matplotlib dependency is detected."""
        # Setup mock project with matplotlib dependency
        mock_project.ast_modules = {"matplotlib"}

        # Setup mock settings
        mock_settings = MagicMock()
        mock_settings.mode.use_tk = False
        mock_settings.assets_dir = Path("/fake/assets")
        mock_settings.tk_libs = {"matplotlib", "tkinter"}
        mock_get_settings.return_value = mock_settings

        # Execute pack method
        builtins_packer.pack()

        # Assertions
        assert mock_unpack_archive.call_count == 2  # noqa: PLR2004
        mock_unpack_archive.assert_any_call(
            Path("/fake/assets/tkinter-lib.zip"),
            builtins_packer.info.dist_dir,
            "zip",
        )
        mock_unpack_archive.assert_any_call(
            Path("/fake/assets/tkinter.zip"),
            builtins_packer.info.dist_dir / "site-packages",
            "zip",
        )
