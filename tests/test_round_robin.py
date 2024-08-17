from sonyflake.round_robin import RoundRobin
from sonyflake.sonyflake import BIT_LEN_MACHINE_ID, SonyFlake


def test_round_robin() -> None:
    rr = RoundRobin(
        [
            SonyFlake(machine_id=0x0000),
            SonyFlake(machine_id=0x7F7F),
            SonyFlake(machine_id=0xFFFF),
        ]
    )

    assert [next(rr) & ((1 << BIT_LEN_MACHINE_ID) - 1) for _ in range(6)] == [
        0x0000,
        0x7F7F,
        0xFFFF,
    ] * 2
