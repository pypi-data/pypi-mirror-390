from pathlib import Path
from typing import Optional

import click

from phylorun.engines import ENGINES
from phylorun.engines.engine import Engine


CONTEXT_SETTINGS = dict(ignore_unknown_options=True, allow_extra_args=True)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--engine",
    type=click.Choice(["beastx", "beast2", "revbayes", "lphy"], case_sensitive=False),
    required=False,
    help="Select engine explicitly: beastx | beast2 | revbayes | lphy.",
)
@click.option(
    "--bin",
    "engine_path",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=False,
    help="Path to the engine binary to use for local runs.",
)
@click.option(
    "--container",
    is_flag=True,
    help="Run inside a containerized environment (no local engine install required).",
)
@click.argument(
    "analysis_file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.pass_context
def cli(
    ctx: click.Context,
    engine: Optional[str],
    engine_path: Optional[str],
    container: bool,
    analysis_file: Path,
) -> None:
    """Run BEAST X, BEAST 2, or RevBayes analyses from a single CLI.

    Examples:
      phylorun someModel.xml
      phylorun --beast2 someModel.xml
      phylorun --bin /path/to/beast someModel.xml
      phylorun --container someModel.rev
    """

    # Choose engine: flag forces selection; otherwise auto-detect
    selected_engine: Engine | None = None

    if engine:
        for e in ENGINES:
            if e.name() != engine:
                continue

            if not e.can_run_analysis(analysis_file):
                raise click.ClickException(
                    f"Engine '{engine}' cannot run file '{analysis_file}'."
                )

            selected_engine = e
            break

        if selected_engine is None:
            raise click.ClickException(f"Engine '{engine}' is not available.")
    else:
        for potentialEngine in ENGINES:
            if potentialEngine.can_run_analysis(analysis_file):
                selected_engine = potentialEngine
                break

        if selected_engine is None:
            raise click.ClickException(
                f"Could not detect a supported engine for file '{analysis_file}'."
            )

    additional_args = list(ctx.args) if ctx.args else None

    if container:
        selected_engine.run_containerized_analysis(analysis_file, additional_args)
    else:
        selected_engine.run_local_analysis(analysis_file, engine_path, additional_args)


if __name__ == "__main__":
    cli()
