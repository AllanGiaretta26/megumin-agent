from pathlib import Path

import pytest

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


def test_read_file_returns_error_on_io_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "blocked.txt").write_text("secret")

    def fail_read_text(
        self: Path,
        encoding: str | None = None,
        errors: str | None = None,
    ) -> str:
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "read_text", fail_read_text)

    result = _read_file_impl("blocked.txt", str(tmp_path))

    assert result.status == "error"
    assert "Erro de I/O em 'blocked.txt'" in result.content
    assert "disk unavailable" in result.content
