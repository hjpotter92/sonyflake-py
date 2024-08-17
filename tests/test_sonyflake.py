import threading
from datetime import datetime, timedelta, timezone
from random import randint
from time import sleep
from unittest import TestCase

from pytest import mark, raises

from sonyflake.sonyflake import (
    BIT_LEN_SEQUENCE,
    SONYFLAKE_EPOCH,
    SonyFlake,
    lower_16bit_private_ip,
    random_machine_id,
    random_machine_ids,
)


class SonyFlakeTestCase(TestCase):
    def setUp(self):
        start_time = datetime.now(timezone.utc)
        self.machine_id = 0x7F7F
        self.sf = SonyFlake(start_time, machine_id=self.machine_id)
        self.start_time = SonyFlake.to_sonyflake_time(start_time)

    @staticmethod
    def _current_time():
        return SonyFlake.to_sonyflake_time(datetime.now(timezone.utc))

    @staticmethod
    def _sleep(duration):
        return sleep(duration / 100)

    def test_sonyflake_epoch(self):
        sf = SonyFlake(
            start_time=SONYFLAKE_EPOCH,
            machine_id=self.machine_id,
        )
        self.assertEqual(sf.start_time, 140952960000)
        next_id = sf.next_id()
        parts = SonyFlake.decompose(next_id)
        self.assertEqual(parts["msb"], 0)
        self.assertEqual(parts["machine_id"], self.machine_id)
        self.assertEqual(parts["sequence"], 0)

    def test_sonyflake_custom_machine_id(self):
        machine_id = randint(1, 255**2)

        sf = SonyFlake(machine_id=machine_id)
        next_id = sf.next_id()
        parts = SonyFlake.decompose(next_id)
        self.assertEqual(parts["machine_id"], machine_id)

    def test_sonyflake_once(self):
        sleep_time = randint(1, 50)
        self._sleep(sleep_time)
        next_id = self.sf.next_id()
        parts = SonyFlake.decompose(next_id)
        self.assertEqual(parts["msb"], 0)
        self.assertTrue(sleep_time <= parts["time"] <= sleep_time + 1)
        self.assertEqual(parts["sequence"], 0)
        self.assertEqual(parts["machine_id"], self.machine_id)

    def test_sonyflake_future(self):
        future_start_time = datetime.now(timezone.utc) + timedelta(minutes=1)

        with raises(ValueError, match=r"start_time cannot be in future"):
            SonyFlake(start_time=future_start_time)

    def test_sonyflake_invalid_machine_id(self):
        for machine_id in [-1, 0xFFFF + 1]:
            with raises(
                ValueError, match=r"machine_id must be in range \[0x0000, 0xFFFF\]"
            ):
                SonyFlake(machine_id=machine_id)

    def test_sonyflake_for_10sec(self):
        last_id = 0
        current = initial = self._current_time()
        max_sequence = 0
        while (current - initial) < 1000:
            next_id = self.sf.next_id()
            parts = SonyFlake.decompose(next_id)
            self.assertLess(last_id, next_id, "Duplicated id")
            current = self._current_time()
            last_id = next_id
            self.assertEqual(parts["msb"], 0)
            self.assertEqual(parts["machine_id"], self.machine_id)
            overtime = self.start_time + (parts["time"] - current)
            self.assertLessEqual(overtime, 0, "Unexpected overtime.")
            max_sequence = max(max_sequence, parts["sequence"])
        self.assertEqual(
            max_sequence, (1 << BIT_LEN_SEQUENCE) - 1, "Unexpected max sequence"
        )

    def test_sonyflake_in_parallel(self):
        threads = []
        results = []
        for _ in range(10000):
            thread = threading.Thread(target=lambda: results.append(self.sf.next_id()))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        result_set = set(results)
        self.assertEqual(len(results), len(result_set))
        self.assertCountEqual(results, result_set)


def test_random_machine_id() -> None:
    assert random_machine_id()


@mark.parametrize("n", [1, 1024, 65535])
def test_random_machine_ids(n: int) -> None:
    machine_ids = random_machine_ids(n)
    assert len(set(machine_ids)) == n
    assert sorted(machine_ids) == machine_ids


@mark.parametrize("n", [0, 65536])
def test_random_machine_ids_edges(n: int) -> None:
    with raises(ValueError, match=r"n must be in range \(0, 65535\]"):
        random_machine_ids(n)


def test_lower_16bit_private_ip() -> None:
    assert lower_16bit_private_ip()
