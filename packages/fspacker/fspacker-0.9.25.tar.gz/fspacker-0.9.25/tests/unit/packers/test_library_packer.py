from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from packaging.requirements import Requirement

from fspacker.packers._library import LibraryPacker  # noqa: PLC2701
from fspacker.packers.factory import PackerFactory
from fspacker.parsers.project import Project


class TestLibraryPacker:
    """Test LibraryPacker class."""

    @pytest.fixture
    def mock_project(self) -> Project:
        """Create a mock project for testing.

        Returns:
            Project: A mock project instance.
        """
        project = MagicMock(spec=Project)
        project.dependencies = ["requests==2.28.1", "click>=8.0"]
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
    def library_packer(self, mock_factory: PackerFactory) -> LibraryPacker:
        """Create a LibraryPacker instance for testing.

        Returns:
            LibraryPacker: A LibraryPacker instance.
        """
        # Clear packed_libs set before each test
        LibraryPacker.packed_libs.clear()
        return LibraryPacker(mock_factory)

    def test_library_packer_initialization(
        self,
        library_packer: LibraryPacker,
    ) -> None:
        """Test LibraryPacker initialization."""
        assert library_packer.NAME == "依赖库打包"
        assert isinstance(library_packer, LibraryPacker)
        assert hasattr(library_packer, "packed_libs")

    @patch("fspacker.packers._library.RequirementParser.parse")
    def test_pack_with_invalid_requirement(
        self,
        mock_parse: MagicMock,
        library_packer: LibraryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test pack method when requirement parsing fails."""
        # Setup mock to return None (invalid requirement)
        mock_parse.return_value = None

        # Execute pack method
        library_packer.pack()

        # Assertions
        assert "解析依赖失败" in caplog.text
        assert mock_parse.call_count == 2  # noqa: PLR2004

    @patch("fspacker.packers._library.analyze_package_deps")
    @patch("fspacker.packers._library.install_package")
    @patch("fspacker.packers._library.download_to_libs_dir")
    @patch("fspacker.packers._library.get_cached_package")
    @patch("fspacker.packers._library.RequirementParser.parse")
    @patch("pathlib.Path.is_file", lambda _: True)
    @patch("pathlib.Path.exists", lambda _: True)
    def test_pack_with_cached_package(  # noqa: PLR0913, PLR0917
        self,
        mock_parse: MagicMock,
        mock_get_cached_package: MagicMock,
        mock_download_to_libs_dir: MagicMock,
        mock_install_package: MagicMock,
        mock_analyze_package_deps: MagicMock,
        library_packer: LibraryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test pack method when cached package exists."""
        # Setup mocks
        req = Requirement("requests==2.28.1")
        mock_parse.return_value = req

        # Mock cached package exists
        cached_file = Path("/fake/libs/requests-2.28.1-py3-none-any.whl")
        mock_get_cached_package.return_value = cached_file

        # Mock secondary dependencies
        secondary_req = Requirement("urllib3>=1.21.1")
        mock_analyze_package_deps.return_value = [secondary_req]

        # Execute pack method
        library_packer.pack()

        # Assertions
        assert mock_parse.call_count == 2  # noqa: PLR2004

        mock_get_cached_package.assert_called_with(secondary_req)
        mock_download_to_libs_dir.assert_not_called()

        assert mock_install_package.call_count == 2  # noqa: PLR2004
        mock_analyze_package_deps.assert_called_once_with(cached_file)

        # Check that both top-level and secondary dependencies are installed
        calls = mock_install_package.call_args_list
        assert len(calls) == 2  # noqa: PLR2004
        assert "打包依赖" in caplog.text
        assert "找到本地满足要求的依赖" in caplog.text

    @patch("fspacker.packers._library.analyze_package_deps")
    @patch("fspacker.packers._library.install_package")
    @patch("fspacker.packers._library.download_to_libs_dir")
    @patch("fspacker.packers._library.get_cached_package")
    @patch("fspacker.packers._library.RequirementParser.parse")
    @patch("pathlib.Path.is_file", lambda _: True)
    @patch("pathlib.Path.exists", lambda _: True)
    def test_pack_without_cached_package(  # noqa: PLR0913, PLR0917
        self,
        mock_parse: MagicMock,
        mock_get_cached_package: MagicMock,
        mock_download_to_libs_dir: MagicMock,
        mock_install_package: MagicMock,
        mock_analyze_package_deps: MagicMock,
        library_packer: LibraryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test pack method when cached package does not exist."""
        # Setup mocks
        req = Requirement("requests==2.28.1")
        mock_parse.return_value = req

        # Mock no cached package exists
        mock_get_cached_package.return_value = None

        # Mock downloaded file
        downloaded_file = Path("/fake/libs/requests-2.28.1-py3-none-any.whl")
        mock_download_to_libs_dir.return_value = downloaded_file

        # Mock secondary dependencies
        secondary_req = Requirement("urllib3>=1.21.1")
        mock_analyze_package_deps.return_value = [secondary_req]

        # Execute pack method
        library_packer.pack()

        # Assertions
        mock_get_cached_package.assert_called_with(secondary_req)
        mock_download_to_libs_dir.assert_called_with(secondary_req)
        assert mock_install_package.call_count == 2  # noqa: PLR2004
        mock_analyze_package_deps.assert_called_once_with(downloaded_file)
        assert "下载依赖" in caplog.text
        assert "安装依赖" in caplog.text

    @patch("fspacker.packers._library.analyze_package_deps")
    @patch("fspacker.packers._library.install_package")
    @patch("fspacker.packers._library.download_to_libs_dir")
    @patch("fspacker.packers._library.get_cached_package")
    @patch("fspacker.packers._library.RequirementParser.parse")
    @patch("pathlib.Path.exists", lambda _: True)
    def test_pack_with_already_packed_lib(  # noqa: PLR0913, PLR0917
        self,
        mock_parse: MagicMock,
        mock_get_cached_package: MagicMock,
        mock_download_to_libs_dir: MagicMock,
        mock_install_package: MagicMock,
        mock_analyze_package_deps: MagicMock,
        library_packer: LibraryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test pack method when library is already packed."""
        # Setup mocks
        req = Requirement("requests==2.28.1")
        mock_parse.return_value = req

        # Mock cached package exists
        cached_file = Path("/fake/libs/requests-2.28.1-py3-none-any.whl")
        mock_get_cached_package.return_value = cached_file

        # Add to packed_libs to simulate already packed
        LibraryPacker.packed_libs.add("requests")

        # Execute pack method
        library_packer.pack()

        # Assertions
        assert "已存在库" in caplog.text
        mock_install_package.assert_not_called()
        mock_analyze_package_deps.assert_not_called()
        mock_download_to_libs_dir.assert_not_called()

    @patch("fspacker.packers._library.install_package")
    @patch("fspacker.packers._library.download_to_libs_dir")
    @patch("fspacker.packers._library.get_cached_package")
    @patch("fspacker.packers._library.RequirementParser.parse")
    @patch("pathlib.Path.exists", lambda _: True)
    def test_pack_with_invalid_cached_file(  # noqa: PLR0913, PLR0917
        self,
        mock_parse: MagicMock,
        mock_get_cached_package: MagicMock,
        mock_download_to_libs_dir: MagicMock,
        mock_install_package: MagicMock,
        library_packer: LibraryPacker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test pack method when cached file is invalid."""
        # Setup mocks
        req = Requirement("requests==2.28.1")
        mock_parse.return_value = req

        # Mock cached package exists but is invalid (directory instead of file)
        cached_file = Path("/fake/libs/")  # This is a directory
        mock_get_cached_package.return_value = cached_file

        # Mock download
        downloaded_file = Path("/fake/libs/requests-2.28.1-py3-none-any.whl")
        mock_download_to_libs_dir.return_value = downloaded_file

        # Execute pack method
        library_packer.pack()

        # Assertions
        assert "处理依赖失败" in caplog.text
        mock_install_package.assert_not_called()
