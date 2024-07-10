# SpecSheet

## Overview

To do: Write the overview for this project.

## Pre-requisites

Before any installation of the define pre-requisites, it is recommended to install the packages that may cause build issues if they are not present in your machine,

- Arch Linux

```shell
pacman -S --needed base-devel openssl zlib xz tk
```

- Fedora

```shell
dnf install make gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel cmake
dnf install “@development-tools”
dnf group install “C Development Tools and Libraries”
```

- Ubuntu

```shell
sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

We can now install the pre-requisites,

- pyenv + pyenv-virtualenv
  - Using the pyenv installer is recommended,

```shell
curl https://pyenv.run | bash
```

- poetry
  - Using the legacy installer is recommended,

```
curl -sSL https://install.python-poetry.org | python3 -
```

## Setup

We set up a development environment for by creating a virtual environment using pyenv-virtualenv.

First, we install Python 3.11.9,

```shell
pyenv install 3.11.9
```

Then we create a virtual environment for the repository,

```shell
cd specsheet  # in case specsheet is not the current directory
pyenv virtualenv 3.11.9 $(basename $PWD)
pyenv local $(basename $PWD)  # permanently set and activate the virtualenv when entering this dir
```

If this is the first time poetry has been set up in your machine, we configure it not to create its own virtual environment,

```shell
poetry config virtualenvs.create false
```

We should also configure poetry to use the pyenv virtual environments,

```shell
poetry config virtualenvs.path ~/.pyenv/versions/3.11.9
```

In case it was not enabled by default, we should enable parallel installation,

```shell
poetry config installer.parallel true
```

We should also tell poetry to prefer the active Python in the virtual environment,

```
poetry config virtualenvs.prefer-active-python true
```

To confirm that our configuration has been properly set, we use the following command,

```shell
poetry config --list
```

...and we should expect an output similar to this one,

```
cache-dir = "/home/afagarap/.cache/pypoetry"
experimental.new-installer = true
experimental.system-git-client = false
installer.max-workers = null
installer.no-binary = null
installer.parallel = true
virtualenvs.create = false
virtualenvs.in-project = null
virtualenvs.options.always-copy = false
virtualenvs.options.no-pip = false
virtualenvs.options.no-setuptools = false
virtualenvs.options.system-site-packages = false
virtualenvs.path = "/home/afagarap/.pyenv/versions/3.11.9"
virtualenvs.prefer-active-python = true
virtualenvs.prompt = "{project_name}-py{python_version}"
```

To set up poetry for this repository, we configure poetry to use the Python version of its virtual environment like so,

```shell
cd specsheet  # in case specsheet is not the current directory
poetry env use $(pyenv which python)
```

...which should output a message similar to as follows,

```
3.11.9
Skipping virtualenv creation, as specified in config file.
Using virtualenv: /home/afagarap/.pyenv/versions/3.11.9
```

Finally, we can now install the dependencies,

```shell
cd specsheet  # in case specsheet is not the current directory
poetry install
pre-commit install  # install pre-commit hooks
```

## Usage

To do: Write usage guideline once a stand-in app has been implemented.

## Contributing

To do: Write contributing guideline.

## License

Full license is available [here](LICENSE)

```
Copyright (C) NeoAlpha Global - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
```
