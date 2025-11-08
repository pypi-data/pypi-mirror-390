from copy import deepcopy
from dataclasses import dataclass, field
from decimal import Decimal
import math
from .models import (
    Fixture,
    Interpolation,
    Keyframe,
    KeyframeValue,
    Parameter,
    Sequence,
    SpaceVector,
)


@dataclass
class Multitrack:
    """Data object to store list of keyframes for multiple fixtures."""

    keyframes_per_fixture: dict[str, list[Keyframe]
                                ] = field(default_factory=dict)
    """Datastructure to store list of keyframes per fixture."""

    def has_track_for(self, fixture_id: str) -> bool:
        return fixture_id in self.keyframes_per_fixture

    def get_keyframes(self, fixture_id: str) -> list[Keyframe]:
        """Get all keyframes for a specific fixture."""
        if not self.has_track_for(fixture_id):
            raise KeyError(f"Fixture {fixture_id} not found.")
        return self.keyframes_per_fixture[fixture_id]

    def copy(self) -> "Multitrack":
        """Creates a deep copy."""
        tracks = {}
        for f_id, keyframes in self.keyframes_per_fixture.items():
            tracks[f_id] = copy(keyframes)
        return Multitrack(tracks)

    def offset(self, delay: Decimal, *, prefix: Keyframe | None = None) -> "Multitrack":
        """Offset every track.

        In-Place, returns self.
        """
        for f_id, keyframes in self.keyframes_per_fixture.items():
            self.keyframes_per_fixture[f_id] = offset(
                keyframes, offset=delay, prefix=prefix
            )
        return self

    def stretch(
        self, *, target_duration: Decimal | None = None, factor: Decimal | None = None
    ) -> "Multitrack":
        """Stretch or compress the duration of all tracks.

        In-Place, returns self.
        """
        for f_id, keyframes in self.keyframes_per_fixture.items():
            self.keyframes_per_fixture[f_id] = stretch(
                keyframes, factor=factor, target_duration=target_duration
            )
        return self

    def repeat(
        self,
        *,
        min_duration: Decimal | None = None,
        count: int | None = None,
        delay: Decimal = Decimal(0),
    ) -> "Multitrack":
        """Repeat the sequence of keyframes.

        In-Place, returns self.
        """
        multi_duration = self.duration
        for f_id, keyframes in self.keyframes_per_fixture.items():
            self.keyframes_per_fixture[f_id] = repeat(
                keyframes,
                min_duration=min_duration,
                count=count,
                delay=delay + (multi_duration - keyframes[-1].time),
            )
        return self

    def overlay(
        self, foreground: "Multitrack", opaque_foreground: bool = True
    ) -> "Multitrack":
        """Overlay the foreground multitrack on top of the background multitrack.

        In-Place, returns self.
        """
        for f_id, fg_keyframes in foreground.keyframes_per_fixture.items():
            if self.has_track_for(f_id):
                self.keyframes_per_fixture[f_id] = overlay(
                    self.keyframes_per_fixture[f_id],
                    fg_keyframes,
                    opaque_foreground=opaque_foreground,
                )
            else:
                self.keyframes_per_fixture[f_id] = fg_keyframes
        return self

    def invert(self) -> "Multitrack":
        """Invert keyframe value on all tracks.

        In-Place, returns self.
        """
        for f_id, keyframes in self.keyframes_per_fixture.items():
            self.keyframes_per_fixture[f_id] = invert(keyframes)
        return self

    def set(
        self, keyframe: Keyframe, *, fixture_ids: list[str] | None = None
    ) -> "Multitrack":
        """Adds the given keyframe to all referenced tracks. Ensure tracks exist.

        In-Place, returns self.
        """
        if fixture_ids is None:
            fixture_ids = list(self.keyframes_per_fixture.keys())
        for f_id in fixture_ids:
            if self.has_track_for(f_id):
                self.keyframes_per_fixture[f_id] = overlay(
                    self.keyframes_per_fixture[f_id], [
                        keyframe], opaque_foreground=True
                )
            else:
                self.keyframes_per_fixture[f_id] = [keyframe]
        return self

    @property
    def duration(self) -> Decimal:
        """Get duration of longest track. Timestamp of latest keyframe."""
        return max(kfs[-1].time for kfs in self.keyframes_per_fixture.values())

    def add_to_sequence(self, sequence: Sequence, parameter: Parameter) -> Sequence:
        """Adds tracks to sequence. If track exists, overlays new values."""
        for f_id, keyframes in self.keyframes_per_fixture.items():
            t = sequence.ensure_track(f_id, parameter)
            t.keyframes = overlay(t.keyframes, keyframes,
                                  opaque_foreground=True)
        return sequence


