from itertools import combinations
import networkx as nx
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Generator
from .operations import Multitrack
from .models import (
    Fixture,
    Interpolation,
    Keyframe,
    KeyframeValue,
    SpaceVector,
)
import numpy as np


def sample_function(
    func: Callable[[float | Decimal], float],
    start_x: float | Decimal,
    step_x: float | Decimal,
    *,
    start_time: Decimal = Decimal(0),
    time_per_step: Decimal | None = None,
    interpolation: Interpolation = Interpolation.LINEAR,
) -> Generator[Keyframe, None, None]:
    """Generates a sequence of keyframes based on the provided mathematical function and parameters.

    Args:
        func (Callable[[float | Decimal], float]): The function to sample values from.
        start_x (float | Decimal): The initial x-value for the function.
        step_x (float | Decimal): The incremental step in the x-value for each keyframe.
        start_time (Decimal, optional): The starting time for the first keyframe. Defaults to 0.
        time_per_step (Decimal | None, optional): If provided, defines the duration of each step in time; otherwise, defaults to step_x.
        interpolation (Interpolation, optional): The method used to interpolate between keyframes. Default is LINEAR.

    Yields:
        Generator[Keyframe]: A generator yielding instances of Keyframe sampled from function.
    """
    time: Decimal = Decimal(start_time)
    x: Decimal = Decimal(start_x)
    if not time_per_step:
        time_per_step = Decimal(step_x)
    while True:
        yield Keyframe(
            time=time,
            value=func(x),
            interpolation=interpolation,
        )
        time += time_per_step
        x += Decimal(step_x)


def peak(
    *,
    start_value: float = 0,
    first_delay: Decimal = Decimal(0.5),
    peak_value: float = 1,
    second_delay: Decimal | None = None,
    end_value: float | None = None,
    interpolation: Interpolation = Interpolation.LINEAR,
) -> list[Keyframe]:
    """Creates a 3-point sequence, focussing on peaks, where the center value is the outlier, but offers a lot of flexibility.

    Args:
        start_value (float, optional): Value for first point. Defaults to 0.
        first_delay (Decimal, optional): Delay between first, and middle/peak point. Defaults to Decimal(0.1).
        peak_value (float, optional): Value of peak point. Defaults to 1.
        second_delay (Decimal | None, optional): Delay between middle/peak and last point. Defaults to None, indicating same as first_delay.
        end_value (float | None, optional): Value for end point. Defaults to None, indicating same as start_value.
        interpolation (Interpolation, optional): Applied to all keyframes. Defaults to linear.

    Returns:
        list[Keyframe]: Generated peak sequence.
    """
    if second_delay is None:
        second_delay = first_delay
    if end_value is None:
        end_value = start_value
    return [
        Keyframe(time=Decimal(0), value=start_value, interpolation=interpolation),
        Keyframe(time=first_delay, value=peak_value, interpolation=interpolation),
        Keyframe(
            time=first_delay + second_delay,
            value=end_value,
            interpolation=interpolation,
        ),
    ]


