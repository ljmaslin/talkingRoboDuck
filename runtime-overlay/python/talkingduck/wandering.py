"""Portable reactive wandering. Sensor adapters supply ranges, never a world map.

This is obstacle avoidance, not SLAM, cliff detection or person following.
The shipping kit has no range sensor; no adapter is selected by default.
"""
import json
import math
import time
from urllib.request import urlopen


class HttpRanges:
    """Opt-in range-service adapter. Simulation sets its URL in Compose only."""
    def __init__(self, url):
        self.url = url
        self.sequence = None
        self.changed = time.monotonic()

    def read(self):
        with urlopen(self.url, timeout=.25) as response:
            frame = json.loads(response.read(8192))
        now = time.monotonic()
        if frame.get('sequence') != self.sequence:
            self.sequence, self.changed = frame.get('sequence'), now
        if self.sequence is None or now-self.changed > .3:
            raise ValueError('Depth sensor has stopped updating.')
        values = frame.get('distances_m')
        age = frame.get('age_ms')
        if (not isinstance(age, (float, int)) or not math.isfinite(age) or not 0 <= age < 250
                or not isinstance(values, list) or len(values) != 8
                or any(type(v) not in (float, int) or not math.isfinite(v) or not .02 <= v <= 4 for v in values)):
            raise ValueError('Depth readings are stale or invalid.')
        return frame


class WanderPlan:
    """Eight left-to-right horizontal ranges, in metres; positive yaw turns left."""
    def __init__(self):
        self.turn_until = 0
        self.turn_started = 0
        self.direction = 1
        self.turns = 0
        self.phase = 'walking'

    def step(self, ranges, now):
        nearest = min(ranges)
        if self.phase == 'turning':
            if now-self.turn_started > 12:
                raise ValueError('No clear route found; wandering stopped.')
            if now >= self.turn_until and nearest > .55:
                self.phase = 'walking'
            else:
                return [0, 0, .65*self.direction]
        if nearest < .38:
            self.phase = 'turning'
            self.turn_started, self.turn_until = now, now+.8
            self.direction = 1 if sum(ranges[:4]) >= sum(ranges[4:]) else -1
            self.turns += 1
            return [0, 0, .65*self.direction]
        # Gentle curvature explores rather than tracing exactly the same line.
        yaw = .12*math.sin(now*.45)
        # Very small speed requests settle into standing with the supplied
        # walking model. These commands actually produce stepping in this model.
        return [.25 if nearest > .55 else .20, 0, yaw]
