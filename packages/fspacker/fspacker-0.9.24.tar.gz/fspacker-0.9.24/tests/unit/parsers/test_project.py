"""Unit test for project parsing."""

from __future__ import annotations

import platform
from collections.abc import Callable
from pathlib import Path

import pytest

from fspacker.exceptions import ProjectParseError
from fspacker.parsers.project import Project


class TestPoetryProject:
    """Test poetry project."""

    @pytest.fixture
    def fixture_ext(self) -> str:
        """Get executable extension based on platform.

        Returns:
            str: Executable extension.
        """
        return ".exe" if platform.system() == "Windows" else ""

    def test_helloworld(
        self,
        mock_console_helloworld: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test hello world project."""
        info = Project(mock_console_helloworld)

        assert info.name == "test-console-helloworld"
        assert repr(info) == "[green bold]test-console-helloworld[/]"
        assert not info.is_gui
        assert info.license_file
        assert info.source_file
        assert info.source_file.name == "main.py"
        assert info.dest_src_dir == mock_console_helloworld / "dist" / "src"
        assert info.runtime_dir == mock_console_helloworld / "dist" / "runtime"

        assert info.source_file == mock_console_helloworld / "main.py"

        assert info.min_python_version == "3.6.8"

        # set gui mode
        monkeypatch.setattr("fspacker.settings._settings.mode.gui", True)
        assert info.is_gui

    @pytest.mark.skipif(
        platform.system() != "Windows" or platform.architecture()[0] != "64bit",
        reason="Skip for non-Win64 system.",
    )
    def test_helloworld_embed_win64(
        self,
        mock_console_helloworld: Path,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Test hello world project for windows 64bit."""
        info = Project(mock_console_helloworld)
        assert info.embed_filename == "python-3.6.8-embed-amd64.zip"

        monkeypatch.setattr(
            "fspacker.settings._settings.dirs.embed",
            tmp_path / "embed",
        )
        assert (
            info.embed_filepath
            == tmp_path / "embed" / "python-3.6.8-embed-amd64.zip"
        )

    @pytest.mark.skipif(
        platform.system() != "Windows" or platform.architecture()[0] != "32bit",
        reason="Skip for non-Win64 system.",
    )
    def test_helloworld_embed_win32(
        self,
        mock_console_helloworld: Path,
    ) -> None:
        """Test hello world project for windows 32bit."""
        info = Project(mock_console_helloworld)
        assert info.embed_filename == "python-3.6.8-embed-win32.zip"

    def test_pygame(
        self,
        mock_pygame_normal_dir: Path,
        fixture_ext: str,
    ) -> None:
        """Test pygame project."""
        info = Project(mock_pygame_normal_dir)

        assert info.name == "test-pygame"
        assert info.dependencies == ["pygame>=2.6.1"]
        assert info.python_specifiers == ">=3.12"
        assert info.is_gui
        assert info.is_normal_project

        assert (
            info.dest_src_dir
            == mock_pygame_normal_dir / "dist" / "src" / "test_pygame"
        )
        assert info.runtime_dir == mock_pygame_normal_dir / "dist" / "runtime"

        assert (
            info.source_file
            == mock_pygame_normal_dir / "src" / "test_pygame" / "main.py"
        )
        assert (
            info.exe_file
            == mock_pygame_normal_dir / "dist" / f"test_pygame{fixture_ext}"
        )
        assert info.min_python_version == "3.12.10"

    def test_pyside2(
        self,
        mock_pyside2_normal_dir: Path,
        fixture_ext: str,
    ) -> None:
        """Test pyside2 project."""
        info = Project(mock_pyside2_normal_dir)

        assert info.name == "test-pyside2"
        assert info.dependencies == ["pyside2>=5.15.2.1"]
        assert info.python_specifiers == ">=3.8"
        assert info.is_gui
        assert info.is_normal_project
        assert (
            info.dest_src_dir
            == mock_pyside2_normal_dir / "dist" / "src" / "test_pyside2"
        )
        assert (
            info.source_file
            == mock_pyside2_normal_dir / "src" / "test_pyside2" / "main.py"
        )
        assert info.runtime_dir == mock_pyside2_normal_dir / "dist" / "runtime"
        assert (
            info.exe_file
            == mock_pyside2_normal_dir / "dist" / f"test_pyside2{fixture_ext}"
        )
        assert info.min_python_version == "3.8.10"

    def test_nomain(self, mock_console_nomain: Path) -> None:
        """Test no main project."""
        info = Project(mock_console_nomain)

        assert info.name == "test-console-nomain"
        assert not info.is_gui
        assert not info.license_file
        assert not info.source_file

    def test_with_venv(self, mock_console_with_venv: Path) -> None:
        """Test project with `.venv` directory."""
        info = Project(mock_console_with_venv)

        assert info.source_file
        assert info.source_file.name != "invalid_main.py"
        assert info.source_file.name == "main.py"

    def test_multi_py310(self, mock_multi_py310: Path) -> None:
        """Test python 3.10 project."""
        info = Project(mock_multi_py310)

        assert info.name == "test-multi-py310"
        assert info.authors == ["Your Name <you@example.com>"]
        assert info.dependencies == [
            "pygame<2.7.0,>=2.6.1",
            "tomli<3.0.0,>=2.2.1",
            "typer>=0.15.2",
        ]
        assert info.python_specifiers == ">=3.10,<4.0"
        assert info.is_gui
        assert info.min_python_version == "3.10.11"

    def test_min_python_version_various_specs(
        self,
        mock_create_project_file: Callable[[str, str, list[str] | None], Path],
    ) -> None:
        """Test min_python_version with various specifiers."""
        # Test with >= specifier
        project_dir = mock_create_project_file("test-project-1", ">=3.7", [])
        info = Project(project_dir)
        assert info.min_python_version == "3.7.9"

        # Test with > specifier
        project_dir = mock_create_project_file("test-project-2", ">3.6", [])
        info = Project(project_dir)
        assert info.min_python_version == "3.6.8"

        # Test with complex specifier - should pick minimum from >= or >
        project_dir = mock_create_project_file(
            "test-project-3",
            ">=3.7,<3.10",
            [],
        )
        info = Project(project_dir)
        assert info.min_python_version == "3.7.9"

        # Test with no >= or > specifier - should default to 3.8
        project_dir = mock_create_project_file(
            "test-project-4",
            "<3.10,!=3.9",
            [],
        )
        info = Project(project_dir)
        assert info.min_python_version == "3.8.10"

        # Test with empty specifier - should default to 3.8
        project_dir = mock_create_project_file("test-project-5", "", [])
        info = Project(project_dir)
        assert info.min_python_version == "3.8.10"


class TestProjectParseTomlError:
    """Test project parse toml error."""

    def test_invalid_project_path(self) -> None:
        """Test invalid project path."""
        # Test project path is None.
        with pytest.raises(ProjectParseError) as execinfo:
            Project(None)  # type: ignore  # noqa: PGH003
        assert "Invalid project directory: None" in str(execinfo.value)

        # Test project path is not exists.
        with pytest.raises(ProjectParseError) as execinfo:
            Project(Path("nonexistent_dir"))
        assert "Invalid project directory: nonexistent_dir" in str(
            execinfo.value,
        )

    def test_no_toml_file(self, tmp_path: Path) -> None:
        """测试没有项目文件."""
        with pytest.raises(ProjectParseError) as execinfo:
            Project(tmp_path)

        assert "路径下未找到 pyproject.toml" in str(execinfo.value)

    def test_unkown_toml_error(
        self,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试TOML解析失败, 其他类型."""
        project_dir = tmp_path / "project_unkown_toml"
        project_dir.mkdir()

        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
            hello, world!
            """,
            encoding="utf-16",
        )

        Project(project_dir)

        assert "未知错误" in caplog.text

        pyproject_toml.write_text("不正确的Toml文件", encoding="utf-8")
        Project(project_dir)
        assert "TOML解析错误" in caplog.text

    def test_invalid_source_ast(
        self,
        mock_console_invalid_ast: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试源文件AST解析错误."""
        Project(mock_console_invalid_ast)

        assert "源文件解析语法错误" in caplog.text

    def test_invalid_project_config(
        self,
        mock_console_helloworld: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 pyproject.toml 解析依赖失败."""
        project_dir = mock_console_helloworld
        assert project_dir.exists()

        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
    [invalidprojectconfig]
    name = "ex95-error-invalid-project-cfg"
    version = "0.1.0"
    description = "Add your description here"
    readme = "README.md"
    requires-python = ">=3.8"
    dependencies = []""",
            encoding="utf-8",
        )

        Project(project_dir)

        assert "配置项无效" in caplog.text

    def test_invalid_pep621_data(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试PEP621配置项错误."""
        project_dir = tmp_path_factory.mktemp("test-invalid-pep621-data")
        project_file = project_dir / "pyproject.toml"
        project_file.write_text("[project]", encoding="utf-8")

        Project(project_dir)

        assert "未找到项目PEP621配置项" in caplog.text

    def test_invalid_poetry_data(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 poetry 配置项错误."""
        project_dir = tmp_path_factory.mktemp("test-invalid-poetry-data")
        project_file = project_dir / "pyproject.toml"
        project_file.write_text("[tool.poetry]", encoding="utf-8")

        Project(project_dir)

        assert "未找到项目poetry配置项" in caplog.text

    def test_invalid_pep621_config(
        self,
        tmp_path_factory: pytest.TempPathFactory,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 pyproject.toml 解析依赖 pep621 失败."""
        project_dir = tmp_path_factory.mktemp("test-invalid-pep621-config")
        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
    [project]
    version = "0.1.0"
    description = "Add your description here"
    readme = "README.md"
    dependencies = "error"
    optional-dependencies = "error"
    """,
            encoding="utf-8",
        )
        main_file = project_dir / "main.py"
        main_file.write_text(
            """
def main():
    print("Test for poetry project!")

main()
    """,
            encoding="utf-8",
        )

        Project(project_dir)

        assert "未设置项目参数: [[red]name[/]]" in caplog.text
        assert "未设置项目参数: [[red]requires-python[/]]" in caplog.text
        assert "依赖项格式错误" in caplog.text

    def test_invalid_poetry_cfg(
        self,
        mock_console_helloworld: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """测试 pyproject.toml 解析可选依赖失败."""
        project_dir = mock_console_helloworld
        assert project_dir.exists()

        # 创建一个无效的poetry配置文件
        pyproject_toml = project_dir / "pyproject.toml"
        pyproject_toml.write_text(
            """
    [tool.poetry]
    version = "0.1.0"
    description = ""
    authors = ["test <test@example.com>"]
    readme = "README.md"

    [tool.poetry.dependencies]

    [build-system]
    requires = ["poetry-core"]
    build-backend = "poetry.core.masonry.api"
    """,
            encoding="utf-8",
        )

        info = Project(project_dir)

        assert info.dependencies == []

        assert "未设置项目参数: [[red]name[/]]" in caplog.text
        assert "未指定python版本" in caplog.text


class TestProjectIsValidEntry:
    """Test project is_valid_entry method."""

    def test_valid_entry(self, mock_console_helloworld: Path) -> None:
        """Test valid entry file."""
        info = Project(mock_console_helloworld)
        # Test a normal file that should be valid
        valid_file = mock_console_helloworld / "main.py"
        assert info.is_valid_entry(valid_file) is True

    @pytest.mark.parametrize(
        "parent_folder",
        ["dist-info", "dist", "site-packages", "runtime"],
    )
    def test_file_with_ignored_directory(
        self,
        mock_console_helloworld: Path,
        parent_folder: str,
    ) -> None:
        """Test file in ignored directory."""
        info = Project(mock_console_helloworld)
        # Test file in dist-info directory which should be ignored
        invalid_file = mock_console_helloworld / parent_folder / "file.py"
        assert info.is_valid_entry(invalid_file) is False

    def test_file_with_ignored_folder_name(
        self,
        mock_console_helloworld: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test file in directory with ignored folder name."""
        info = Project(mock_console_helloworld)
        # Test file in directory that should be ignored based on settings
        monkeypatch.setattr(
            "fspacker.settings._settings.ignore_folders",
            ["test_folder"],
        )
        invalid_file = mock_console_helloworld / "test_folder" / "file.py"
        assert info.is_valid_entry(invalid_file) is False

    def test_file_starting_with_dot(
        self,
        mock_console_helloworld: Path,
    ) -> None:
        """Test file starting with dot."""
        info = Project(mock_console_helloworld)
        # Test file that starts with dot which should be ignored
        hidden_file = mock_console_helloworld / ".hidden.py"
        assert info.is_valid_entry(hidden_file) is False

    def test_file_starting_with_underscore(
        self,
        mock_console_helloworld: Path,
    ) -> None:
        """Test file starting with underscore."""
        info = Project(mock_console_helloworld)
        # Test file that starts with underscore which should be ignored
        hidden_file = mock_console_helloworld / "_private.py"
        assert info.is_valid_entry(hidden_file) is False

    def test_valid_nested_file(self, mock_console_helloworld: Path) -> None:
        """Test valid nested file."""
        info = Project(mock_console_helloworld)
        # Test a valid file in a subdirectory
        valid_file = mock_console_helloworld / "subdir" / "module.py"
        assert info.is_valid_entry(valid_file) is True
