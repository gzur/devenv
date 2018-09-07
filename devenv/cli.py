#!/usr/bin/env python3
import os
import json
import click
from devenv.lib import get_container_name, \
    get_container, \
    get_environment_identifier,\
    get_image, \
    delete_containers, \
    delete_images, \
    restart_shell, \
    start_new_shell, \
    get_dirname, \
    _build

@click.group()
@click.option('--debug/--no-debug', default=False,
              envvar='REPO_DEBUG')
def cli(**kwargs):
    pass

@cli.command()
@click.option('--verbose', is_flag=True, type=click.BOOL,
              help='Enable verbose output')
def shell(verbose=False):
    env_id = get_environment_identifier()
    container_name = get_container_name()
    image_name = get_environment_identifier()
    if get_image(image_name) is None:
        # Transparently build an image if one does not exist.
        _build_wrapper(verbose=verbose)

    if get_container(container_name) is not None:
        click.echo("Container exists - resuming")
        restart_shell(container_name)
    else:
        # TODO: Allow the user to change what is volume mounted.
        volumes = "{host_dir}:{container_dir}"\
            .format(host_dir=os.getcwd(), container_dir='/{dir_name}'.format(dir_name=get_dirname()))

        start_new_shell(env_id, container_name, volumes)
    click.echo("Exited. (Run \"devenv commit\" to save state")


@cli.command()
def push():
    click.echo("PSYCH! - Not implemented ... yet")


@cli.command()
def commit():
    container_name = get_container_name()
    container = get_container(container_name)
    if container is None:
        click.echo("No container found for environment.")
    else:
        image_id = get_environment_identifier()
        container.commit(image_id)
        click.echo("Container commited as: {image}".format(image=image_id))


@cli.command()
def clean():
    deleted_containerws = delete_containers()
    if delete_containers:
        click.echo("Deleted containers: {containers}"
                   .format(containers=deleted_containerws))

    image_to_delete = get_environment_identifier()

    deleted_image = delete_images(image_to_delete)
    if deleted_image:
        click.echo("Deleted image {image_name}"
                   .format(image_name=image_to_delete))


@cli.command()
@click.option('--force', is_flag=True, type=click.BOOL,
              help='Overwrite existing images')
@click.option('--dockerfile', type=click.STRING,
              help='Specify Dockerfile to base the environment on.')
@click.option('--image', type=click.STRING,
              help='Specify an existin image to base environment on.')
@click.option('--verbose', is_flag=True, type=click.BOOL,
              help='Enable verbose output')
def build(force=False, verbose=True, dockerfile=None, image=None):
    if force:
        click.echo("Forcing new image {image_name}"
                   .format(image_name=get_environment_identifier()))
    _build_wrapper(force, verbose, dockerfile, image)


def _build_wrapper(force=False, verbose=True, dockerfile=None, image=None):
    build_output = _build(force, dockerfile, image)
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
            line = decoded_line.get('stream')
            if line:
                if verbose:
                    click.echo(line, nl=False)
            else:
                if line:
                    line = decoded_line.get('aux')
                    click.echo(line.get('ID'))



@click.group('internal')
def internal():
    pass


@click.command()
def image_name():
    click.echo(get_environment_identifier())


internal.add_command(image_name)

if __name__ == '__main__':
    cli()