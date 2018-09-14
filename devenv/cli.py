#!/usr/bin/env python3
import os
import json
import click
from devenv.lib import \
    get_container_name, \
    get_container, \
    get_environment_identifier,\
    get_image, \
    delete_containers, \
    delete_images, \
    commit_container, \
    restart_shell, \
    start_new_shell, \
    get_dirname, \
    build_image


_global_test_options = [
    click.option('--verbose', '-v', 'verbosity',
                 flag_value=2,
                 default=1,
                 help='Verbose output'),
    click.option('--quiet', '-q', 'verbosity',
                 flag_value=0,
                 help='Minimal output'),
    click.option('--force', '-f',
                 is_flag=True,
                 default=False,
                 help='Stop on failure'),
]

def global_test_options(func):
    for option in reversed(_global_test_options):
        func = option(func)
    return func

@click.group()
@click.option('--debug/--no-debug', default=False,
              envvar='REPO_DEBUG')
def cli(**kwargs):
    pass


@cli.command()
@global_test_options
@click.option('--dockerfile', type=click.STRING,
              help='Specify Dockerfile to base the environment on.')
@click.option('--image', type=click.STRING,
              help='Specify an existin image to base environment on.')
@click.option('--volume', type=click.STRING, multiple=True, help="Specify volume mounts of the form ]"
                                                  "[host_path]:[container_path]")
@click.option('--new', is_flag=True, type=click.BOOL)
def shell(**kwargs):
    user_volumes = kwargs.pop('volume', tuple())
    restart_container = kwargs.pop('new', False)
    container_name = get_container_name()
    env_id = get_environment_identifier()
    if get_image(env_id) is None:
        # Transparently build an image if one does not exist.
        _build_wrapper(**kwargs)

    default_volumes = "{host_dir}:{container_dir}" \
        .format(host_dir=os.getcwd(),
                container_dir='/{dir_name}'.format(
                    dir_name=get_dirname()))

    volumes = (default_volumes,) + user_volumes
    if restart_container:
        commit_container()
        delete_containers()
    if get_container(container_name) is not None:
        click.echo("Container exists - resuming")
        restart_shell(container_name)
    else:
        start_new_shell(env_id, container_name, volumes)
    click.echo("Exited. (Run \"devenv commit\" to save state")


@cli.command()
def push():
    click.echo("PSYCH! - Not implemented ... yet")


@cli.command()
def commit():
    click.echo(commit_container())


@cli.command()
@click.option('--all', is_flag=True,
              type=click.BOOL,
              default=False,
              help='Also delete image')
def clean(all=False):
    deleted_containerws = delete_containers()
    if delete_containers:
        click.echo("Deleted containers: {containers}"
                   .format(containers=deleted_containerws))

    import ipdb;ipdb.set_trace()
    if all:
        image_to_delete = get_environment_identifier()

        deleted_image = delete_images(image_to_delete)
        if deleted_image:
            click.echo("Deleted image {image_name}"
                       .format(image_name=image_to_delete))


@cli.command()
@click.option('--dockerfile', type=click.STRING,
              help='Specify Dockerfile to base the environment on.')
@click.option('--image', type=click.STRING,
              help='Specify an existin image to base environment on.')
@global_test_options
def build(force=False, verbosity=1, dockerfile=None, image=None):
    if force:
        click.echo("Forcing new image {image_name}"
                   .format(image_name=get_environment_identifier()))
    _build_wrapper(force, verbosity, dockerfile, image)


def _build_wrapper(force=False, verbosity=1, dockerfile=None, image=None):
    build_output = build_image(force, dockerfile, image)
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
                if verbosity > 1:
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