def linear(fixtures: list[Fixture], start: SpaceVector, end: SpaceVector) -> Multitrack:
    """Simulates an infinite plane following the path from start to end (surface perpendicular to the direction of travel) over the duration of one second, and outputs the keyframe data for each fixture along the way based on intersection with the plane.

    Args:
        fixtures (list[Fixture]): List of Fixture objects that will be affected by the path.
        start (SpaceVector): Start point for movement. Reached at 0.0.
        end (SpaceVector): End point for movement. Reached at 1.0.

    Returns:
        MultitrackKeyframes: A collection of keyframe data for each fixture along the path. Keyframes are 0 by default, and 1 for the time of intersection.
    """
    assert len(fixtures) > 0, "At least one fixture is required."
    assert start != end, "Start and end position of plane must be different."

    def _plane_ellipsoid_contact_times(
        center: np.ndarray,  # [x0, y0, z0]
        radii: np.ndarray,  # [a, b, c]
        plane_normal: np.ndarray,  # [nx, ny, nz]
        plane_point_at_t0: np.ndarray,  # [px, py, pz] at t=0
        plane_velocity: np.ndarray,  # [vx, vy, vz]
    ) -> tuple[float, float]:
        """Written by Mistral.AI
        Calculate the times when a moving plane first contacts and finally leaves an ellipsoid.

        Returns: (t_first, t_last)
        """
        # Normalize the normal vector
        n = np.asarray(plane_normal)
        n = n / np.linalg.norm(n)

        # Compute d0 and vn
        d0 = np.dot(n, plane_point_at_t0 - center)  # Shift by center
        vn = np.dot(n, plane_velocity)

        # Compute R
        a, b, c = radii
        nx, ny, nz = n
        R = np.sqrt((a * nx) ** 2 + (b * ny) ** 2 + (c * nz) ** 2)

        # Solve for t
        t1 = (-d0 - R) / vn
        t2 = (-d0 + R) / vn

        # Ensure t1 <= t2
        if t1 > t2:
            t1, t2 = t2, t1

        return t1, t2

    # Calculate plane parameters
    plane_t0 = np.array([start.lr, start.bf, start.bt])
    plane_t1 = np.array([end.lr, end.bf, end.bt])
    plane_v = plane_t1 - plane_t0
    plane_n = plane_v / np.linalg.norm(plane_v)

    tracks: dict[str, list[Keyframe]] = {}
    for f in fixtures:
        t_start, t_end = _plane_ellipsoid_contact_times(
            np.array([f.target.lr, f.target.bf, f.target.bt]),
            np.array([f.spread.lr, f.spread.bf, f.spread.bt]),
            plane_n,
            plane_t0,
            plane_v,
        )

        points: list[Keyframe] = []

        # Is in bounds?
        if max(t_start, t_end) < 0 or min(t_start, t_end) > 1:
            points.append(Keyframe(Decimal(0), 0, Interpolation.STEP_PRE))
            continue

        # Start
        if t_start > 0:
            points.append(Keyframe(Decimal(0), 0, Interpolation.STEP_PRE))
            points.append(Keyframe(Decimal(t_start), 1, Interpolation.STEP_PRE))
        else:
            points.append(Keyframe(Decimal(0), 1, Interpolation.STEP_PRE))

        # End
        if t_end <= 1:
            points.append(Keyframe(Decimal(t_end), 0, Interpolation.STEP_PRE))

        tracks[f.id] = points

    return Multitrack(tracks)


def sequence(
    order: list[str],
    *,
    value: KeyframeValue = 1,
    delay: Decimal = Decimal(1),
    interpolation: Interpolation = Interpolation.STEP_PRE,
) -> Multitrack:
    """Creates tracks for ids where each track gets triggered in the given order with the given delay."""
    tracks: dict[str, list[Keyframe]] = {}
    for i, f_id in enumerate(order):
        tracks[f_id] = [
            Keyframe(time=i * delay, value=value, interpolation=interpolation)
        ]

    return Multitrack(tracks)


def flicker(
    fixtures: list[Fixture],
    *,
    value: KeyframeValue = 1,
    delay: Decimal = Decimal(1),
    interpolation: Interpolation = Interpolation.STEP_PRE,
) -> Multitrack:
    """Creates tracks for fixtures to trigger them in a chaotic pattern, based on the total longest distance between consecutively triggered fixture targets."""
    G = nx.Graph()

    # Add edges with 1/distance as weights for inverted TSP
    for f_a, f_b in combinations(fixtures, 2):
        distance = f_a.target.distance(f_b.target)
        weight = 1 / (distance + 1e-9)  # Avoid division by zero
        G.add_edge(f_a.id, f_b.id, weight=weight)

    # Solve TSP (approximation)
    path = nx.algorithms.approximation.traveling_salesman_problem(G, cycle=True)
    return sequence(order=path, value=value, delay=delay, interpolation=interpolation)
