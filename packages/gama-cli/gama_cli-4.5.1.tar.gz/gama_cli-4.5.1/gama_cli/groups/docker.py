import click

from gama_cli.helpers import call
import requests


@click.group(help="Docker convenience methods")
def docker():
    pass


@click.command(name="clearlogs")
def clearlogs():  # type: ignore
    """Clears all the docker logs"""
    command = 'sudo sh -c "truncate -s 0 /var/lib/docker/containers/*/*-json.log"'
    call(command)


# Reusable option decorator for config_dir
config_dir_option = click.option(
    "-c",
    "--config-dir",
    type=str,
    default="~/.config/greenroom",
    help="The directory where the GAMA config is stored. Resolved relative to: ~/.config/greenroom",
)


def change_registry(image_with_registry: str, new_registry: str):
    # replace the leading part of the image with the new registry
    return new_registry + "/" + "/".join(image_with_registry.split("/")[1:])


@click.command(name="pull-registry")
@click.option(
    "--host",
    "-h",
    type=str,
    required=True,
    default="localhost:5555",
    help="The registry to pull the images from, ie localhost:5555",
)
# @click.argument(
#     "service",
#     required=False,
#     type=click.Choice(SERVICES),
# )
@config_dir_option
def pull_registry(host: str, config_dir: str = "~/.config/greenroom"):  # type: ignore
    from .gs import get_docker_client

    dc = get_docker_client(config_dir)
    all_services = dc.compose.config().services

    for service_name, service_config in all_services.items():
        local_image_tag = service_config.image
        if local_image_tag is None:
            continue
        target_image_tag = change_registry(local_image_tag, host)
        dc.image.pull(target_image_tag)
        dc.image.tag(target_image_tag, local_image_tag)


@click.command(name="push-registry")
@click.option(
    "--host",
    "-h",
    type=str,
    required=True,
    default="localhost:5555",
    help="The registry to push the images to, ie localhost:5555",
)
# @click.argument(
#     "service",
#     required=False,
#     type=click.Choice(SERVICES),
# )
@config_dir_option
def push_registry(host: str, config_dir: str = "~/.config/greenroom"):  # type: ignore
    from .gs import get_docker_client

    dc = get_docker_client(config_dir)
    all_services = dc.compose.config().services

    for service_name, service_config in all_services.items():
        local_image_tag = service_config.image
        if local_image_tag is None:
            continue
        target_image_tag = change_registry(local_image_tag, host)
        dc.image.tag(local_image_tag, target_image_tag)
        dc.image.push(target_image_tag)


@click.command(name="registry")
@click.option("--port", type=int, default=5555)
@click.option("--persist", type=bool, default=True, is_flag=True)
@click.option("--restart", type=bool, default=False, is_flag=True)
@click.option("--clean-volume", type=bool, default=False, is_flag=True)
@click.argument("up_or_down", type=str)
def registry(port: int, persist: bool, restart: bool, clean_volume: bool, up_or_down: str):  # type: ignore
    """Starts the docker registry"""
    cmd = f"docker run -d -p {port}:5000"
    if persist:
        cmd += " --name registry -v /var/lib/registry:/var/lib/registry"
    if restart:
        cmd += " --restart=always"

    cmd += " registry:latest"
    if up_or_down == "up":
        call(cmd)
    elif up_or_down == "down":
        call("docker stop registry")
        call("docker rm registry")
        if clean_volume:
            call("sudo rm -rf /var/lib/registry")
    else:
        raise click.ClickException("Invalid command")


@click.command(name="list-registry")
@click.option("--host", type=str, default="localhost:5555")
def list_registry(host: str):  # type: ignore
    response = requests.get(f"http://{host}/v2/_catalog")
    if response.status_code == 200:
        repositories = response.json().get("repositories", [])
        click.echo(f"Repositories: {repositories}")
    else:
        click.echo(f"Failed to fetch repositories: {response.status_code}")
