import os, pty
import docker
from devenv.lib import get_environment_identifier, \
    get_container_name, build_image, start_new_shell, get_container

test_client = docker.from_env()


def test_env_identifier():
    os.chdir('/tmp')
    test_name = get_environment_identifier()
    assert(test_name == "tmp_d0f036b9")


def test_container_name():
    os.chdir('/tmp')
    container_name = get_container_name()
    env_name = get_environment_identifier()
    assert(container_name == "container_{env_name}"
           .format(env_name=env_name))


def test_build_container():
    os.chdir('/tmp')
    build_image()
    image_name = get_environment_identifier()
    test_client.images.get(image_name)
    assert(image_name is not None)


# def test_start_container():
#     os.chdir('/tmp')
#     build_image()
#     env_name = get_environment_identifier()
#     container_name = get_container_name()
#
#     start_new_shell(env_name, container_name, "")
#
#     container = get_container(container_name)
#     assert(container is not None)


def test_delete_container():
    os.chdir('/tmp')
    container_name = get_container_name()
    env_name = get_environment_identifier()
    assert(container_name == "container_{env_name}"
           .format(env_name=env_name))
