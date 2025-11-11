# FleCSI Skeleton Package (skelf)

## Create Python Environment

The best way to build this package for development is to create a python
environment:
```shell
$ python -m venv --prompt skelf-devel .venv
$ source .venv/bin/activate
$ pip install build twine
```
Then you can build like:
```shell
$ pip install -ve .
```

## Publish

```shell
$ twine upload dist/*
```
