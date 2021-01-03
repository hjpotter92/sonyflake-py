# sonyflake-py

Sonyflake is a distributed unique ID generator inspired by [Twitter's Snowflake](https://blog.twitter.com/2010/announcing-snowflake).

This is a python rewrite of the original [sony/sonyflake](https://github.com/sony/sonyflake) project, written in Go.

A Sonyflake ID is composed of

    39 bits for time in units of 10 msec
     8 bits for a sequence number
    16 bits for a machine id

## Installation

``` shell
pip install sonyflake-py
```

## License

The MIT License (MIT).