@dataclass
class LayeredKeyframe:
    """Storing keyframes with layers."""

    layer: int
    """Higher layers, in front of lower layers."""

    keyframe: Keyframe
    """Reference keyframe."""


def min_value(keyframes: list[Keyframe]) -> float | int:
    """Return the minimum int|float value in the given keyframes.

    Args:
        keyframes (list[Keyframe]): Keyframes, some containing int|float values.

    Returns:
        float | int: Minimum value found in keyframes.
    """
    values = [k.value for k in keyframes if isinstance(k.value, (int, float))]
    assert len(values) > 0
    return min(values)


def max_value(keyframes: list[Keyframe]) -> float | int:
    """Return the maximum int|float value in the given keyframes.

    Args:
        keyframes (list[Keyframe]): Keyframes, some containing int|float values.

    Returns:
        float | int: Maximum value found in keyframes.
    """
    values = [k.value for k in keyframes if isinstance(k.value, (int, float))]
    assert len(values) > 0
    return max(values)


def copy(keyframes: list[Keyframe]) -> list[Keyframe]:
    """Creates a deep copy of a list of keyframes."""
    return deepcopy(
        keyframes
        # [Keyframe(Decimal(str(k.time)), k.value, k.interpolation) for k in keyframes]
    )


def offset(
    keyframes: list[Keyframe], offset: Decimal, *, prefix: Keyframe | None = None
) -> list[Keyframe]:
    """Add an offset to the time property of each Keyframe object in a list.

    Args:
        keyframes (list[Keyframe]): A list containing Keyframe objects.
        offset (Decimal): The amount by which to increase each keyframe's time in seconds.
        prefix (Keyframe | None): Keyframe to insert before the offset keyframes.

    Returns:
        list[Keyframe]: The modified list of keyframes where each keyframe's time has been increased by the specified offset.
    """
    keyframes = copy(keyframes)
    for k in keyframes:
        k.time += offset

    if prefix:
        return [prefix, *keyframes]
    else:
        return keyframes


def get_duration(keyframes: list[Keyframe]) -> Decimal:
    """Calculate the duration between the first and last keyframe in a list. Not containing the delay of the fist keyframe.

    Args:
        keyframes (list[Keyframe]): A list containing Keyframe objects.

    Returns:
        Decimal: The difference between the time of the last keyframe and the first keyframe.
    """
    assert len(keyframes) > 0
    return keyframes[-1].time - keyframes[0].time


def first(
    keyframes: list[Keyframe], value: KeyframeValue, *, after: Decimal | None = None
) -> Keyframe | None:
    """Returns first keyframe to match target value or None, if no match is found.

    Args:
        after (Decimal | None): If provided, only keyframes after the timestamp are considered. Defaults to None.
    """
    for k in keyframes:
        if after and k.time < after:
            continue
        if k.value == value:
            return k
    return None


