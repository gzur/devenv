import os
import docker
from devenv.lib import generate_image_name, get_container_name
from devenv.cli import _build_wrapper
test_client = docker.from_env()

TEST_DIR = '/tmp'


def test_env_identifier():
    os.chdir(TEST_DIR)
    test_name = generate_image_name()
    assert(test_name == "tmp_d0f036b9")


def test_container_name():
    os.chdir(TEST_DIR)
    container_name = get_container_name()
    env_name = generate_image_name()
    assert(container_name == "container_{env_name}"
           .format(env_name=env_name))


def test_build_container():
    os.chdir(TEST_DIR)
    _build_wrapper()
    image_name = generate_image_name()
    image = test_client.images.get(image_name)
    assert(image_name is not None)
    assert(image_name in [x.split(':')[0] for x in image.tags])


def test_delete_container():
    os.chdir('/tmp/')
    image_name = generate_image_name()
    test_client.images.remove(image_name)
    # If we made it this far, we're gucci.
    assert True
