#!/usr/bin/env python3
import sys
import json
import click
from devenv.lib import (
    get_container_name,
    get_container,
    generate_image_name,
    get_image,
    delete_containers,
    delete_images,
    commit_container,
    restart_shell,
    start_new_shell,
    build_image,
    test_docker_connection,
)


_global_test_options = [
    click.option('--verbose', '-v', 'verbosity', flag_value=2, default=1, help='Verbose output'),
    click.option('--quiet', '-q', 'verbosity', flag_value=0, help='Minimal output'),
    click.option('--force', '-f', is_flag=True, default=False, help='Stop on failure'),
]


def global_test_options(func):
    for option in reversed(_global_test_options):
        func = option(func)
    return func


@click.group()
@click.option('--debug/--no-debug', default=False, envvar='REPO_DEBUG')
def cli(**kwargs):
    if test_docker_connection() is False:
        error_msg("Could not connect to docker daemon. Is it running?")
        sys.exit(1)
    pass


@cli.command()
@global_test_options
@click.option(
    '--dockerfile', type=click.STRING, help='Specify Dockerfile to base the environment on.'
)
@click.option('--env_file', type=click.STRING, help='Load env from env file.')
@click.option(
    '--base_image', type=click.STRING, help='Specify an existing image to base environment on.'
)
@click.option(
    '--volume',
    type=click.STRING,
    multiple=True,
    help="Specify volume mounts using the normal docker syntax",
)
@click.option('--docker_opts', type=click.STRING, help='Forward random docker opts (Advanced).')
@click.option(
    '--new',
    is_flag=True,
    type=click.BOOL,
    help="Force the re-creation of the containers."
    "This is necessary if adding runtime options to an already running container,"
    "such as adding/removing ports or volume mounts."
    "Be aware that this option commits your container to a new image and starts"
    "a new container based on the committed image.",
)
def shell(**kwargs):
    # todo: there is way too much logic in here
    user_volumes = kwargs.pop('volume', tuple())
    restart_container = kwargs.pop('new', False)

    docker_opts = kwargs.pop("docker_opts") or " "

    container_name = get_container_name()
    env_id = generate_image_name()
    if get_image(env_id) is None:
        # Transparently build an image if one does not exist.
        _build_wrapper(
            kwargs.get("force"),
            kwargs.get("verbosity"),
            kwargs.get("dockerfile"),
            kwargs.get("base_image"),
        )

    if restart_container:
        commit_container(temporary=True)
        delete_containers()
    if get_container(container_name) is not None:
        click.echo("Container exists - resuming")
        restart_shell(container_name)
    else:
        start_new_shell(
            env_id,
            container_name,
            user_volumes,
            docker_opts=docker_opts,
            env_file=kwargs.get('env_file'),
        )
    click.echo("Exited. (Run \"devenv commit\" to save state")


@cli.command()
def init():
    click.echo("Marking directory as a developent environment")
    open(".devenv", "w+").close()
    _build_wrapper()
    container_name = get_container_name()
    env_id = generate_image_name()
    start_new_shell(env_id, container_name, tuple())


@cli.command()
def push():
    click.echo("PSYCH! - Not implemented ... yet")


@cli.command()
def commit():
    click.echo(commit_container())


@cli.command()
@click.option('--all', is_flag=True, type=click.BOOL, default=False, help='Also delete image')
def clean(all=False):
    deleted_containers = delete_containers()
    if delete_containers:
        click.echo("Deleted containers: {containers}".format(containers=deleted_containers))

    if all:
        image_to_delete = generate_image_name()

        deleted_image = delete_images(image_to_delete)
        if deleted_image:
            click.echo("Deleted image {image_name}".format(image_name=image_to_delete))


@cli.command()
@click.option(
    '--dockerfile', type=click.STRING, help='Specify Dockerfile to base the environment on.'
)
@click.option(
    '--base_image', type=click.STRING, help='Specify an existin image to base environment on.'
)
@global_test_options
def build(force=False, verbosity=1, dockerfile=None, base_image=None):
    if force:
        click.echo("Forcing new image {image_name}".format(image_name=generate_image_name()))
    _build_wrapper(force, verbosity, dockerfile, base_image)


# def _build_wrapper(force=False, verbosity=1, dockerfile=None, base_image=None):
def _build_wrapper(force=False, verbosity=1, dockerfile=None, base_image=None):
    build_output = build_image(force, dockerfile, base_image)
    last_line = None
    for x in next(build_output):
        decoded_lines = []
        try:
            lines_received = x.split(b"\r\n")
            for line in lines_received:
                if line:
                    as_json = json.loads(line.decode())
                    decoded_lines.append(as_json)
        except json.JSONDecodeError:
            bad = x.split(b"\r\n")
            for bad_line in bad:
                if bad_line:
                    as_json = json.loads(bad_line.decode())
                    decoded_lines.append(as_json)
        for decoded_line in decoded_lines:
            line = None
            if decoded_line.get('status') is not None:
                if decoded_line.get('status') == last_line:
                    line = "."
                else:
                    line = "\n" + decoded_line.get('status')
                last_line = decoded_line.get('status')
            else:
                line = (
                    decoded_line.get('stream')
                    or decoded_line.get('aux', {}).get('ID')
                    or "[No message decoded from line]" + json.dumps(decoded_line)
                )
            if line:
                # if verbosity > 1:
                click.echo(line, nl=False)
            else:
                message = None
                if decoded_line.get('errorDetail') is not None:
                    message = decoded_line.get('errorDetail', {})['message']
                if message:
                    error_msg("{}\n".format(message.strip()))
                    sys.exit(-1)


def error_msg(msg):
    click.echo(click.style("Error: %s" % msg, fg='red'))


@click.group('internal')
def internal():
    pass


@click.command()
def image_name():
    click.echo(generate_image_name())


internal.add_command(image_name)

if __name__ == '__main__':
    cli()
