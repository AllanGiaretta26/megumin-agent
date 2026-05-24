from pathlib import Path

import pytest

from app.modules.agent.tools.write_file import _write_file_impl


def test_write_file_returns_error_on_traversal(tmp_path: Path) -> None:
    result = _write_file_impl("../escape.txt", "content", str(tmp_path))
    assert result.status == "error"
    assert "Acesso negado" in result.content


def test_write_file_returns_ok_on_valid_path(tmp_path: Path) -> None:
    result = _write_file_impl("notes/hello.txt", "hi", str(tmp_path))

    assert result.status == "ok"
    assert "escrito com sucesso" in result.content
    assert (tmp_path / "notes" / "hello.txt").read_text() == "hi"


def test_write_file_returns_error_on_io_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_write_text(self: Path, data: str, encoding: str | None = None) -> int:
        raise OSError("read-only filesystem")

    monkeypatch.setattr(Path, "write_text", fail_write_text)

    result = _write_file_impl("blocked.txt", "content", str(tmp_path))

    assert result.status == "error"
    assert "Erro de I/O em 'blocked.txt'" in result.content
    assert "read-only filesystem" in result.content
