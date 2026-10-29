import sys
from pathlib import Path
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'xgo-runtime/python'))
from talkingduck.actions import Actions
from talkingduck.speech import command_for, select_spoken_command

class Controller:
    def __init__(self):
        self.mode = 'shadow'
        self.calls = []
        self.ready = True
    def status(self):
        return {'full_robot_ready': self.ready, 'control_ready': self.mode not in ('calibrate', 'servo_debug'), 'mode': self.mode}
    def command(self, **kwargs): self.calls.append(kwargs)
    def set_mode(self, mode): self.mode = mode

class Commands(unittest.TestCase):
    def test_wake_negation_and_complete_utterance(self):
        self.assertEqual(select_spoken_command('duck walk', 'duck walk', 1, 1, True), 'walk')
        for general, candidate in [('walk', 'walk'), ('walk', 'duck walk'), ('duck do not walk', 'duck walk'), ('duck walk and stop', 'duck walk')]:
            self.assertIsNone(select_spoken_command(general, candidate, 1, 1, True))
        for phrase in ('do not walk', 'sit and stand', 'what is standing', 'dance'):
            self.assertIsNone(command_for(phrase))

    def test_sit_is_explicitly_unavailable_and_never_changes_mode(self):
        c = Controller(); actions = Actions(c)
        result = actions.execute('sit')
        self.assertFalse(result['accepted'])
        self.assertIn('no deployed', result['reason'])
        self.assertEqual(c.mode, 'shadow')
        self.assertEqual(c.calls, [])

    def test_missing_feedback_blocks_motion_but_not_disarm(self):
        c = Controller(); c.ready = False; actions = Actions(c)
        self.assertFalse(actions.execute('walk')['accepted'])
        self.assertEqual(c.calls, [])
        self.assertTrue(actions.execute('rest')['accepted'])
        self.assertEqual(c.mode, 'off')

    def test_stop_cancels_inflight_walk(self):
        c = Controller(); actions = Actions(c)
        self.assertTrue(actions.execute('walk')['accepted'])
        time.sleep(.12)
        self.assertTrue(any(call.get('twist', [0])[0] > 0 for call in c.calls))
        actions.stop(); count = len(c.calls)
        time.sleep(.15)
        self.assertEqual(len(c.calls), count)
        self.assertEqual(c.calls[-1]['twist'], [0, 0, 0])

    def test_unknown_commands_never_enable_motors(self):
        c = Controller(); actions = Actions(c)
        self.assertFalse(actions.execute(None)['accepted'])
        self.assertEqual(c.mode, 'shadow')

if __name__ == '__main__': unittest.main()
