# FleCSI Sandbox

This skeleton project will get you started with building and running a
FleCSI-based application.

# Spack Environment

Spack is the easiest way to build and run this example. You can install spack
following the instructions
[here](https://spack.readthedocs.io/en/latest/getting_started.html). Once you
have sourced the appropriate script for your shell, you can create a spack
environment like:

```shell
$ spack env create flecsi support/env.yaml
```

The contents of _env.yaml_ are similar to this content, which configures FleCSI
with the Legion backend:

```yaml
spack:
  specs:
  - flecsi
  packages:
    flecsi:
      require: '@2 +flog +graphviz +hdf5 backend=legion build_type=Debug'
    legion:
      require: 'network=gasnet conduit=mpi'
  view: true
  concretizer:
    unify: true
```
