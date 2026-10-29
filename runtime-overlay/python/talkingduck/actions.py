"""The same controller adapter is used on the UNO Q and in the test harness."""
import threading
import time


class Actions:
    def __init__(self, controller, ranges=None):
        self.controller = controller
        self.lock = threading.RLock()
        self.generation = 0
        self.last_error = ''
        self.ranges = ranges
        self.wander = {'active': False, 'phase': 'idle', 'turns': 0,
                       'sensor': 'not configured' if ranges is None else 'range service'}

    def snapshot(self):
        state = self.controller.status()
        state['speech_last_error'] = self.last_error
        with self.lock:
            state['wandering'] = dict(self.wander)
        return state

    def stop(self):
        with self.lock:
            self.generation += 1
            self.wander['active'] = False
            self.wander['phase'] = 'idle'
            try:
                self.controller.command(twist=[0, 0, 0])
            except ValueError:
                # In commissioning modes no travel command is accepted anyway.
                return {'accepted': True, 'reason': 'Travel cancelled; commissioning mode is active.'}
        return {'accepted': True, 'reason': 'Travel stopped; the current control mode keeps balance.'}

    def execute(self, command):
        with self.lock:
            if command == 'stop':
                return self.stop()
            if command == 'rest':
                self.stop()
                self.controller.set_mode('off')
                return {'accepted': True, 'reason': 'Motor torque released. The robot must be supported.'}
            if command == 'sit':
                return {'accepted': False, 'reason': 'Sit is recognised, but this XGO runtime has no deployed sit/stand policy. No movement requested.'}
            if command == 'wander' and self.ranges is None:
                return {'accepted': False, 'reason': 'Wandering needs a configured depth sensor. The XGO kit has none.'}
            if command not in ('stand', 'walk', 'wander', 'pick', 'open beak', 'close beak', 'rest'):
                return {'accepted': False, 'reason': 'No supported complete XGO command recognised.'}
            state = self.snapshot()
            if not state.get('full_robot_ready') or not state.get('control_ready'):
                return {'accepted': False, 'reason': 'XGO feedback is not ready, or calibration/servo setup is active.'}
            self.stop()
            try:
                if command == 'rest':
                    self.controller.set_mode('off')
                    reason = 'Motor torque released. The robot must be supported.'
                elif command in ('stand', 'walk', 'wander'):
                    self.controller.set_mode('policy')
                    self.controller.command(twist=[0, 0, 0])
                    reason = 'XGO walking/get-up policy enabled with zero travel command.'
                    if command == 'walk':
                        generation = self.generation
                        threading.Thread(target=self._walk, args=(generation,), daemon=True).start()
                        reason = 'XGO forward command, at most two seconds; measured travel is shown by the simulator.'
                    elif command == 'wander':
                        self.wander.update(active=True, phase='checking sensor', turns=0)
                        threading.Thread(target=self._wander, args=(self.generation,), daemon=True).start()
                        reason = 'Autonomous wandering started. Stop travel cancels it; missing depth data stops travel.'
                elif command == 'pick':
                    if self.controller.mode != 'policy':
                        return {'accepted': False, 'reason': 'Stand up before picking.'}
                    self.controller.start_pick()
                    reason = 'XGO pick policy requested.'
                else:
                    self.controller.command(mouth=30 if command == 'open beak' else 0)
                    reason = 'XGO mouth target set; its motor is separate from the 14-joint walking model.'
                self.last_error = ''
                return {'accepted': True, 'reason': reason}
            except ValueError as exc:
                return {'accepted': False, 'reason': str(exc)}

    def _walk(self, generation):
        deadline = time.monotonic() + 2.0
        try:
            while time.monotonic() < deadline:
                with self.lock:
                    if generation != self.generation:
                        return
                    if self.controller.mode != 'policy':
                        return
                    self.controller.command(twist=[0.25, 0, 0])
                time.sleep(.05)
        except Exception as exc:
            self.last_error = str(exc)
        finally:
            with self.lock:
                if generation == self.generation:
                    self.stop()

    def _wander(self, generation):
        from .wandering import WanderPlan
        plan = WanderPlan()
        try:
            while True:
                with self.lock:
                    if generation != self.generation or self.controller.mode != 'policy':
                        return
                # Sensor I/O is outside the action lock so Stop responds immediately.
                frame = self.ranges.read()
                twist = plan.step(frame['distances_m'], time.monotonic())
                with self.lock:
                    if generation != self.generation:
                        return
                    state = self.controller.status()
                    if not state['full_robot_ready'] or not state['control_ready'] or state['mode'] != 'policy':
                        raise ValueError('Robot feedback/control is unavailable.')
                    self.controller.command(twist=twist)
                    self.wander.update(phase=plan.phase, turns=plan.turns,
                        nearest_m=round(min(frame['distances_m']), 3),
                        sensor=frame.get('source', 'range service'), simulated=frame.get('simulated', False))
                time.sleep(.05)
        except Exception as exc:
            with self.lock:
                if generation == self.generation:
                    self.last_error = str(exc)
        finally:
            with self.lock:
                if generation == self.generation:
                    self.stop()
