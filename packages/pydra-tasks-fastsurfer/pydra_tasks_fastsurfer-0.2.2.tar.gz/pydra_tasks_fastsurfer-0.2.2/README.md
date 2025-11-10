# Pydra task package for fastsurfer

[![CI/CD](https://github.com/nipype/pydra-tasks-fastsurfer/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/nipype/pydra-tasks-fastsurfer/actions/workflows/ci-cd.yaml)
[![Codecov](https://codecov.io/gh/nipype/pydra-tasks-fastsurfer/branch/main/graph/badge.svg?token=UIS0OGPST7)](https://codecov.io/gh/nipype/pydra-tasks-fastsurfer)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pydra-tasks-fastsurfer.svg)](https://pypi.python.org/pypi/pydra-tasks-fastsurfer/)
[![Latest Version](https://img.shields.io/pypi/v/pydra-tasks-fastsurfer.svg)](https://pypi.python.org/pypi/pydra-tasks-fastsurfer/)

This package contains a Pydra interface for the fastsurfer toolkit.t.


## Tests

This package comes with a battery of automatically generated test modules. To install the necessary dependencies to run the tests, use the following command:

the necessary dependencies to run the tests

```
   $ pip install -e .[test]
```

Then the tests, including [doctests](https://docs.python.org/3/library/doctest.html), can be launched using

```
   $ pytest --doctest-modules pydra/tasks/*
```


By default, the tests are set to time-out after 10s, after which the underlying tool is
assumed to have passed the validation/initialisation phase and we assume that it will
run to completion. To disable this and run the test(s) through to completion run

```
   $ pytest --doctest-modules --timeout-pass 0 pydra/tasks/*
```


## Contributing to this package

### Developer installation

Install repo in developer mode from the source directory and install pre-commit to
ensure consistent code-style and quality.

```
   $ pip install -e .[test,dev]
   $ pre-commit install
```


### Typing and sample test data

The automatically generated tests will attempt to provided the task instance to be tested
with sensible default values based on the type of the field and any constraints it has
on it. However, these will often need to be manually overridden after consulting the
underlying tool's documentation.

For file-based data, automatically generated file-system objects will be created for
selected format types, e.g. Nifti, Dicom. Therefore, it is important to specify the
format of the file using the "mime-like" string corresponding to a
[fileformats](https://github.com/ArcanaFramework/fileformats) class
in the ``inputs > types`` and ``outputs > types`` dicts of the YAML spec.

If the required file-type is not found implemented within fileformats, please see the [fileformats
docs](https://arcanaframework.github.io/fileformats/developer.html) for instructions on how to define
new fileformat types, and see 
[fileformats-medimage-extras](https://github.com/ArcanaFramework/fileformats-medimage-extras/blob/6c2dabe91e95687eebc2639bb6f034cf9595ecfc/fileformats/extras/medimage/nifti.py#L30-L48)
for an example on how to implement methods to generate sample data for them.
