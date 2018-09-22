# Development Environment Manager

## Main features:
  * Persist installed packages, configuration and bash history for later.
  * Automatically mount your project into the environment.
  * Automatically discover previously built/modified enviroments (based on project path)
  * Specify what base docker image to build environments on top off..
 
# Quickstart

1. Clone this repository and run
```bash
make install
```
2. Go to the root directory of your project and run
```bash
devenv shell
```
3. PROFIT!

# Usage
All of the below assumes you to be located in your project directory.
`devenv` bases all of its assumptions on where you are located on a file-system level.

### Build
_*Note:* All options accepted by `build` are also applicable to `shell`_
#### Specify your own base image.
By default, `devenv` ships using the centos:6 docker image as a base image. This can be overridden via the command line:
```bash
devenv build --verbose --base_image=python:37
```
Any subsequent `devenv shell` commands run inside the same directory, will default to this image until `devenv clean` is run.

#### Override the default Dockerfile:
```bash
devenv build --verbose --dockerfile=./Dockerfile
```

### Commit
After you have exited an environment, you can commit whatever you did while inside the environment to a Docker image:

```
devenv commit
```

### Cleanup
```
devenv clean
```
### Shell
_*Note:* All options accepted by `build` are also applicable to `shell`_
```bash
devenv shell
```
#### Override base-image
 Start shell in docker container based off ubuntu - rather than the default centos.
```bash
devenv shell --verbose --base_image=ubuntu:latest 
```
#### User-defined volume mounts:
```bash
devenv shell --volume=/tmp:/tmp --volume ~.aws:/root/.aws
```
#### User-defined volume mount to an existing environment:
Docker does not allow new volumes to be mounted on existing containers.
To circumvent this limitation, the `-—new` option causes the following to be performed:
  1. commit the existing environment container to a new image (overwriting any previous image)
  2. delete the existing container
  3. recreate the container (based on the image from step #1) with the new volume mounts.

This allows us to specify new volumes for an existing environment.

_**Note**: Existing volume mounts need to be re-specified when invoking `--new`_
```bash
devenv shell --new --volume=/tmp:/tmp --volume ~.aws:/root/.aws --volume /var/log:/var/log
```