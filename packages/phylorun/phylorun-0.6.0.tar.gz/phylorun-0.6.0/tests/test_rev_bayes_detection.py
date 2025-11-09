from pathlib import Path

from phylorun.engines.revBayes import RevBayes


def to_file(text: str, path: str):
    path.write_text(text)
    return path


def test_rev_file_is_ok(tmp_path: Path):
    path = to_file(
        "",
        tmp_path / "analysis.rev",
    )
    assert RevBayes().can_run_analysis(path)


def test_non_rev_file_is_ok(tmp_path: Path):
    path = to_file(
        "",
        tmp_path / "analysis.txt",
    )
    assert not RevBayes().can_run_analysis(path)
