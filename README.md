# sonyflake-py

[![codecov][codecov-badge]][codecov] [![Build Status][travis-ci-badge]][travis-ci] [![Documentation Status][readthedocs-badge]][readthedocs]


Sonyflake is a distributed unique ID generator inspired by [Twitter's
Snowflake](https://blog.twitter.com/2010/announcing-snowflake).

This is a python rewrite of the original
[sony/sonyflake](https://github.com/sony/sonyflake) project, written
in Go.

A Sonyflake ID is composed of

    39 bits for time in units of 10 msec
     8 bits for a sequence number
    16 bits for a machine id

## Installation

``` shell
pip install sonyflake-py
```

## Quickstart

``` python
from sonyflake import SonyFlake
sf = SonyFlake()
next_id = sf.next_id()
print(next_id)
```

The generator can be configured with variety of options, such as
custom `machine_id`, `start_time` etc.

- `start_time` should be an instance of `datetime.datetime`.
- `machine_id` should be an integer value upto 16-bits, callable or
  `None` (will be used random machine id).

If you need to generate ids at rate more than 256ids/10msec, you can use the `RoundRobin` wrapper over multiple `SonyFlake` instances:

``` python
from timeit import timeit
from sonyflake import RoundRobin, SonyFlake, random_machine_ids
sf = RoundRobin([SonyFlake(machine_id=_id) for _id in random_machine_ids(10)])
t = timeit(sf.next_id, number=100000)
print(f"generated 100000 ids in {t:.2f} seconds")
```

> :warning: This increases the chance of collisions, so be careful when using random machine IDs.

For convenience, both `SonyFlake` and `RoundRobin` implement iterator protocol (`next(sf)`).

## License

The MIT License (MIT).


  [codecov]: https://codecov.io/gh/hjpotter92/sonyflake-py
  [codecov-badge]: https://codecov.io/gh/hjpotter92/sonyflake-py/branch/master/graph/badge.svg?token=XZCRNSSSQK
  [readthedocs]: http://sonyflake-py.rtfd.io/
  [readthedocs-badge]: https://readthedocs.org/projects/sonyflake-py/badge/?version=latest
  [travis-ci]: https://travis-ci.com/hjpotter92/sonyflake-py
  [travis-ci-badge]: https://travis-ci.com/hjpotter92/sonyflake-py.svg?branch=master
