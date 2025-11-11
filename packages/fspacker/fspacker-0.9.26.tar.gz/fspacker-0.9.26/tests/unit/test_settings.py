import importlib
import pathlib
from pathlib import Path

import pytest

import fspacker.settings


@pytest.fixture(autouse=True)
def reload_module() -> None:
    importlib.reload(fspacker.settings)


class TestSettings:
    """Test settings module."""

    def test_default_settings(
        self,
    ) -> None:
        """Test default settings."""
        settings = fspacker.settings.get_settings()
        cache_dir = pathlib.Path("~").expanduser() / ".cache" / "fspacker"

        # check default dirs settings
        assert settings.dirs.cache == cache_dir
        assert settings.dirs.libs == cache_dir / "libs-repo"
        assert settings.dirs.embed == cache_dir / "embed-repo"
        assert settings.dirs.tools == cache_dir / "tools"

        dirs = {
            "cache": cache_dir,
            "embed": cache_dir / "embed-repo",
            "libs": cache_dir / "libs-repo",
            "tools": cache_dir / "tools",
        }
        assert str(settings.dirs) == ",".join([
            f"{k}={v}" for k, v in dirs.items()
        ])

        # check default mode settings
        assert not settings.mode.archive
        assert not settings.mode.simplify
        assert "非调试" in str(settings.mode)
        assert "CONSOLE" in str(settings.mode)

    def test_set_mode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test change mode settings."""
        settings = fspacker.settings.get_settings()

        assert "非调试" in str(settings.mode)
        assert "CONSOLE" in str(settings.mode)
        assert "在线" in str(settings.mode)
        assert "离线" not in str(settings.mode)

        monkeypatch.setattr(
            "fspacker.settings._settings.mode",
            fspacker.settings.PackMode(
                archive=True,
                debug=True,
                gui=True,
                offline=True,
                rebuild=True,
                recursive=True,
                simplify=True,
                use_tk=True,
            ),
        )

        assert "GUI" in str(settings.mode)
        assert "调试" in str(settings.mode)
        assert "非调试" not in str(settings.mode)
        assert "离线" in str(settings.mode)

        settings.mode.reset()

        assert settings.mode == fspacker.settings.PackMode(
            archive=False,
            debug=False,
            gui=False,
            offline=False,
            rebuild=False,
            recursive=False,
            simplify=False,
            use_tk=False,
        )
        assert "GUI" not in str(settings.mode)
        assert "非调试" in str(settings.mode)

    def test_get_dirs_from_env(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Test get cache dir from env."""
        monkeypatch.setenv("FSP_DIRS__CACHE", str(tmp_path))
        monkeypatch.setenv("FSP_DIRS__LIBS", str(tmp_path / "libs"))

        settings = fspacker.settings.get_settings()
        assert settings.dirs.cache == tmp_path
        assert settings.dirs.libs == tmp_path / "libs"

    def test_get_dirs_when_env_not_set(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test get cache dir when env not set."""
        monkeypatch.delenv("FSP_DIRS__CACHE", raising=False)
        monkeypatch.delenv("FSP_DIRS__LIBS", raising=False)

        cache_dir = Path("~").expanduser() / ".cache" / "fspacker"
        assert fspacker.settings.get_settings().dirs.cache == cache_dir

    def test_dump_settings(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test dump settings to env file."""
        # 创建一个临时.env文件路径
        env_file = tmp_path / ".env"

        fspacker.settings.get_settings()

        monkeypatch.setattr(fspacker.settings, "_env_filepath", env_file)

        # 获取设置实例并调用dump方法
        settings = fspacker.settings.get_settings()
        settings.dump()

        # 检查.env文件是否创建
        assert env_file.exists()

        # 读取文件内容
        content = env_file.read_text(encoding="utf-8")

        # 检查内容是否包含预期的环境变量前缀
        assert "FSP_DIRS__" in content
        assert "FSP_URLS__" in content

        cache_dir = Path("~").expanduser() / ".cache" / "fspacker"
        assert f"FSP_DIRS__CACHE={cache_dir}" in content

        # 检查是否只导出了指定前缀的设置
        assert "FSP_MAX_THREAD" not in content
