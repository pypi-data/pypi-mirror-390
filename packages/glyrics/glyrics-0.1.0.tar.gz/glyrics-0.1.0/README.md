# glyrics - Flask app for fetching song lyrics from the Genius API

This repository contains the source code for the `glyrics` API server which
fetches song lyrics from the Genius API.

## Installation

1.  Clone the repository.
    ```shell
    $ git clone git@github.com:will2dye4/glyrics.git
    $ cd glyrics
    ```

1.  Edit the config file as needed for your environment.
    ```shell
    $ $EDITOR glyrics/config/config.json
    ```

## Running the Server

**NOTE:** `glyrics` depends on [Python](https://www.python.org/downloads/) 3.10
or newer; please ensure that you have a semi-recent version of Python installed
before proceeding.

### Running Locally

To run the server locally, run the following from the root of the repository:

```shell
$ pip install .
$ glyrics
```

### Deploying to gunicorn

To run the server using `gunicorn`, run the following:

```shell
$ pip install .
$ pip install gunicorn
$ gunicorn -c glyrics/config/gunicorn.conf.py 'glyrics:app'
```

