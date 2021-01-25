# sonyflake-py

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
