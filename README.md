<div align="center">
    <a href="http://contamehistorias.pt/arquivopt/" target="_blank">
	    <img width="300" height="250" src="img/vintage-typewriter.png" alt="Conta-me Histórias">
    </a>
    <br>
    <b> This repository contains the source code of the back-end server of <a href="http://contamehistorias.pt/arquivopt/" target="_blank">conta-me historias</a>. </b>

</div>


## Web application

[![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue.svg)](https://www.python.org/)


The [conta-me historias](http://contamehistorias.pt/arquivopt/) web application depends on:
    
- the front-end [user interface](https://github.com/LIAAD/contamehistorias-ui)
- the back-end API to retrieve data (this repository)

See [UI](https://github.com/LIAAD/contamehistorias-api) for instructions on how to run the front-end server.


### Setup

It is recommended to setup a [virtual environment](https://docs.python.org/3.8/library/venv.html).

The API uses a RedisJSON server as cache system. While the back-end still works without cache, it is recommended to run the Redis server, for a better experience. See [RedisJSON](https://github.com/RedisJSON/RedisJSON) for instructions on how to run the server.

#### Install requirements

```shell
$ pip install -r requirements.txt
```

#### Run server

```shell
$ cd api/
```

Directly from python

```shell
$ python app.py
```

or through Gunicorn

```shell
$ sh run.sh
```

### LIAAD dependencies

This project uses the following LIAAD software:

- [Conta-me Historias Temporal Summarization](https://github.com/LIAAD/TemporalSummarizationFramework)
- [PAMPO](https://github.com/LIAAD/py-pampo)
