import unittest
import asyncio
from sr_band import SRBand, SRBandException


class TestSRBand(unittest.TestCase):
    def test_init_high_less_than_target(self):
        with self.assertRaises(SRBandException):
            SRBand(2.0, 1.9, 1.6)

        with self.assertRaises(SRBandException):
            sr = SRBand(2.0, 2.4, 1.6)
            sr.update_high(1.9)

    def test_init_high_equal_to_target(self):
        with self.assertRaises(SRBandException):
            SRBand(2.0, 2.0, 1.6)

            with self.assertRaises(SRBandException):
                sr = SRBand(2.0, 2.4, 1.6)
                sr.update_high(2.0)

    def test_init_low_more_than_target(self):
        with self.assertRaises(SRBandException):
            SRBand(2.0, 2.4, 2.1)

        with self.assertRaises(SRBandException):
            sr = SRBand(2.0, 2.4, 1.6)
            sr.update_low(2.1)

    def test_init_low_equal_to_target(self):
        with self.assertRaises(SRBandException):
            SRBand(2.0, 2.4, 2.0)

        with self.assertRaises(SRBandException):
            sr = SRBand(2.0, 2.4, 1.6)
            sr.update_low(2.0)

    def test_set_reset_high(self):
        async def run_test():
            sr = SRBand(2.0, 2.4, 1.6)
            event_counter = Counter()
            fall_task = asyncio.create_task(
                update_status_func(event_counter, sr.fall_event)
            )

            sr.run(2.6)
            assert_set_fall(sr)
            await asyncio.sleep(0)
            assert_event_count(event_counter, 1)

            sr.run(2.1)
            assert_set_fall(sr)

            await asyncio.sleep(0)
            assert_event_count(event_counter, 2)

            sr.run(2.0)  # should trigger reset
            assert_idle(sr)

            fall_task.cancel()

        asyncio.run(run_test())

    def test_set_reset_low(self):
        async def run_test():
            sr = SRBand(2.0, 2.4, 1.6)
            event_counter = Counter()
            fall_task = asyncio.create_task(
                update_status_func(event_counter, sr.rise_event)
            )

            sr.run(1.5)
            assert_set_rise(sr)
            await asyncio.sleep(0)
            assert_event_count(event_counter, 1)

            sr.run(1.7)
            assert_set_rise(sr)

            await asyncio.sleep(0)
            assert_event_count(event_counter, 2)

            sr.run(2.1)  # should trigger reset
            assert_idle(sr)

            fall_task.cancel()

        asyncio.run(run_test())

    def test_rise_to_fall(self):
        async def run_test():
            sr = SRBand(2.0, 2.4, 1.6)
            fall_event_counter = Counter()
            rise_event_counter = Counter()
            fall_task = asyncio.create_task(
                update_status_func(fall_event_counter, sr.fall_event)
            )
            rise_task = asyncio.create_task(
                update_status_func(rise_event_counter, sr.rise_event)
            )

            sr.run(2.0)
            assert_idle(sr)
            await asyncio.sleep(0)
            assert_event_count(fall_event_counter, 0)
            assert_event_count(rise_event_counter, 0)

            sr.run(1.5)
            assert_set_rise(sr)
            await asyncio.sleep(0)
            assert_event_count(fall_event_counter, 0)
            assert_event_count(rise_event_counter, 1)

            sr.run(2.5)
            assert_set_fall(sr)
            await asyncio.sleep(0)
            assert_event_count(fall_event_counter, 1)
            assert_event_count(rise_event_counter, 1)

            fall_task.cancel()
            rise_task.cancel()

        asyncio.run(run_test())


class Counter:
    n = 0


def assert_idle(sr: SRBand) -> None:
    assert sr.status == SRBand.Status.IDLE, f"Expected IDLE, but got {sr.status}."


def assert_set_fall(sr: SRBand) -> None:
    assert (
        sr.status == SRBand.Status.SET_FALL
    ), f"Expected SET_FALL, but got {sr.status}."


def assert_set_rise(sr: SRBand) -> None:
    assert (
        sr.status == SRBand.Status.SET_RISE
    ), f"Expected SET_RISE, but got {sr.status}."


def assert_event_count(counter: Counter, n: int) -> None:
    assert counter.n == n, f"Expected _events_counter.n == {n}, but got {counter.n}."


async def update_status_func(counter: Counter, some_event: asyncio.Event):
    counter.n = 0
    while True:
        await some_event.wait()
        some_event.clear()
        counter.n += 1


unittest.main()
