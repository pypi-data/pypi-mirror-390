from pathlib import Path
from typing import Optional

from phylorun.engines.beast2 import BEAST2
from phylorun.engines.engine import Engine

from loguru import logger
import subprocess

import os


class LPhy(Engine):
    def name(self) -> str:
        """Returns the name of the engine as used in the CLI."""
        return "lphy"

    def can_run_analysis(self, analysis_file: Path) -> bool:
        """Checks if LPhy engine can run the analysis in the given file."""
        if not analysis_file.name.endswith(".lphy"):
            logger.debug("No LPhy file: wrong file extension (.lphy requried).")
            return False

        logger.debug("LPhy file found.")
        return True

    def run_local_analysis(
        self,
        analysis_file: Path,
        engine_path: Optional[str] = None,
        additional_cli_args: Optional[list[str]] = None,
    ):
        """Runs the analysis in the given file using the locally installed engine."""
        engine_path = engine_path or self._find_binary_path()
        if not engine_path:
            raise Exception("""No lphybeast binary found.
Use `phylorun --bin <path-to-binary> your_analysis.xml` to manually specify the lphybeast binary.
            """)

        additional_lphy_cli_args = [
            arg for arg in additional_cli_args or [] if not arg.startswith("--beast2")
        ]
        additional_beast_cli_args = [
            arg.removeprefix("--beast2")
            for arg in additional_cli_args or []
            if arg.startswith("--beast2")
        ] or ["-working"]

        env = os.environ.copy()
        if beast_path := self._find_beast_path():
            env["BEAST"] = beast_path

        # run lphybeast
        subprocess.run(
            ["sh", engine_path, *additional_lphy_cli_args, analysis_file], env=env
        )

        # run BEAST 2
        beast2_file = analysis_file.parent / (analysis_file.stem + ".xml")
        beast2 = BEAST2()
        beast2.run_local_analysis(
            beast2_file, additional_cli_args=additional_beast_cli_args
        )

    def _find_binary_path(self) -> Optional[str]:
        if path := os.environ.get("BEAST"):
            return path

        possible_paths = list(
            Path("/Users").glob(
                "*/Library/Application Support/BEAST/2.*/lphybeast/bin/lphybeast"
            )
        )
        possible_paths = sorted(possible_paths)

        if not possible_paths:
            return None

        return str(possible_paths[-1])

    def _find_beast_path(self) -> Optional[str]:
        if path := os.environ.get("BEAST"):
            return path

        possible_paths = list(Path("/Applications").glob("BEAST 2.*"))
        possible_paths = sorted(possible_paths)

        if not possible_paths:
            return None

        return str(possible_paths[-1])

    def run_containerized_analysis(
        self, analysis_file: Path, additional_cli_args: Optional[list[str]] = None
    ):
        """Runs the analysis in the given file in a container. This does not require the
        engine to be installed on the system."""
        raise NotImplementedError
