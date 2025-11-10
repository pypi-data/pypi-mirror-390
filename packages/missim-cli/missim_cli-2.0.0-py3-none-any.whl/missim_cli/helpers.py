from typing import List
import click
import os
from pathlib import Path
import subprocess
import yaml
import platform
from python_on_whales.utils import ValidPath
import pkg_resources


def get_project_root() -> Path:
    current_file_dir = Path(__file__).parent
    return current_file_dir.parent.parent.parent


def make_dir_set_permission(path: Path, permission=0o777) -> Path:
    """Make a directory and set the permissions"""
    os.makedirs(path, mode=permission, exist_ok=True)
    path.chmod(permission)
    # If this errors then the current user does not have permission to set the permissions
    # This probably means the directory already exists
    return path


def get_missim_version():
    """MISSIM version is latest if it is a dev version otherwise it is the CLI version"""
    version = pkg_resources.require("missim-cli")[0].version
    if version == "0.0.0":
        version = "latest"
    return version


def is_dev_version():
    if os.environ.get("MISSIM_CLI_DEV_MODE") == "false":
        return False

    if os.environ.get("MISSIM_CLI_DEV_MODE") == "true":
        return True
    return pkg_resources.require("missim_cli")[0].version == "0.0.0"


def docker_compose_path(path: str) -> Path:
    current_file_dir = Path(__file__).parent
    return current_file_dir / "docker" / path


def get_docker_file_args(files: List[str]):
    return "-f " + " -f ".join(files)


def get_args_str(args: List[str]):
    return " ".join(args)


def call(command: str, abort=True, env=None):
    click.echo(click.style(f"Running: {command}", fg="blue"))
    if env:
        env = {**os.environ, **env}

    prj_root = get_project_root()
    error = subprocess.call(command, shell=True, executable="/bin/bash", cwd=prj_root, env=env)
    if error and abort:
        raise click.ClickException("Failed")


def get_arch():
    arch = platform.machine()
    if arch == "x86_64":
        return "amd64"
    elif arch == "aarch64":
        return "arm64"
    else:
        print(f"Unsupported arch: {arch}")
        exit(1)


def docker_bake(version: str, compose_files: List[ValidPath], push: bool, services: List[str]):
    compose_args: list[str] = []
    for f in compose_files:
        compose_args.append(f"--file {f}")

    # Load the compose config
    file_args = " ".join(compose_args)
    command_get_config = f"docker compose {file_args} config"
    print("Running command: ", command_get_config)
    config = subprocess.run(
        command_get_config, shell=True, check=True, cwd=get_project_root(), capture_output=True
    )
    config = config.stdout.decode("utf-8")
    config = yaml.safe_load(config)

    # Create the bake command args
    bake_args = compose_args
    bake_args.append(
        "--provenance=false"
    )  # this allows us to create a multi-arch manifest at a later stage

    # Get the arch
    arch = get_arch()

    # Get all services we should build and set their tags and arch
    services_actual: list[str] = []
    for service, service_config in config["services"].items():
        if "image" in service_config and "build" in service_config:
            # If we have a list of services to build, only build those
            if len(services) == 0 or service in services:
                image = service_config["image"]
                image = image.split(":")[0]
                bake_args.append(f"--set {service}.platform=linux/{arch}")
                bake_args.append(f"--set {service}.tags={image}:{version}-{arch}")
                bake_args.append(f"--set {service}.tags={image}:latest-{arch}")
                services_actual.append(service)

    # Add other args
    if push:
        bake_args.append("--push")

    print(f"Baking services: {', '.join(services_actual)}...")
    bake_command = " ".join(
        [
            "docker buildx bake",
            " ".join(bake_args),
            " ".join(services_actual),
        ]
    )

    print("Running bake command: ", bake_command)
    subprocess.run(
        bake_command,
        shell=True,
        check=True,
        cwd=get_project_root(),
    )


def maybe_ignore_build(dev_mode: bool, build: bool):
    """Force build false in non-dev mode"""
    if dev_mode:
        return build
    if build:
        click.echo(click.style("Ignoring --build flag in non-dev mode", fg="yellow"))
    return False


def maybe_ignore_prod(dev_mode: bool, prod: bool):
    """Force prod true in non-dev mode"""
    if dev_mode:
        return prod
    if prod is False:
        click.echo(click.style("Ignoring prod=false in non-dev mode", fg="yellow"))
    return True
