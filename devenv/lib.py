#!/usr/bin/env python3
import os
import docker
import hashlib
import io
# from docker import APIClient

DEFAULT_BASE_IMAGE = 'centos:6'
DOCKERFILE = """
FROM {base_image}
"""

DOCKERFILE_END = """
ENV PS1='[\\u@{env_id} \w]\$ '
WORKDIR /{work_dir}
"""
client = docker.from_env()
api_client = docker.APIClient()


def delete_containers():
    # only delete containers belonging to this environment
    filter_str = 'owner={env_name}'.format(env_name=get_environment_identifier())
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
        container_name=container_name
    ))


def start_new_shell(env_id, container_name, volumes):

    return os.system("docker run -i -t -v {volumes} "
                     "--label=owner={env_id} "
                     "--name={container_name} "
                     "{env_id} "
                     "/bin/bash".format(
                         env_id=env_id,
                         container_name=container_name,
                         volumes=volumes))
def commit_container():
    container_name = get_container_name()
    container = get_container(container_name)
    if container is None:
        return "No container found for environment."
    else:
        image_id = get_environment_identifier()
        container.commit(image_id)
    return "Container commited as: {image}".format(image=image_id)


def get_dirname(dir_path=None):
    if dir_path is None:
        dir_path = os.getcwd()
    return os.path.basename(dir_path)


def get_environment_identifier():
    dir_path = os.getcwd()
    dir_name = get_dirname(dir_path)
    hasher = hashlib.sha1()
    hasher.update(dir_path.encode())
    return "{dirname}_{path_hash}".format(
        dirname=dir_name,
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


def _build(force=False, dockerfile_path=None, base_image=None):
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
