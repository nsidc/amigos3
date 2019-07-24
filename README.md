# AMIGOS III operations command line interface

## Development

### Getting started

Dependencies in the development environment are managed with [Conda](https://docs.conda.io/en/latest/index.html).

1. Initialize submodules (run in repository root directory)

    ```
    $ git submodule init && git submodule update
    ```

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anoconda](https://www.anaconda.com/distribution/)

1. Create the environment (run in repository root directory)

    ```
    $ conda env create -f environment.yml
    ```

    This will create a 'amigos' environment with the correct version of python and dependencies for the project.

1. Activate the environment

    ```
    $ conda activate amigos
    ```

1. Install amigos CLI commands (local to source directory)

    ```
    $ python setup.py develop
    ```

### Running tests

Due to poor support for Python 2.6, tests are run in a separate Python 2.7 environment. Easy way:

```
make test
```

Hard way:

1. from the repository directory, run


    ```
    $ conda env create -f environment-testing.yml
    ```

    This will create a 'amigos' environment with the correct version of python and dependencies for the project.

1. Activate the environment

    ```
    $ conda activate amigos-testing
    ```

1. Run tests

    ```
    $ pytest --ignore amigos/ext
    ```

### Deployment

TODO
