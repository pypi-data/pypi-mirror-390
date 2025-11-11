# Introduction

An arithmetic expression calculator in Python, demoing the Pratt
parsing algorithm.

This takes inspiration from [this 2010 blog
post](https://eli.thegreenplace.net/2010/01/02/top-down-operator-precedence-parsing)
by Eli Bendersky, as well as a few other sources, which I'll touch on
in a future blog post.

# Installation

## Using `uv`

1. [Make sure](https://docs.astral.sh/uv/getting-started/installation/) `uv` is
installed in your system.

2. `git clone https://github.com/BrandonIrizarry/pratt_calc && cd !$`

3. `uv sync`

## Conventional

1. `git clone https://github.com/BrandonIrizarry/pratt_calc && cd !$`

2. `python -m venv venv`

3. `source venv/bin/activate`

4. `pip install .` 

# Usage

`./pratt_calc $EXPRESSION`

Example: 

`./pratt_calc '3-4*5'`

This should print -17 at the console.

# TODO

- [ ] add support for running the tests.
- [ ] CI?

