from pathlib import Path
import subprocess
from typing import Optional

from loguru import logger
from phylorun.engines.engine import Engine
from phylorun.utils.docker_utils import (
    create_image_if_needed,
    get_docker_client,
    run_and_print_command,
    start_container,
)


BINARY_URL = "https://github.com/revbayes/revbayes/releases/download/v1.3.1/revbayes-v1.3.1-linux64.tar.gz"


class RevBayes(Engine):
    def name(self) -> str:
        """Returns the name of the engine as used in the CLI."""
        return "revbayes"

    def can_run_analysis(self, analysis_file: Path) -> bool:
        """Checks if RevBayes can run the analysis in the given file."""
        if not analysis_file.name.endswith(".rev"):
            logger.debug("No Rev file: wrong file extension (.rev requried).")
            return False

        logger.debug("RevBayes file found.")
        return True

    def run_local_analysis(
        self,
        analysis_file: Path,
        engine_path: Optional[str] = None,
        additional_cli_args: Optional[list[str]] = None,
    ):
        """Runs the analysis in the given file using the locally installed engine."""
        engine_path = engine_path or "rb"
        if not engine_path:
            raise Exception("""No RevBayes binary found.
Use `phylorun --container your_analysis.rev` to use a docker container if you don't have RevBayes installed.
Use `phylorun --bin <path-to-binary> your_analysis.rev` to manually specify the RevBayes binary.
            """)

        additional_cli_args = additional_cli_args or []

        subprocess.run([engine_path, *additional_cli_args, analysis_file])

    def run_containerized_analysis(
        self, analysis_file: Path, additional_cli_args: Optional[list[str]] = None
    ):
        """Runs the analysis in the given file in a container. This does not require the
        engine to be installed on the system."""
        docker_client = get_docker_client()

        IMAGE_NAME = "revbayes:1.3.1"

        create_image_if_needed(
            docker_client,
            IMAGE_NAME,
            f"""FROM ubuntu:latest
            RUN apt-get update \\
                && apt-get install -y wget tar \\
                && wget {BINARY_URL} -O /revBayes.tgz \\
                && tar -xzf /revBayes.tgz -C /opt   \\
                && rm /revBayes.tgz
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
                    f"/opt/revbayes-v1.3.1/bin/rb {' '.join(additional_cli_args or [])} '/data/{analysis_file.name}'",
                    working_dir="/data",
                )
            else:
                run_and_print_command(
                    container,
                    f"/opt/revbayes-v1.3.1/bin/rb {' '.join(additional_cli_args or [])} '/data/{analysis_file.name}'",
                    working_dir="/working",
                )
        finally:
            container.stop()
            container.remove()
