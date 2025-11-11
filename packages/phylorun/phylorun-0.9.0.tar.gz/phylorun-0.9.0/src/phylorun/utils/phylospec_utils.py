from pathlib import Path


def is_phylospec_file(analysis_file: Path):
    return analysis_file.name.endswith(".phylospec")
