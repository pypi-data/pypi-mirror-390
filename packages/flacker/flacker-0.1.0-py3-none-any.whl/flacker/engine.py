from concurrent.futures import ThreadPoolExecutor
import copy
from decimal import Decimal
import math
from time import sleep, time

from .models import (
    EngineFixture,
    EngineTrack,
    Flacker,
    FlackerApiInterface,
    Interpolation,
    KeyframeValue,
)

import logging
logger = logging.getLogger(__name__)


class Engine:
    """Render a lightshow."""

    def __init__(self, flacker: Flacker, apis: dict[str, FlackerApiInterface]) -> None:
        self.apis = apis
        self.flacker = flacker
        self.tracks: list[EngineTrack] = []
        self.fixtures: dict[str, EngineFixture] = {}
        self._executor = ThreadPoolExecutor(max_workers=1)

        for t in self._executor._threads:
            t.daemon = True

    def load_sequence(self, sequence_id: str):
        """Loads a specific sequence and resets the render paremeters."""
        sequence = next(
            filter(lambda s: s.id == sequence_id, self.flacker.sequences), None
        )
        if sequence is None:
            raise ValueError(f"Sequence with id [{sequence_id}] not found.")
        self.load_tracks([t.id for t in sequence.tracks])

    def load_tracks(self, track_ids: list[str]):
        """Loads specific tracks and resets the render paremeters."""
        self.render_time: Decimal = Decimal(0)
        self.is_running: bool = True
        self.tracks = [
            EngineTrack(t)
            for s in self.flacker.sequences
            for t in s.tracks
            if t.id in track_ids
        ]

        # Create and validate fixtures
        self.fixtures = {
            f.id: EngineFixture(f) for s in self.flacker.spaces for f in s.fixtures
        }
        for id, f in self.fixtures.items():
            if f.fixture.api not in self.apis.keys():
                logger.warning(
                    f"Fixture API unknown [{f.fixture.api}]. Fixture will be removed. Fixture ID [{f.fixture.id}]. Known APIs [{', '.join([a for a in self.apis.keys()])}]."
                )
                del self.fixtures[id]
        logger.info("Finished loading tracks.")

    def play(
        self,
        step_size: Decimal = Decimal(0.05),
        *,
        start: Decimal = Decimal(0),
        end: Decimal | None = None,
        wait_for_propagation: bool = True,
    ):
        """Starts playing back the loaded tracks with the given step size in seconds. If no end given, plays until all tracks are finished. If wait_for_propagation is True, play method waits for propagation threads to finish before returning."""
        assert start >= 0, "Start cannot be negative."
        assert end is None or end > start, "End must be after start."

        last_step = time()
        while self.is_running and (end is None or self.render_time < end):
            # Make sure to jump to start time
            step = step_size if self.render_time >= start else start

            self.step(step)
            self.propagate()
            now = time()
            sleep(max(0, float(step_size) - (now - last_step)))
            last_step = now

        if wait_for_propagation:
            logger.info("Waiting for propagation to finish...")
            self._executor.shutdown()

    def step(self, step_size: Decimal):
        """Calculate light values for next step in time. Step size in seconds."""
        if not self.is_running:
            raise BaseException("Cannot render next step, already finished all tracks.")

        assert step_size >= 0, "Step size must be non-negative."

        self.render_time += step_size
        still_running = False  # Keep track if there are still running tracks

        # Reset changed flags
        for f in self.fixtures.values():
            f.changed = False

        # Render all tracks
        for t in self.tracks:
            if not t.is_running:
                continue
            still_running = True

            # Move track forward
            t.step(step_size)
            if t.current is None:
                continue  # Track is not ready yet

            # Interpolate and update value
            interpolated_value = self._get_current_value(t)

            # Update values of relevant fixtures
            for f in self.fixtures.values():
                if f.fixture.id in t.track.fixture_ids:
                    f.set(t.track.parameter, interpolated_value)

        # Update running state
        self.is_running = still_running
        if not self.is_running:
            logger.info("All tracks finished rendering.")

    def propagate(self):
        """Forward new fixture states to APIs."""
        for api_id, api in self.apis.items():
            fixtures = [
                copy.deepcopy(f)
                for f in self.fixtures.values()
                if f.fixture.api == api_id
            ]
            self._executor.submit(
                api.update_fixture, fixtures=fixtures, time=self.render_time
            )

    def _get_current_value(self, track: EngineTrack) -> KeyframeValue:
        """Interpolate between current keyframes of track and return the interpolated value."""
        current = track.current
        if current is None:
            raise BaseException(
                f"Track has no current keyframe. Cannot interpolate values."
            )

        next = track.next
        if next is None:
            return current.frame.value

        t = current.delta.copy_abs() / (
            current.delta.copy_abs() + next.delta.copy_abs()
        )

        return self._interpolate_value(
            current.frame.value, next.frame.value, t, current.frame.interpolation
        )

    def _interpolate_value(
        self,
        start: KeyframeValue,
        end: KeyframeValue,
        t: Decimal,
        interpolation: Interpolation,
    ) -> KeyframeValue:
        """CHATGPT. Interpolate between two numeric values with given interpolation type.
        t is normalized between 0.0 (start) and 1.0 (end)."""

        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            logger.warning(
                f"Interpolation [{interpolation}] only supported for int/float. "
                f"Got {type(start)} → {start}, {type(end)} → {end}. Falling back to STEP."
            )
            return start  # default STEP_PRE behavior

        # Clamp t for safety
        progress = max(0, min(1, float(t)))

        match interpolation:
            case Interpolation.STEP_PRE:
                return start
            case Interpolation.STEP_POST:
                return end
            case Interpolation.LINEAR:
                f = progress
            case Interpolation.EASE_IN:
                f = progress**2
            case Interpolation.EASE_OUT:
                f = 1 - (1 - progress) * (1 - progress)
            case Interpolation.EASE_IN_OUT:
                f = (
                    2 * progress * progress
                    if progress < 0.5
                    else 1 - pow(-2 * progress + 2, 2) / 2
                )
            case Interpolation.EXPONENTIAL:
                f = pow(2, 10 * (progress - 1)) if progress > 0 else 0
            case Interpolation.LOGARITHMIC:
                f = math.log10(9 * progress + 1)  # maps 0→0, 1→1 smoothly
            case Interpolation.SINE:
                f = 0.5 - 0.5 * math.cos(math.pi * progress)
            case Interpolation.SMOOTHSTEP:
                f = progress * progress * (3 - 2 * progress)
            case Interpolation.BOUNCE:
                f = self._bounce_out(float(progress))
            case Interpolation.ELASTIC:
                f = self._elastic_out(progress)
            case _:
                logger.warning(
                    f"Unhandled interpolation type [{interpolation}]. Using STEP."
                )
                return start

        return start + f * (end - start)

    def _bounce_out(self, t: float) -> float:
        """CHATGPT. Bounce easing function (out)."""
        n1, d1 = 7.5625, 2.75
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375

    def _elastic_out(self, t: float) -> float:
        """CHATGPT. Elastic easing function (out)."""
        c4 = (2 * math.pi) / 3
        if t == 0:
            return 0
        if t == 1:
            return 1
        return pow(2, -10 * t) * math.sin((float(t) * 10 - 0.75) * c4) + 1