def overlay(
    background: list[Keyframe],
    foreground: list[Keyframe],
    opaque_foreground: bool = True,
) -> list[Keyframe]:
    """Merges two sequences of keyframes, where foreground has a higher priority than the background.

    Args:
        background (list[Keyframe]): Low priority sequence of Keyframes.
        foreground (list[Keyframe]): High priority sequence of Keyframes.
        opaque_foreground (bool, optional): If true, background keyframes are hidden between start and end of foreground keyframes. Otherwise they are just overlayed. Defaults to True.

    Returns:
        list[Keyframe]: Merged list of keyframes.
    """
    # Save keyframes with their layer and sort them all
    bg = 0
    fg = 1
    all = [
        *[LayeredKeyframe(fg, k) for k in foreground],
        *[LayeredKeyframe(bg, k) for k in background],
    ]  # Foreground must come first to sort matching timestamps correctly
    all = sorted(all, key=lambda lk: lk.keyframe.time)

    merged = []
    hidden = False
    for k in all:
        # Handle hidden-state and opaqueness
        if k.layer == fg:
            hidden = opaque_foreground

            # Deactivate hiding on last, foreground keyframe
            if k.keyframe.time == foreground[-1].time:
                hidden = False

        # Skip background keyframes if hidden
        if hidden and k.layer == bg:
            continue

        merged.append(k.keyframe)

    return merged


def repeat(
    keyframes: list[Keyframe],
    *,
    min_duration: Decimal | None = None,
    count: int | None = None,
    delay: Decimal = Decimal(0),
) -> list[Keyframe]:
    """Repeat a set of keyframes, based on different possible restraints.

    Args:
        keyframes (list[Keyframe]): Keyframes to repeat.
        delay (Decimal): Next repetition of keyframes is placed with a certain delay after the previous. 0 means first keyframe replaces last. Defaults to 0 seconds.
        min_duration (Decimal | None, optional): Total duration to target with repeated sequence. Is repeated whole number of times until duration is covered. Given in seconds. Defaults to None.
        count (int | None, optional): Is repeated count-number of times. Defaults to None.

    Returns:
        list[Keyframe]: Repeated sequence of keyframes.
    """
    assert len(keyframes) > 0

    duration = get_duration(keyframes)
    assert delay >= 0 or duration > abs(delay)

    # Prepare different restraints
    if min_duration:
        count = math.ceil((min_duration - duration) / (delay + duration))
    else:
        assert count is not None and count > 0

    snippet = copy(keyframes)
    repeated = copy(keyframes)
    for _ in range(count - 1):
        # Offset next sequence and merge with previous
        snippet = offset(snippet, offset=delay + duration)
        repeated = overlay(repeated, copy(snippet), opaque_foreground=True)

    return repeated


def reverse(
    keyframes: list[Keyframe], *, flip_interpolation: bool = True
) -> list[Keyframe]:
    """Reverse a sequence of keyframes. Initial delay is discarded.

    Args:
        keyframes (list[Keyframe]): Sequence of keyframes to reverse.
        flip_interpolation (bool, optional): Moves the interpolation to other keyframes to keep the same interpolation between the same keyframes. Defaults to True.

    Returns:
        list[Keyframe]: Reversed sequence of keyframes.
    """
    assert len(keyframes) > 0
    # Remove intial delay
    sequence = offset(copy(keyframes), -keyframes[0].time)
    duration = sequence[-1].time
    sequence.reverse()

    reversed = []
    for i, (k, interpolation_keyframe) in enumerate(
        zip(sequence, [*sequence[1:], sequence[0]])
    ):
        k.time = duration - k.time

        if flip_interpolation:
            inter = interpolation_keyframe.interpolation
            if i < len(sequence) - 1:
                #! Not really sure if to reverse last interpolation or not
                inter = Interpolation.reverse(inter)
            k.interpolation = inter

    return reversed


def stretch(
    keyframes: list[Keyframe],
    *,
    target_duration: Decimal | None = None,
    factor: Decimal | None = None,
) -> list[Keyframe]:
    """Stretch (or compress) a sequence of keyframes. Ends on last keyframe.

    Args:
        keyframes (list[Keyframe]): Sequence of keyframes to stretch. Must contain at least one keyframe.
        target_duration (Decimal | None, optional): Target duration to reach with stretched sequence. Defaults to None.
        factor (Decimal | None, optional): A factor to stretch the sequence by, <1 meaning compressing. Should be >0. Defaults to None.

    Returns:
        list[Keyframe]: Stretched sequence of keyframes.
    """
    assert len(keyframes) > 0

    if target_duration:
        assert target_duration > 0
        factor = target_duration / keyframes[-1].time
    else:
        assert factor is not None and factor > 0

    for k in keyframes:
        k.time *= factor

    return keyframes


