import datetime
import ipaddress
from socket import gethostbyname, gethostname
from threading import Lock
from time import sleep
from typing import Callable, Dict, Optional

BIT_LEN_TIME = 39
BIT_LEN_SEQUENCE = 8
BIT_LEN_MACHINE_ID = 63 - (BIT_LEN_TIME + BIT_LEN_SEQUENCE)
SONYFLAKE_EPOCH = datetime.datetime(2014, 9, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)


def lower_16bit_private_ip() -> int:
    """
    Returns the lower 16 bits of the private IP address.
    """
    ip: ipaddress.IPv4Address = ipaddress.ip_address(gethostbyname(gethostname()))
    ip_bytes = ip.packed
    return (ip_bytes[2] << 8) + ip_bytes[3]


class SonyFlake:
    """
    The distributed unique ID generator.
    """

    def __new__(
        cls,
        start_time: Optional[datetime.datetime] = None,
        machine_id: Optional[Callable[[], int]] = None,
        check_machine_id: Optional[Callable[[int], bool]] = None,
    ):
        if start_time and datetime.datetime.utcnow() < start_time:
            return None
        instance = super().__new__(cls)
        if machine_id is not None:
            instance._machine_id = machine_id()
        else:
            instance._machine_id = lower_16bit_private_ip()
        if check_machine_id is not None:
            if not check_machine_id(instance._machine_id):
                return None
        return instance

    def __init__(
        self,
        start_time: Optional[datetime.datetime] = None,
        machine_id: Optional[Callable[[], int]] = None,
        check_machine_id: Optional[Callable[[int], bool]] = None,
    ):
        """
        Create a new instance of `SonyFlake` unique ID generator.

        `start_time` is the time since which the SonyFlake time is
        defined as the elapsed time.

        * If `start_time` is 0, the start time of the SonyFlake is set
        to _"`2014-09-01 00:00:00 +0000 UTC`"_.

        * If `start_time` is ahead of the current time, SonyFlake is
        not created.

        `machine_id` returns the unique ID of the SonyFlake instance.

        * If `machine_id` returns an error, SonyFlake is not created.

        * If `machine_id` is nil, default `machine_id` is used.

        * Default `machine_id` returns the lower 16 bits of the
        private IP address.

        `check_machine_id` validates the uniqueness of the machine ID.

        * If `check_machine_id` returns `False`, SonyFlake is not
        created.

        * If `check_machine_id` is `None`, no validation is done.
        """
        if start_time is None:
            start_time = SONYFLAKE_EPOCH
        self.mutex = Lock()
        self._start_time = self.to_sonyflake_time(start_time)
        self.elapsed_time = self.current_elapsed_time()
        self.sequence = (1 << BIT_LEN_SEQUENCE) - 1
        if not hasattr(self, "_machine_id"):
            self._machine_id = machine_id and machine_id() or lower_16bit_private_ip()

    @staticmethod
    def to_sonyflake_time(given_time: datetime.datetime) -> int:
        """
        Convert a `datetime.datetime` object to SonyFlake's time
        value.
        """
        return int(given_time.timestamp() * 100)

    @property
    def start_time(self):
        return self._start_time

    @property
    def machine_id(self):
        return self._machine_id

    def current_time(self):
        """
        Get current UTC time in the SonyFlake's time value.
        """
        return self.to_sonyflake_time(datetime.datetime.utcnow())

    def current_elapsed_time(self):
        """
        Get time elapsed since the SonyFlake ID generator was
        initialised.
        """
        return self.current_time() - self.start_time

    def next_id(self):
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
                    sleep(self.sleep_time(overtime))
            return self.to_id()

    def to_id(self) -> int:
        if self.elapsed_time >= (1 << BIT_LEN_TIME):
            raise TimeoutError("Over the time limit!")
        time = self.elapsed_time << (BIT_LEN_SEQUENCE + BIT_LEN_MACHINE_ID)
        sequence = self.sequence << BIT_LEN_MACHINE_ID
        return time | sequence | self.machine_id

    @staticmethod
    def sleep_time(duration: int) -> float:
        """
        Calculate the time remaining until generation of new ID.
        """
        return (
            duration * 10 - (datetime.datetime.utcnow().timestamp() * 100) % 1
        ) / 100

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
