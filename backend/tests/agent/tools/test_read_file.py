from pathlib import Path

from app.modules.agent.tools.read_file import _read_file_impl


def test_read_file_returns_error_on_traversal(tmp_path: Path) -> None:
    result = _read_file_impl("../escape.txt", str(tmp_path))
    assert result.status == "error"
    assert "Acesso negado" in result.content


def test_read_file_returns_ok_on_valid_path(tmp_path: Path) -> None:
    (tmp_path / "hello.txt").write_text("hi")
    result = _read_file_impl("hello.txt", str(tmp_path))
    assert result.status == "ok"
    assert result.content == "hi"
