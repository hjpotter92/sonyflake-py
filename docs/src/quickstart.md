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
