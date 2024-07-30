import asyncio


class SRBandException(Exception):
    ...


class SRBand:
    class Status:
        IDLE = "IDLE"
        SET_FALL = "SET_FALL"
        SET_RISE = "SET_RISE"

    def __init__(self, target: float, high: float, low: float):
        """
        Initialize an SRBand object with specified target, high, and low thresholds.

        Args:
            target (float): The target value.
            high (float): The high threshold.
            low (float): The low threshold.

        Raises:
            SRBandException: If the provided arguments do not satisfy low < target < high.
        """
        if not low < target < high:
            raise SRBandException("Args must abide by rule of: low < target < high.")

        self._target = target
        self._high = high
        self._low = low

        self.status: str = SRBand.Status.IDLE
        self.value = None

        self.fall_event: asyncio.Event = asyncio.Event()
        self.rise_event: asyncio.Event = asyncio.Event()

    def run(self, new_value: float, trigger_events: bool = True) -> None:
        """
        Run the current value and trigger events if thresholds are crossed.

        Args:
            new_value (float): The new value to update.
        """
        self.value = new_value

        if self.value > self._high:
            self.status = SRBand.Status.SET_FALL
        elif self.value < self._low:
            self.status = SRBand.Status.SET_RISE

        if self.status == SRBand.Status.SET_FALL and self.value <= self._target:
            self.status = SRBand.Status.IDLE
        elif self.status == SRBand.Status.SET_RISE and self.value >= self._target:
            self.status = SRBand.Status.IDLE

        if trigger_events:
            if self.status == SRBand.Status.SET_FALL:
                self.fall_event.set()
            elif self.status == SRBand.Status.SET_RISE:
                self.rise_event.set()

    def update_high(self, new_high: float) -> None:
        if not self._low < self._target < new_high:
            raise SRBandException("Args must abide by rule of: low < target < high.")
        self._high = new_high
        if self.value:
            self.run(self.value, trigger_events=False)

    def update_low(self, new_low: float) -> None:
        if not new_low < self._target < self._high:
            raise SRBandException("Args must abide by rule of: low < target < high.")
        self._low = new_low
        if self.value:
            self.run(self.value, trigger_events=False)

    def update_target(self, new_target: float) -> None:
        if not self._low < new_target < self._high:
            raise SRBandException("Args must abide by rule of: low < target < high.")
        self._target = new_target
        if self.value:
            self.run(self.value, trigger_events=False)

