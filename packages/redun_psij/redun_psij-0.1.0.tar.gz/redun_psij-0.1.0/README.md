# redun_psij

This package enables Redun tasks to be scheduled on any job scheduler supported by PSI/J, which includes Slurm, PBS, LFS among others.

It is not tightly integrated into Redun, and therefore has a different flavour than the executors natively supported in Redun.

## Installation

The package is pure Python with its only dependencies being [redun](https://insitro.github.io/redun/index.html) and [PSI/J](https://exaworks.org/psij-python/index.html).  It is available on PyPI or as Nix flake.

## Features

- job specs are defined in [Jsonnet](https://jsonnet.org/)

## Usage

_To be completed_

## Status

This code is in production using a Slurm backend.  No other job schedulers have been tested.
