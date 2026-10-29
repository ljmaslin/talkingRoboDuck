import sys
import io
import json
from pathlib import Path
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'xgo-runtime/python'))
from talkingduck.actions import Actions
from talkingduck.wandering import WanderPlan, HttpRanges
from test_commands import Controller


class Ranges:
    def __init__(self): self.failed = False
    def read(self):
        if self.failed: raise ValueError('Sensor disconnected')
        return {'distances_m': [1.0]*8, 'source': 'test', 'simulated': True}


class Wandering(unittest.TestCase):
    def test_range_service_rejects_stale_invalid_and_replayed_frames(self):
        def response(frame): return io.BytesIO(json.dumps(frame).encode())
        valid = {'sequence': 1, 'age_ms': 5, 'distances_m': [1.0]*8}
        for field, value in [('age_ms', 500), ('distances_m', [float('nan')]*8), ('distances_m', [0]*8)]:
            frame = {**valid, field: value}
            with patch('talkingduck.wandering.urlopen', return_value=response(frame)):
                with self.assertRaises(ValueError): HttpRanges('http://sensor/ranges').read()
        sensor = HttpRanges('http://sensor/ranges')
        with patch('talkingduck.wandering.time.monotonic', side_effect=[10, 10.4]):
            with patch('talkingduck.wandering.urlopen', side_effect=lambda *a, **k: response(valid)):
                sensor.read()
                with self.assertRaises(ValueError): sensor.read()

    def test_physical_default_refuses_wandering_without_sensor(self):
        c = Controller()
        self.assertFalse(Actions(c).execute('wander')['accepted'])
        self.assertEqual(c.mode, 'shadow')
        self.assertFalse(c.calls)

    def test_obstacle_stops_forward_motion_and_turns_toward_clearer_side(self):
        plan = WanderPlan()
        self.assertGreater(plan.step([1]*8, 0)[0], 0)
        command = plan.step([1, 1, .8, .3, .2, .2, .2, .2], .1)
        self.assertEqual(command[0], 0)
        self.assertGreater(command[2], 0)
        self.assertEqual(plan.step([1]*8, .2)[0], 0)  # minimum turn duration
        self.assertGreater(plan.step([1]*8, 1)[0], 0)

    def test_trapped_robot_eventually_stops(self):
        plan = WanderPlan(); plan.step([.2]*8, 0)
        with self.assertRaises(ValueError): plan.step([.2]*8, 13)

    def test_disconnected_sensor_cancels_continuous_travel(self):
        c, sensor = Controller(), Ranges()
        actions = Actions(c, sensor)
        self.assertTrue(actions.execute('wander')['accepted'])
        time.sleep(.15)
        self.assertTrue(any(x.get('twist', [0])[0] > 0 for x in c.calls))
        sensor.failed = True
        time.sleep(.15)
        count = len(c.calls)
        self.assertFalse(actions.snapshot()['wandering']['active'])
        self.assertIn('disconnected', actions.last_error)
        self.assertEqual(c.calls[-1]['twist'], [0, 0, 0])
        time.sleep(.1)
        self.assertEqual(len(c.calls), count)

    def test_stop_during_sensor_io_prevents_late_motion(self):
        entered, release = threading.Event(), threading.Event()
        class SlowSensor:
            def read(self):
                entered.set(); release.wait(1)
                return {'distances_m': [1]*8}
        c = Controller(); actions = Actions(c, SlowSensor())
        actions.execute('wander')
        self.assertTrue(entered.wait(1))
        actions.stop(); count = len(c.calls)
        release.set(); time.sleep(.1)
        self.assertEqual(len(c.calls), count)
        self.assertEqual(c.calls[-1]['twist'], [0, 0, 0])


if __name__ == '__main__': unittest.main()
