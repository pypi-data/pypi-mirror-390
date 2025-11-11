<!-- This disables the "First line in file should be a top level heading" rule -->
<!-- markdownlint-disable MD041 -->
<a href="https://github.com/alexandrainst/bits_and_bobs">
<img
 src="https://filedn.com/lRBwPhPxgV74tO0rDoe8SpH/alexandra/alexandra-logo.jpeg"
 width="239"
 height="175"
 align="right"
 alt="Alexandra Institute Logo"
/>
</a>

# Bits And Bobs

General utility functions with no dependencies.

______________________________________________________________________
[![Code Coverage](https://img.shields.io/badge/Coverage-81%25-yellowgreen.svg)](https://github.com/alexandrainst/bits_and_bobs/tree/main/tests)
[![Documentation](https://img.shields.io/badge/docs-passing-green)](https://alexandrainst.github.io/bits_and_bobs)
[![License](https://img.shields.io/github/license/alexandrainst/bits_and_bobs)](https://github.com/alexandrainst/bits_and_bobs/blob/main/LICENSE)
[![LastCommit](https://img.shields.io/github/last-commit/alexandrainst/bits_and_bobs)](https://github.com/alexandrainst/bits_and_bobs/commits/main)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](https://github.com/alexandrainst/bits_and_bobs/blob/main/CODE_OF_CONDUCT.md)

Developer:

- Dan Saattrup Smart (<dan.smart@alexandra.dk>)

## Installation

Install the package via uv or pip:

```bash
uv add bits_and_bobs
```

or

```bash
pip install bits_and_bobs
```

## Overview of the utility functions

The package currently includes the following utility functions:

### `cache_arguments`

An extension of the `functools.cache`/`functools.lru_cache` decorators, which can also
cache specific arguments of a function, rather than always including all arguments. This
is useful if you have a function with some arguments that do not affect the output, for
instance a logging message or a verbosity flag.

Here is an example of how to use it:

```python
>>> import bits_and_bobs as bnb
>>>
>>> @bnb.cache_arguments(["x", "y"])
>>> def add(x: int, y: int, logging_message: str = "Computing...") -> int:
... print(logging_message)
... return x + y
>>>
>>> # This will compute and cache the result
>>> print(add(1, 2))
Computing...
3
>>>
>>> # This will use the cached result, since x and y are the same
>>> print(add(1, 2, logging_message="This will not be printed"))
3
```

### `no_terminal_output`

A context manager that suppresses all terminal output. This blocks all Python output,
but also all output from underlying C/C++/Fortran libraries. This is useful if you want
to silence noisy libraries, for instance in Terminal User Interfaces (TUIs).

Use it like this:

```python
>>> import bits_and_bobs as bnb
>>>
>>> print("This will be printed")
This will be printed
>>>
>>> with bnb.no_terminal_output():
...  print("This will NOT be printed")
>>>
>>> # We can specify a condition that disables the suppression
>>> def print_if_debug():
...  with bnb.no_terminal_output(disable_condition=lambda: os.getenv("DEBUG") == "1"):
...   print("This will be printed only if DEBUG=1")
>>> print_if_debug()
>>> os.environ["DEBUG"] = "1"
>>> print_if_debug()
This will be printed only if DEBUG=1
```

### `only_allow_specific_loggers`

This function restricts logging output to only the specified loggers, suppressing all
others. This is useful if you care about log messages from only a few specific
loggers and want to ignore the rest, usually coming from third-party libraries.

Here is an example of how to use it:

```python
>>> import bits_and_bobs as bnb
>>> import logging
>>>
>>> logger1 = logging.getLogger("logger1")
>>> logger2 = logging.getLogger("logger2")
>>>
>>> bnb.only_allow_specific_loggers(["logger1"])
>>>
>>> logger1.warning("This will be printed")
WARNING:logger1:This will be printed
>>>
>>> logger2.warning("This will NOT be printed")
```
