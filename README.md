HRM Compiler
============

Work-in-progress compiler to have an high-level tool
to reason about problems in Human Resources Machines.

I hate pseudo-assembly, and I want to write a compiler.

## Install

```
virtualenv .hrm
source .hrm/bin/activate

pip install -e .
```

## Usage

`hrmc <script>`

## Run tests

Use `pytest`, it will find all the tests.
I don't have end-to-end tests (from source language to target language) though.

## Examples

There is no formal doc about the accepted grammar (check _parser.py_),
but you can find some examples in the `examples` folder.

## Source code location

The version hosted on [github](https://github.com/alfateam123/hrm-compiler) is a mirror of the version hosted on
the self-hosted version at [wintermade.it/code/winterthediplomat/HRM-compiler](https://wintermade.it/code/winterthediplomat/HRM-compiler).

