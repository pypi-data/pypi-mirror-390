import io
import sys
from typing import Optional
import docker
from docker.models.containers import Container
from docker.errors import DockerException, ImageNotFound
from loguru import logger


def get_docker_client() -> docker.DockerClient:
    """Instantiate and return a Docker client."""
    try:
        return docker.from_env()
    except DockerException:
        logger.error("Docker could not be instantiated. Is it installed and running?")
        raise Exception(
            "Docker could not be instantiated. Is it installed and running?"
        )


def create_image_if_needed(
    client: docker.DockerClient, image_name: str, docker_file: str
):
    """Ensure a Docker image exists, building it from a Dockerfile string if necessary."""
    try:
        client.images.get(image_name)
        # image already created
        return
    except ImageNotFound:
        # we still need to create the image
        ...

    logger.info(
        "Setting up docker container. This might take a while, but only has to be done once."
    )

    docker_file_bytes = io.BytesIO(docker_file.encode("utf-8"))

    client.images.build(
        fileobj=docker_file_bytes,
        tag=image_name,
        rm=True,
        platform="linux/x86_64",
    )


def start_container(
    client: docker.DockerClient, image_name: str, **kwargs
) -> Container:
    """Start a Docker container from a specified image.

    Args:
        client (docker.DockerClient): The Docker client.
        image_name (str): Name of the Docker image.
        **kwargs: Additional keyword arguments passed to container run.

    Returns:
        Container: The started Docker container.
    """
    return client.containers.run(
        image_name, "sleep infinity", detach=True, platform="linux/x86_64", **kwargs
    )


def run_and_print_command(
    container: Container,
    command: str,
    user: Optional[str] = None,
    working_dir: Optional[str] = None,
):
    """Run a command inside a Docker container and print its output to stdout and stderr.

    Args:
        container (Container): The Docker container where the command will be executed.
        command (str): The command to execute.
        user (Optional[str]): User to run the command as (if specified).
        working_dir (Optional[str]): The working directory inside the container (if specified).
    """
    result = container.exec_run(
        command, stream=True, demux=True, user=user or "root", workdir=working_dir
    )

    for stdout, stderr in result.output:
        if stdout:
            print(stdout.decode(), end="")
        if stderr:
            print(stderr.decode(), end="", file=sys.stderr)
