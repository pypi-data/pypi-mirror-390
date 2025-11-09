from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class Engine(ABC):
    """This is an abstract class which is inherited for every engine. It acts as
    an interface to the engine and abstracts away things like running an analysis
    using the engine."""

    @abstractmethod
    def name(self) -> str:
        """Returns the name of the engine as used in the CLI."""
        raise NotImplementedError

    @abstractmethod
    def can_run_analysis(self, analysis_file: Path) -> bool:
        """Checks if this engine can run the analysis in the given file."""
        raise NotImplementedError

    @abstractmethod
    def run_local_analysis(
        self,
        analysis_file: Path,
        engine_path: Optional[str] = None,
        additional_cli_args: Optional[list[str]] = None,
    ):
        """Runs the analysis in the given file using the locally installed engine."""
        raise NotImplementedError

    @abstractmethod
    def run_containerized_analysis(
        self, analysis_file: Path, additional_cli_args: Optional[list[str]] = None
    ):
        """Runs the analysis in the given file in a container. This does not require the
        engine to be installed on the system."""
        raise NotImplementedError
