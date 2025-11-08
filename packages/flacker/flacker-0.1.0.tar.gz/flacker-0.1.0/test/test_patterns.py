import logging
from decimal import Decimal
from time import sleep, time

from flacker.apis import HueApi, HueEntertainmentApi, MultiApi, PlotApi
from flacker.engine import Engine
from flacker.models import (
    Capabilities,
    Flacker,
    FlackerApiInterface,
    Interpolation,
    Keyframe,
    Parameter,
    Sequence,
    Space,
    SpaceVector,
    Track,
)
from flacker.operations import first, invert, offset, space_bounds, stretch
from flacker.patterns import flicker, linear, peak, sequence

ip = "192.168.178.85"
logging.getLogger().setLevel(logging.INFO)


space = Space.load("living-room_space.json")
# space.fixtures = [f for f in space.fixtures if f.capabilities == Capabilities.COLOR]

# ==== Flicker ====
flicker_seq = Sequence("flicker", "flicker")

delay = Decimal(0.05)
on_seq_flicker = flicker(space.fixtures, delay=delay)
off_seq_flicker = on_seq_flicker.copy().invert().offset(delay)
on_off_flicker = (
    on_seq_flicker.overlay(off_seq_flicker)
    .set(Keyframe(Decimal(0), 0))
    .repeat(count=5, delay=delay)
)
flicker_seq = on_off_flicker.add_to_sequence(flicker_seq, Parameter.BRIGHTNESS)


# ==== Sequence ====
sequence_seq = Sequence("sequence", "sequence")

delay = Decimal(0.1)
order = [f.id for f in sorted(space.fixtures, key=lambda f: f.target.lr)]
on_seq = sequence(order, delay=delay)
off_seq = on_seq.copy().invert().offset(on_seq.duration + delay)
on_off = (
    on_seq.overlay(off_seq).set(Keyframe(Decimal(0), 0)).repeat(count=5, delay=delay)
)
sequence_seq = on_off.add_to_sequence(sequence_seq, Parameter.BRIGHTNESS)


# ==== Linear ====
linear_seq = Sequence("linear", "linear")
lower_b, upper_b = space_bounds(space.fixtures)
lin = linear(
    space.fixtures, SpaceVector(lower_b.lr, 0, 0), SpaceVector(upper_b.lr, 0, 0)
)
for f in space.fixtures:
    kf = lin.get_keyframes(f.id)

    # Transform peak to smooth curve
    k_start = first(kf, value=1)
    if k_start is None:
        continue
    k_end = first(kf, value=0, after=k_start.time)

    duration = 1 - k_start.time
    if k_end:
        duration = k_end.time - k_start.time
    center = k_start.time + duration / 2
    duration = Decimal(min(0.3, max(0.3, duration)))
    start_time = center - duration / 2

    kf = peak(interpolation=Interpolation.EASE_IN_OUT)
    kf = stretch(kf, target_duration=duration)
    kf = offset(
        kf,
        start_time,
        prefix=Keyframe(Decimal(0), value=0) if start_time > 0 else None,
    )

    kf = stretch(kf, factor=Decimal(1))

    linear_seq.tracks.append(Track(f.id, "Track", Parameter.BRIGHTNESS, [f.id], kf))


flacker = Flacker([space], [linear_seq, sequence_seq, flicker_seq])
flacker.save("pattern_flacker.json", overwrite=True)


plot = PlotApi()
apis: dict[str, FlackerApiInterface] = {
    "hue": MultiApi([HueApi(ip)])
}
engine = Engine(flacker, apis)


def arg_parse():
    import argparse

    parser = argparse.ArgumentParser(description="Load a sequence from the engine.")
    parser.add_argument(
        "-s",
        "--sequence_name",
        type=str,
        help="The name of the sequence to load",
        default="sequence",
    )

    return parser.parse_args()


args = arg_parse()
engine.load_sequence(args.sequence_name)
engine.play()

plot.save_plot("plot.png", order_ids=order)
print("Done.")