def invert(keyframes: list[Keyframe]) -> list[Keyframe]:
    """Invert int|float keyframe values."""
    assert len(keyframes) > 0

    for k in keyframes:
        if isinstance(k.value, (int, float)):
            k.value = 1 - k.value

    return keyframes


def scale_values(
    keyframes: list[Keyframe],
    *,
    new_min: int | float | None = None,
    new_max: int | float | None = None,
) -> list[Keyframe]:
    """Rescales int|float values of given keyframes to a new min-max value

    Args:
        keyframes (list[Keyframe]): Keyframes to rescale.
        new_min (int | float | None, optional): New min value, or current if None. Defaults to None.
        new_max (int | float | None, optional): New max value, or current if None. Defaults to None.

    Returns:
        list[Keyframe]: Keyframes with scaled values.
    """
    cur_min = min_value(keyframes)
    cur_max = max_value(keyframes)
    if not new_min:
        new_min = cur_min
    if not new_max:
        new_max = cur_max

    scaling = (new_max - new_min) / (cur_max - cur_min)

    for k in keyframes:
        if not isinstance(k.value, (int, float)):
            continue

        k.value = (k.value - cur_min) * scaling + new_min

    return keyframes


def repeat_at_times(snippet: list[Keyframe], timestamps: list[Decimal], *, delay: Decimal = Decimal(0), overlay_previous: bool = False) -> list[Keyframe]:
    """Repeats a given snippet at the provided timestamps.

    Snippets are placed at the timestamp by their 0s mark. They can be offset using the delay parameter.

    Args:
        snippet (list[Keyframe]): Snippet to repeat.
        timestamps (list[Decimal  |  float]): Times at which snippet will be repeated.
        delay (Decimal, optional): Delay to apply to the snippets relative to their timestamps. Delay greater 0 means snippet will be pushed back. Defaults to 0s.
        overlay_previous (bool, optional): By default, later snippes will overlay onto earlier snippets. This can be inverted using this parameter. Defaults to False.

    Returns:
        list[Keyframe]: Repeated snippet.
    """
    result: list[Keyframe] = []
    for t in timestamps:
        offset_snippet = offset(snippet, offset=t + delay)

        if overlay_previous:
            result = overlay(offset_snippet, result)
        else:
            result = overlay(result, offset_snippet)

    return result


def space_bounds(
    fixtures: list[Fixture], *, include_spread: bool = True
) -> tuple[SpaceVector, SpaceVector]:
    """Get bounds of fixture targets with or without spread.

    Returns:
        lower_bounds, upper_bounds (SpaceVector, SpaceVector)
    """
    # Determine bounds
    lower_bounds = SpaceVector()
    upper_bounds = SpaceVector()

    for f in fixtures:
        spread = SpaceVector()
        if include_spread:
            spread = f.spread / 2
        v = f.target
        if v.bf - spread.bf < lower_bounds.bf:
            lower_bounds.bf = v.bf - spread.bf
        if v.bf + spread.bf > upper_bounds.bf:
            upper_bounds.bf = v.bf + spread.bf

        if v.bt - spread.bt < lower_bounds.bt:
            lower_bounds.bt = v.bt - spread.bt
        if v.bt + spread.bt > upper_bounds.bt:
            upper_bounds.bt = v.bt + spread.bt

        if v.lr - spread.lr < lower_bounds.lr:
            lower_bounds.lr = v.lr - spread.lr
        if v.lr + spread.lr > upper_bounds.lr:
            upper_bounds.lr = v.lr + spread.lr

    return lower_bounds, upper_bounds
