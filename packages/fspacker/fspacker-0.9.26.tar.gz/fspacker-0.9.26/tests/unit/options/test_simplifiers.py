from fspacker.options.simplify.rules import get_simplify_rules
from fspacker.options.simplify.rules import SimplifyRule


def test_get_simplify_options_existing() -> None:
    """测试获取已存在的库的精简配置."""
    option = get_simplify_rules("pyside2")
    assert isinstance(option, SimplifyRule)
    assert option.patterns is not None
    assert "PySide2/__init__.py" in option.patterns

    option = get_simplify_rules("torch")
    assert isinstance(option, SimplifyRule)
    assert option.patterns is None
    assert option.excludes is not None
    assert "torch/utils/bottleneck/*" in option.excludes


def test_get_simplify_options_nonexistent() -> None:
    """测试获取不存在的库的精简配置."""
    option = get_simplify_rules("nonexistent_lib")
    assert option is None
