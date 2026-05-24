from pathlib import Path

import pytest

from app.modules.agent.tools.list_directory import _list_directory_impl


def test_list_directory_returns_error_on_traversal(tmp_path: Path) -> None:
    result = _list_directory_impl("../escape", str(tmp_path))
    assert result.status == "error"
    assert "Acesso negado" in result.content


def test_list_directory_returns_ok_on_valid_path(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "README.md").write_text("docs")

    result = _list_directory_impl(".", str(tmp_path))

    assert result.status == "ok"
    assert "📁 src" in result.content
    assert "  README.md" in result.content


def test_list_directory_returns_error_on_io_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_iterdir(self: Path):
        raise OSError("cannot scan")

    monkeypatch.setattr(Path, "iterdir", fail_iterdir)

    result = _list_directory_impl(".", str(tmp_path))

    assert result.status == "error"
    assert "Erro de I/O em '.'" in result.content
    assert "cannot scan" in result.content
