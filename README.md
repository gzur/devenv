# `devenv` - general-purpose dockerized shell environment manager.

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

### Run shell
```bash
devenv shell
```
### Build
#### Specify your own base image.
By default, `devenv` ships using the centos:6 docker image as a base image. This can be overridden via the command line:
```bash
devenv build --verbose --image=python:37
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

