import datetime
import ipaddress
from functools import partial
from random import randrange
from socket import gethostbyname, gethostname
from threading import Lock
from time import sleep
from typing import Any, Callable, Dict, Iterator, Optional, Union
from warnings import warn

BIT_LEN_TIME = 39
BIT_LEN_SEQUENCE = 8
BIT_LEN_MACHINE_ID = 63 - (BIT_LEN_TIME + BIT_LEN_SEQUENCE)
MAX_MACHINE_ID = (1 << BIT_LEN_MACHINE_ID) - 1
UTC = datetime.timezone.utc
SONYFLAKE_EPOCH = datetime.datetime(2014, 9, 1, 0, 0, 0, tzinfo=UTC)
random_machine_id = partial(randrange, 0, MAX_MACHINE_ID + 1)
random_machine_id.__doc__ = "Returns a random machine ID."
utc_now = partial(datetime.datetime.now, tz=UTC)


def lower_16bit_private_ip() -> int:
    """
    Returns the lower 16 bits of the private IP address.
    """
    ip = ipaddress.ip_address(gethostbyname(gethostname()))
    ip_bytes = ip.packed
    return (ip_bytes[2] << 8) + ip_bytes[3]


class SonyFlake(Iterator[int]):
    """
    The distributed unique ID generator.
    """

    _now: Callable[[], datetime.datetime]
    mutex: Lock
    _start_time: int
    _machine_id: int
    elapsed_time: int
    sequence: int

    __slots__ = (
        "_now",
        "mutex",
        "_start_time",
        "_machine_id",
        "elapsed_time",
        "sequence",
    )

    def __init__(
        self,
        start_time: Optional[datetime.datetime] = None,
        machine_id: Union[None, int, Callable[[], int]] = None,
        check_machine_id: Any = None,
        now: Callable[[], datetime.datetime] = utc_now,
    ) -> None:
        """
        Create a new instance of `SonyFlake` unique ID generator.

        `start_time` is the time since which the SonyFlake time is
        defined as the elapsed time.

        * If `start_time` is 0, the start time of the SonyFlake is set
        to _"`2014-09-01 00:00:00 +0000 UTC`"_.

        * If `start_time` is ahead of the current time, SonyFlake is
        not created.

        `machine_id` a unique ID of the SonyFlake instance in range [0x0000, 0xFFFF].

        * If `machine_id` is an integer, it is used as is.

        * If `machine_id` is a callable, it is called to get the machine ID.

        * Otherwise, a random machine ID is generated.
        """

        if start_time is None:
            start_time = SONYFLAKE_EPOCH

        if now() < start_time:
            raise ValueError("start_time cannot be in future")

        if machine_id is None:
            _machine_id = random_machine_id()
        elif callable(machine_id):
            _machine_id = machine_id()
        else:
            _machine_id = machine_id

        if not (0 <= _machine_id <= MAX_MACHINE_ID):
            raise ValueError("machine_id must be in range [0x0000, 0xFFFF]")

        if check_machine_id is not None:
            warn("check_machine_id is deprecated", DeprecationWarning)

        self.mutex = Lock()
        self._now = now
        self._machine_id = _machine_id
        self._start_time = self.to_sonyflake_time(start_time)
        self.elapsed_time = self.current_elapsed_time()
        self.sequence = (1 << BIT_LEN_SEQUENCE) - 1

    @staticmethod
    def to_sonyflake_time(given_time: datetime.datetime) -> int:
        """
        Convert a `datetime.datetime` object to SonyFlake's time
        value.
        """
        return int(given_time.timestamp() * 100)

    @property
    def start_time(self) -> int:
        return self._start_time

    @property
    def machine_id(self) -> int:
        return self._machine_id

    def current_time(self) -> int:
        """
        Get current UTC time in the SonyFlake's time value.
        """
        return self.to_sonyflake_time(self._now())

    def current_elapsed_time(self) -> int:
        """
        Get time elapsed since the SonyFlake ID generator was
        initialised.
        """
        return self.current_time() - self.start_time

    def next_id(self) -> int:
        """
        Generates and returns the next unique ID.

        Raises a `TimeoutError` after the `SonyFlake` time overflows.
        """
        mask_sequence = (1 << BIT_LEN_SEQUENCE) - 1
        with self.mutex:
            current_time = self.current_elapsed_time()
            if self.elapsed_time < current_time:
                self.elapsed_time = current_time
                self.sequence = 0
            else:
                self.sequence = (self.sequence + 1) & mask_sequence
                if self.sequence == 0:
                    self.elapsed_time += 1
                    overtime = self.elapsed_time - current_time
                    sleep(self.sleep_time(overtime, self._now()))
            return self.to_id()

    __next__ = next_id

    def to_id(self) -> int:
        if self.elapsed_time >= (1 << BIT_LEN_TIME):
            raise TimeoutError("Over the time limit!")
        time = self.elapsed_time << (BIT_LEN_SEQUENCE + BIT_LEN_MACHINE_ID)
        sequence = self.sequence << BIT_LEN_MACHINE_ID
        return time | sequence | self.machine_id

    @staticmethod
    def sleep_time(duration: int, now: datetime.datetime) -> float:
        """
        Calculate the time remaining until generation of new ID.
        """
        return (duration * 10 - (now.timestamp() * 100) % 1) / 100

    @staticmethod
    def decompose(_id: int) -> Dict[str, int]:
        """
        Decompose returns a set of SonyFlake ID parts.
        """
        mask_sequence = ((1 << BIT_LEN_SEQUENCE) - 1) << BIT_LEN_MACHINE_ID
        mask_machine_id = (1 << BIT_LEN_MACHINE_ID) - 1
        msb = _id >> 63
        time = _id >> (BIT_LEN_SEQUENCE + BIT_LEN_MACHINE_ID)
        sequence = (_id & mask_sequence) >> BIT_LEN_MACHINE_ID
        machine_id = _id & mask_machine_id
        return {
            "id": _id,
            "msb": msb,
            "time": time,
            "sequence": sequence,
            "machine_id": machine_id,
        }
