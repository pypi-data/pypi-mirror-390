import os
from pathlib import Path
import subprocess
from typing import Optional
from phylorun.engines.engine import Engine
from xml.etree import ElementTree

from loguru import logger

from phylorun.utils.docker_utils import (
    create_image_if_needed,
    get_docker_client,
    run_and_print_command,
    start_container,
)


BINARY_URL = "https://github.com/beast-dev/beast-mcmc/releases/download/v10.5.0/BEAST_X_v10.5.0.tgz"
EB_URL = "https://raw.githubusercontent.com/easybuilders/easybuild-easyconfigs/refs/heads/main/easybuild/easyconfigs/b/beagle-lib/beagle-lib-4.0.1-GCC-12.3.0.eb"


class BEASTX(Engine):
    def name(self) -> str:
        """Returns the name of the engine as used in the CLI."""
        return "beastx"

    def can_run_analysis(self, analysis_file: Path) -> bool:
        """Checks if BEAST X can run the analysis in the given file."""
        try:
            xml = ElementTree.parse(analysis_file)
        except ElementTree.ParseError:
            logger.debug("No BEAST X file: no XML file.")
            return False

        root = xml.getroot()

        if root is None or root.tag.lower() != "beast":
            logger.debug("No BEAST X file: no root BEAST tag.")
            return False

        if not root.attrib.get("version", "").startswith("1.") and not root.attrib.get(
            "version", ""
        ).startswith("10."):
            logger.debug("No BEAST X file: wrong version (likely for BEAST 2).")
            return False

        if not any(child.tag.lower() == "mcmc" for child in root):
            logger.debug("No BEASTX file: no <mcmc> tag.")
            return False

        logger.debug("BEAST X file found.")

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
            raise Exception("""No BEAST X binary found.
Use `phylorun --container your_analysis.xml` to use a docker container if you don't have BEAST X installed.
Use `phylorun --bin <path-to-binary> your_analysis.xml` to manually specify the BEAST X binary.
            """)

        additional_cli_args = additional_cli_args or []

        subprocess.run([engine_path, *additional_cli_args, analysis_file])

    def _find_binary_path(self) -> Optional[str]:
        if path := os.environ.get("BEAST"):
            return path

        possible_paths = (
            list(Path("/Applications").glob("BEAST X*/bin/beast"))
            + list(Path("/Applications").glob("BEAST X*/bin/beast"))
            + list(Path("~").glob("beast*/bin/beast"))
        )
        possible_paths = sorted(possible_paths)

        if not possible_paths:
            return None

        return str(possible_paths[-1])

    def run_containerized_analysis(
        self, analysis_file: Path, additional_cli_args: Optional[list[str]] = None
    ):
        """Runs the analysis in the given file in a container. This does not require the
        engine to be installed on the system."""
        docker_client = get_docker_client()

        IMAGE_NAME = "beastx:10.5.0"

        create_image_if_needed(
            docker_client,
            IMAGE_NAME,
            f"""FROM ubuntu:latest
            RUN apt-get update \\
                && apt-get install -y wget tar openjdk-17-jdk python3-venv python3-pip \\
                && wget {BINARY_URL} -O /BEAST.tgz \\
                && tar -xzf /BEAST.tgz -C /opt   \\
                && rm /BEAST.tgz
            """,
        )

        working_dir_is_data_dir = Path() == analysis_file.parent

        volumes = {str(analysis_file.parent.resolve()): {"bind": "/data", "mode": "rw"}}
        if not working_dir_is_data_dir:
            volumes[str(Path().resolve())] = {"bind": "/working", "mode": "rw"}

        container = start_container(
            docker_client,
            IMAGE_NAME,
            volumes=volumes,
        )

        try:
            if working_dir_is_data_dir:
                run_and_print_command(
                    container,
                    f"/opt/BEASTv10.5.0/bin/beast -java {' '.join(additional_cli_args or [])} '/data/{analysis_file.name}'",
                    working_dir="/data",
                )
            else:
                run_and_print_command(
                    container,
                    f"/opt/BEASTv10.5.0/bin/beast -java {' '.join(additional_cli_args or [])} '/data/{analysis_file.name}'",
                    working_dir="/working",
                )
        finally:
            container.stop()
            container.remove()
