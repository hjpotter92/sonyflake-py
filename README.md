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
- `machine_id` should be a callable which returns an integer value
  upto 16-bits.

## License

The MIT License (MIT).


  [codecov]: https://codecov.io/gh/hjpotter92/sonyflake-py
  [codecov-badge]: https://codecov.io/gh/hjpotter92/sonyflake-py/branch/master/graph/badge.svg?token=XZCRNSSSQK
  [readthedocs]: http://sonyflake-py.rtfd.io/
  [readthedocs-badge]: https://readthedocs.org/projects/sonyflake-py/badge/?version=latest
  [travis-ci]: https://travis-ci.com/hjpotter92/sonyflake-py
  [travis-ci-badge]: https://travis-ci.com/hjpotter92/sonyflake-py.svg?branch=master
