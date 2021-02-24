import threading
from datetime import datetime, timedelta
from random import randint
from time import sleep
from unittest import TestCase

from sonyflake.sonyflake import BIT_LEN_SEQUENCE, SonyFlake, lower_16bit_private_ip


class SonyFlakeTestCase(TestCase):
    def setUp(self):
        start_time = datetime.utcnow()
        self.sf = SonyFlake(start_time)
        self.start_time = SonyFlake.to_sonyflake_time(start_time)
        self.machine_id = lower_16bit_private_ip()

    @staticmethod
    def _current_time():
        return SonyFlake.to_sonyflake_time(datetime.utcnow())

    @staticmethod
    def _sleep(duration):
        return sleep(duration / 100)

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
        future_start_time = datetime.utcnow() + timedelta(minutes=1)
        sonyflake = SonyFlake(start_time=future_start_time)
        self.assertIsNone(sonyflake, "SonyFlake starting in the future")

    def test_sonyflake_invalid_machine_id(self):
        def check_machine_id(_: int) -> bool:
            return False

        sonyflake = SonyFlake(check_machine_id=check_machine_id)
        self.assertIsNone(sonyflake, "Machine ID check failed")

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
