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

## Examples

There is no formal doc about the accepted grammar (check _parser.py_),
but you can find some examples in the `examples` folder.

## Development

### Run tests

To run the unit tests, execute `pytest`.


### Run differential testing

To check that a new optimization does not introduces bugs, it is possible to
use [hrm-interpreter](https://github.com/alfateam123/hrm-interpreter)
and a custom script to compile the examples with different flags and run the different
builds.

To be able to perform this kind of testing:

1. install rust and cargo via rustup
2. clone and build `hrm-interpreter` in the parent directory of this repository
3. run `run_all_on_interpreter.py`

If something is wrong, you should see an AssertionError.
