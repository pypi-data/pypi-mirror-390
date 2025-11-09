from pathlib import Path

from phylorun.engines.beastX import BEASTX


def to_file(text: str, path: str):
    path.write_text(text)
    return path


def test_simple_beast_config_is_ok(tmp_path: Path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast version="10.5.0">
            <alignment></alignment>
            <mcmc></mcmc>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert BEASTX().can_run_analysis(path)


def test_beast2_xml_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
           <alignment></alignment>
            <mcmc></mcmc>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert not BEASTX().can_run_analysis(path)


def test_missing_mcmc_tag_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast version="10.5.0">
            <alignment></alignment>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert not BEASTX().can_run_analysis(path)


def test_empty_file_fails(tmp_path):
    path = to_file(
        "",
        tmp_path / "analysis.xml",
    )
    assert not BEASTX().can_run_analysis(path)


def test_non_xml_file_fails(tmp_path):
    path = to_file(
        """
        config:
            - this is not a XML file
        """,
        tmp_path / "analysis.xml",
    )
    assert not BEASTX().can_run_analysis(path)


def test_missing_beast_tag_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <some-other-tag></some-other-tag>""",
        tmp_path / "analysis.xml",
    )
    assert not BEASTX().can_run_analysis(path)
