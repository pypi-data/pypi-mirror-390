from pathlib import Path

from phylorun.engines.beast2 import BEAST2


def to_file(text: str, path: str):
    path.write_text(text)
    return path


def test_simple_beast_config_is_ok(tmp_path: Path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
            <data></data>
            <run></run>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert BEAST2().can_run_analysis(path)


def test_simple_beast_config_with_alignment_is_ok(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
            <alignment></alignment>
            <run></run>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert BEAST2().can_run_analysis(path)


def test_beast1_xml_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast version="1.10.4">
            <data></data>
            <run></run>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert not BEAST2().can_run_analysis(path)


def test_missing_data_tag_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
            <run></run>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert not BEAST2().can_run_analysis(path)


def test_missing_run_tag_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
            <data></data>
        </beast>""",
        tmp_path / "analysis.xml",
    )
    assert not BEAST2().can_run_analysis(path)


def test_empty_file_fails(tmp_path):
    path = to_file(
        "",
        tmp_path / "analysis.xml",
    )
    assert not BEAST2().can_run_analysis(path)


def test_non_xml_file_fails(tmp_path):
    path = to_file(
        """
        config:
            - this is not a XML file
        """,
        tmp_path / "analysis.xml",
    )
    assert not BEAST2().can_run_analysis(path)


def test_missing_beast_tag_fails(tmp_path):
    path = to_file(
        """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <some-other-tag></some-other-tag>""",
        tmp_path / "analysis.xml",
    )
    assert not BEAST2().can_run_analysis(path)
