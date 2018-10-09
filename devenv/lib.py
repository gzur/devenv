#!/usr/bin/env python3
import os
import docker
import hashlib
import io
import logging

# TODO:
#   * Namespaced bash history
#   * Cross-platform compatibility
#   * Override default shell command

log = logging.getLogger(__file__)
DEFAULT_BASE_IMAGE = 'centos:6'
DOCKERFILE = """
FROM {base_image}
"""
DOCKERFILE_END = """
ENV PS1="\[\e[31m\](devenv) \[\e[m\] \\u@{env_id} \w\$ "
ENV PS1="\[\e[31m\](devenv)\[\e[m\] \\u@{env_id} \w\$ "
WORKDIR /{work_dir}
RUN echo -e '#!/bin/bash\\nls -la "$@"' > /usr/bin/ll && chmod +x /usr/bin/ll
"""
client = docker.from_env()
api_client = docker.APIClient()


def delete_containers(env_identifier=None):
    # only delete containers belonging to this environment
    if env_identifier is None:
        env_identifier = get_environment_identifier()
    filter_str = 'owner={env_identifier}'.format(env_identifier=env_identifier)
    deleted = client.containers.prune(dict(label=filter_str))
    container_ids = ",".join(deleted.get('ContainersDeleted') or [])
    return container_ids


def delete_images(name):
    # only delete the image belonging to this environment
    try:
        client.images.remove(name, force=True, noprune=True)
        return True
    except docker.errors.ImageNotFound:
        return False


def restart_shell(container_name):
    os.system("docker start -a -i {container_name}".format(
        container_name=container_name))


def commit_container(temporary=False):
    container_name = get_container_name()
    container = get_container(container_name)
    if container is None:
        return "No container found for environment."
    else:
        image_id = get_environment_identifier(temporary=temporary)
        container.commit(image_id)
    return "Container commited as: {image}".format(image=image_id)


def generate_vol_string(volumes):
    vol_str = ""
    for vol in volumes:
        vol_str += " -v {vol} ".format(vol=vol)
    return vol_str


def start_new_shell(env_id, container_name,
                    user_volumes=tuple,
                    env_file=None,
                    entrypoint='/bin/bash',
                    docker_opts=' ',
                    restore_from_tmp=False):
    env_file_str = ""
    if env_file is not None:
        env_file_str = "--env-file {env_file}".format(env_file=env_file)
    default_volumes = (
        "{host_dir}:{container_dir}".format(
            host_dir=os.getcwd(),
            container_dir='/{dir_name}'.format(
                dir_name=get_dirname())),
        "~/.gitconfig:/root/.gitconfig",
        "`pwd`/.devenv-home-dir:/root",
    )
    volumes = default_volumes + user_volumes
    volume_str = generate_vol_string(volumes)
    log.debug("Volume string generated: {vol_str}".format(vol_str=volume_str))
    cmd = "docker run -i -t {volumes} " \
        "--label=owner={env_id} " \
        "--name={container_name} " \
        "{docker_opts} " \
        "{env_file_str} " \
        "{image_id} " \
        "{entrypoint}".format(
            image_id=env_id,
            env_id=env_id,
            container_name=container_name,
            docker_opts=docker_opts,
            volumes=volume_str,
            env_file_str=env_file_str,
            entrypoint=entrypoint,
        )
    log.debug("Docker command: [cmd]".format(cmd=cmd))
    print("Docker command: {cmd}".format(cmd=cmd))
    return os.system(cmd)


def get_dirname(dir_path=None):
    if dir_path is None:
        dir_path = os.getcwd()
    return os.path.basename(dir_path)


def get_environment_identifier(temporary=False):
    dir_path = os.getcwd()
    dir_name = get_dirname(dir_path)
    tmp_str = ""
    if temporary:
        tmp_str += "_tmp"
    hasher = hashlib.sha1()
    hasher.update(dir_path.encode())
    return "{dirname}_{path_hash}{tmp_str}".format(
        dirname=dir_name,
        tmp_str=tmp_str,
        path_hash=hasher.hexdigest()[:8]
    )


def get_image(name):
    try:
        return client.images.get(name)
    except docker.errors.ImageNotFound:
        return None


def get_container(container_id_or_name):
    try:
        return client.containers.get(container_id_or_name)
    except docker.errors.NotFound:
        return None


def get_container_name() -> str:
    return "container_{image_name}".format(image_name=get_environment_identifier())


def build_image(force=False, dockerfile_path=None, base_image=None):
    docker_file_str = DOCKERFILE.format(base_image=DEFAULT_BASE_IMAGE)

    if base_image is not None:
        docker_file_str = DOCKERFILE.format(base_image=base_image)

    elif dockerfile_path is not None:
        with open(dockerfile_path, 'r') as dockerfile:
            docker_file_str = dockerfile.read()
            docker_file_str

    docker_file_str += DOCKERFILE_END
    docker_file = io.BytesIO(docker_file_str.format(
        env_id=get_environment_identifier(),
        work_dir=get_dirname()
    ).encode())

    env_identifier = get_environment_identifier()
    build_params = dict(
        fileobj= docker_file,
        tag=env_identifier,
        nocache=force is True
    )
    yield api_client.build(**build_params)
