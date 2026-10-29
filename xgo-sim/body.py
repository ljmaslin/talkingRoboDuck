"""External test equipment: XGO MuJoCo body, BAM motors and MCU ABI emulator.

No speech or policy inference lives here. STM32 firmware/serial electronics are
emulated, not executed. Before first ARM, physics is paused at the spawn pose.
"""
import base64
import collections
import json
import math
from pathlib import Path
import socketserver
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import mujoco
import numpy as np
from bam.model import load_model
from bam.mujoco import MujocoController
from rl_core import MOTOR_IDS, POLICY_IDS
from wire import STATE, COMMAND, ALL_MASK, ARM, DISARM, POLICY, HOLD

NAMES = ['left_hip_yaw', 'left_hip_roll', 'left_hip_pitch', 'left_knee', 'left_ankle',
         'neck_pitch', 'head_pitch', 'head_yaw', 'head_roll',
         'right_hip_yaw', 'right_hip_roll', 'right_hip_pitch', 'right_knee', 'right_ankle']
ROOT = Path('/opt/xgo/model')

class World:
    def __init__(self):
        spec = mujoco.MjSpec.from_file(str(ROOT/'scene.xml'))
        # Static test-room furniture: metres, MuJoCo half extents.
        room = [
            ('north', [0, 1.2, .16], [1.24, .04, .16], [.35, .62, .67, 1]),
            ('south', [0, -1.2, .16], [1.24, .04, .16], [.35, .62, .67, 1]),
            ('east', [1.2, 0, .16], [.04, 1.2, .16], [.35, .62, .67, 1]),
            ('west', [-1.2, 0, .16], [.04, 1.2, .16], [.35, .62, .67, 1]),
            ('orange_box', [.75, 0, .15], [.16, .19, .15], [.87, .43, .23, 1]),
            ('blue_box', [-.48, .52, .13], [.22, .16, .13], [.27, .50, .84, 1]),
            ('green_box', [-.50, -.66, .12], [.18, .14, .12], [.42, .68, .36, 1]),
        ]
        for name, pos, size, rgba in room:
            spec.worldbody.add_geom(name='room_'+name, type=mujoco.mjtGeom.mjGEOM_BOX,
                pos=pos, size=size, rgba=rgba, group=4, contype=1, conaffinity=3)
        self.model = m = spec.compile()
        m.opt.timestep = .005
        # Match xgoduck_constants.py contacts without importing the GPU training stack.
        for i in range(m.ngeom):
            name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_GEOM, i) or ''
            if name.startswith('room_'):
                m.geom_contype[i], m.geom_conaffinity[i] = 1, 3
            elif name == 'floor':
                m.geom_contype[i], m.geom_conaffinity[i] = 1, 1
            elif name.endswith('_collision'):
                m.geom_contype[i], m.geom_conaffinity[i] = (3, 2) if name in ('trunk_collision', 'head_collision') else (1, 0)
                m.geom_condim[i] = 3 if name in ('left_foot_collision', 'right_foot_collision') else 1
                if name in ('left_foot_collision', 'right_foot_collision'):
                    m.geom_friction[i, 0] = 1.0
                    m.geom_priority[i] = 1
            else:
                m.geom_contype[i], m.geom_conaffinity[i] = 0, 0
        self.data = d = mujoco.MjData(m)
        self.joint_ids = [m.joint(name).id for name in NAMES]
        self.qadr = m.jnt_qposadr[self.joint_ids]
        self.vadr = m.jnt_dofadr[self.joint_ids]
        actuators = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i) for i in range(m.nu)]
        if len(actuators) != 14: raise RuntimeError('XGO walking body must have 14 actuated joints')
        # BAM supplies motor torque; don't apply the companion XML position gain again.
        m.actuator_gainprm[:] = 0
        m.actuator_gainprm[:, 0] = 1
        m.actuator_biasprm[:] = 0
        m.actuator_biastype[:] = 0
        m.actuator_ctrllimited[:] = False
        m.actuator_forcelimited[:] = False
        self.motor_model = load_model(str(ROOT/'params/1910_m6.json'))
        self.motor_model.actuator.kp = 5.0
        self.motor_model.actuator.vin = 7.4
        self.bam = MujocoController(self.motor_model, actuators, m, d)
        self.actuator_names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[i, 0]) for i in range(m.nu)]
        self.policy_to_actuator = [NAMES.index(name) for name in self.actuator_names]
        self.lock = threading.RLock()
        self.started = time.monotonic()
        self.seq = self.command_seq = self.bad = 0
        self.command_at = 0
        self.last_ordered_seq = None
        self.ttl = .25
        self.geometry = self._geometry()
        self.reset()

    def reset(self):
        with self.lock:
            mujoco.mj_resetDataKeyframe(self.model, self.data, self.model.key('STAND').id)
            mujoco.mj_forward(self.model, self.data)
            self.bam.reset(self.data.qpos)
            self.bam.last_ts = self.data.time
            self.motor_model.actuator.q_target_smooth = self.bam.q_target.copy()
            # Reset simulates restarting both body and MCU; Controller.receive
            # detects the sequence restart and resets its IMU/policy history.
            self.seq = self.command_seq = 0
            self.last_ordered_seq = None
            self.targets = self.angles()
            self.enabled = self.running = self.timed_out = False
            self.queue = collections.deque()
            self.reset_wall = time.monotonic()
            self.range_sequence = 0
            self.range_at = time.monotonic()
            self.room_contacts = 0

    def angles(self):
        values = np.rad2deg(self.data.qpos[self.qadr])
        return [float(values[POLICY_IDS.index(i)]) if i in POLICY_IDS else 0.0 for i in MOTOR_IDS]

    def command(self, raw):
        if len(raw) != COMMAND.size: self.bad += 1; return
        x = COMMAND.unpack(raw)
        magic, seq, source, ttl, mode = x[:5]
        targets = list(x[7:])
        now = time.monotonic()
        age = (int((now-self.started)*1e6)-source) & 0xffffffff
        with self.lock:
            ordered = self.last_ordered_seq is None or 0 < ((seq-self.last_ordered_seq)&0xffffffff) < 0x80000000
            if magic != b'DQC1' or mode not in (DISARM, ARM, POLICY, HOLD) or not all(math.isfinite(v) for v in targets):
                self.bad += 1; return
            if mode != DISARM and (age > 150000 or not ordered):
                self.bad += 1; return
            self.last_ordered_seq = self.command_seq = seq
            self.command_at, self.ttl = now, min(ttl/1e6, .25)
            if mode == DISARM:
                self.enabled = False
            elif mode == ARM:
                if not self.running:
                    self.reset_wall = now
                self.enabled = self.running = True
                self.timed_out = False
            self.targets = targets

    def step(self):
        with self.lock:
            self.range_sequence += 1
            self.range_at = time.monotonic()
            if self.enabled and time.monotonic()-self.command_at > self.ttl:
                self.enabled = False
                self.timed_out = True
            if not self.running:
                return
            if self.enabled:
                policy_target = np.deg2rad([self.targets[MOTOR_IDS.index(i)] for i in POLICY_IDS])
                self.queue.append(policy_target)
                # Representative 15 ms command lag, within XGO's 15–30 ms training range.
                if len(self.queue) > 3:
                    self.bam.q_target = self.queue.popleft()[self.policy_to_actuator]
                self.bam.update()
            else:
                self.data.ctrl[:] = 0
                self.queue.clear()
            mujoco.mj_step(self.model, self.data)
            for contact in self.data.contact:
                if (self.model.geom_group[contact.geom1] == 4 or self.model.geom_group[contact.geom2] == 4):
                    self.room_contacts += 1

    def feedback(self):
        with self.lock:
            self.seq = (self.seq+1)&0xffffffff
            stamp = int((time.monotonic()-self.started)*1e6)&0xffffffff
            angles = self.angles()
            v = np.rad2deg(self.data.qvel[self.vadr])
            velocities = [float(v[POLICY_IDS.index(i)]) if i in POLICY_IDS else 0.0 for i in MOTOR_IDS]
            # QMI payload is projected gravity/body axes; negative specific force at rest.
            acc = -self.data.sensor('imu_accel').data
            if not self.running:
                rotation = self.data.xmat[self.model.body('trunk_base').id].reshape(3, 3)
                acc = rotation.T @ self.model.opt.gravity
            gyro = np.rad2deg(self.data.sensor('imu_ang_vel').data)
            counts = [int(np.clip(round(x*16384/9.8), -32768, 32767)) for x in acc]
            counts += [int(np.clip(round(x*32), -32768, 32767)) for x in gyro]
            age = min(int((time.monotonic()-self.command_at)*1e6), 0xffffffff) if self.command_at else 0xffffffff
            flags = 1 | (2 if self.enabled else 0) | (4 if self.timed_out else 0)
            return STATE.pack(b'DQS1', 1, flags, ALL_MASK, self.seq, stamp, stamp,
                self.command_seq, age, 10000, 0, 0, 0, self.bad, *counts, *angles, *velocities, *self.targets)

    def _geometry(self):
        m = self.model
        meshes, geoms = {}, []
        for i in range(m.ngeom):
            if m.geom_group[i] == 4:
                geoms.append({'id': i, 'type': 'box', 'size': m.geom_size[i].tolist(),
                    'color': '#'+''.join(f'{int(v*255):02x}' for v in m.geom_rgba[i, :3]), 'body': 'room'})
                continue
            mesh = int(m.geom_dataid[i])
            if m.geom_group[i] != 2 or mesh < 0: continue
            key = str(mesh)
            if key not in meshes:
                va, vn = int(m.mesh_vertadr[mesh]), int(m.mesh_vertnum[mesh])
                fa, fn = int(m.mesh_faceadr[mesh]), int(m.mesh_facenum[mesh])
                meshes[key] = {'vertices': np.round(m.mesh_vert[va:va+vn], 7).reshape(-1).tolist(),
                               'indices': m.mesh_face[fa:fa+fn].reshape(-1).tolist()}
            name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.geom_bodyid[i]) or ''
            color = '#f3c64c' if any(word in name for word in ('head', 'jaw', 'trunk')) else '#e6e5d8'
            geoms.append({'id': i, 'mesh': key, 'body': name, 'color': color})
        return {'robot': 'XGO-Duck', 'meshes': meshes, 'geoms': geoms, 'source': 'XGO MJCF geometry compiled by MuJoCo'}

    def ranges(self):
        """Ideal body-mounted horizontal depth slice, not a VL53L5CX hardware model.

        Only room geoms are visible to this virtual sensor. No ground-truth
        position, heading, map or obstacle IDs cross into the robot application.
        """
        with self.lock:
            m, d = self.model, self.data
            rotation = d.xmat[m.body('trunk_base').id].reshape(3, 3)
            heading = math.atan2(rotation[1, 0], rotation[0, 0])
            origin = d.xpos[m.body('trunk_base').id].copy()
            origin[2] = .17  # ideal stabilised horizontal slice for first avoidance test
            mask = np.array([0, 0, 0, 0, 1, 0], dtype=np.uint8)
            distances = []
            for angle in np.linspace(22.5, -22.5, 8):
                yaw = heading+math.radians(float(angle))
                vector = np.array([math.cos(yaw), math.sin(yaw), 0.0])
                hit = np.array([-1], dtype=np.int32)
                distance = mujoco.mj_ray(m, d, origin, vector, mask, True, -1, hit)
                distances.append(round(min(1.2, max(.02, distance)) if distance >= 0 else 1.2, 4))
            return {'sequence': self.range_sequence, 'age_ms': (time.monotonic()-self.range_at)*1000,
                    'distances_m': distances, 'simulated': True,
                    'source': 'Ideal virtual depth slice: 8 rays, 45 degrees, 1.2 m'}

    def pose(self):
        with self.lock:
            positions = []
            for geom in self.geometry['geoms']:
                i = geom['id']
                quat = np.empty(4)
                mujoco.mju_mat2Quat(quat, self.data.geom_xmat[i])
                positions.append([i, *self.data.geom_xpos[i].tolist(), *quat.tolist()])
            return {'sim_t': float(self.data.time), 'base': self.data.qpos[:7].tolist(), 'geoms': positions,
                    'joints': dict(zip(NAMES, self.data.qpos[self.qadr].tolist()))}

    def status(self):
        with self.lock:
            elapsed = time.monotonic()-self.reset_wall
            return {'robot': 'XGO-Duck', 'role': 'External MuJoCo body + emulated MCU',
                'simulation_seconds': float(self.data.time), 'realtime_factor': round(self.data.time/max(elapsed, .001), 3),
                'trunk_z': float(self.data.qpos[2]), 'base': self.data.qpos[:7].tolist(),
                'enabled': self.enabled, 'paused_until_first_arm': not self.running,
                'motor_model': 'XGO 1910 M6 BAM, 7.4V, firmware kp=5',
                'physical_joints_in_model': 14, 'mouth_motor': 'virtual feedback only; walking MJCF has no mouth hinge',
                'firmware_executed': False, 'watchdog': self.timed_out, 'invalid_commands': self.bad,
                'environment': '2.4 m room, three boxes', 'room_contact_steps': self.room_contacts}

world = World()

def physics():
    deadline = time.monotonic()
    while True:
        world.step()
        deadline += .005
        time.sleep(max(0, deadline-time.monotonic()))
        if time.monotonic()-deadline > .1: deadline = time.monotonic()

class MCU(socketserver.StreamRequestHandler):
    def handle(self):
        closing = threading.Event()
        def send():
            deadline = time.monotonic()
            try:
                while not closing.is_set():
                    msg = {'method': 'duck_state', 'payload': base64.b64encode(world.feedback()).decode()}
                    self.request.sendall((json.dumps(msg)+'\n').encode())
                    deadline += .01
                    closing.wait(max(0, deadline-time.monotonic()))
            except OSError: pass
        threading.Thread(target=send, daemon=True).start()
        try:
            for line in self.rfile:
                if len(line) > 8192: break
                msg = json.loads(line)
                if msg.get('method') == 'duck_command':
                    world.command(base64.b64decode(msg['payload'], validate=True))
                # Calibration/servo commissioning are not faked as successful hardware operations.
        finally:
            closing.set()

class TCP(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

class HTTP(BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def reply(self, code, value):
        body = json.dumps(value).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        if self.path == '/state': self.reply(200, world.status())
        elif self.path == '/model': self.reply(200, world.geometry)
        elif self.path == '/pose': self.reply(200, world.pose())
        elif self.path == '/ranges': self.reply(200, world.ranges())
        elif self.path == '/poses':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                while True:
                    self.wfile.write(('data: '+json.dumps(world.pose())+'\n\n').encode())
                    self.wfile.flush()
                    time.sleep(1/30)
            except (OSError, ConnectionError): pass
        else: self.reply(404, {'error': 'Not found'})
    def do_POST(self):
        if self.path == '/reset':
            world.reset()
            self.reply(200, world.status())
        else: self.reply(404, {'error': 'Not found'})

threading.Thread(target=physics, daemon=True).start()
threading.Thread(target=TCP(('0.0.0.0', 7802), MCU).serve_forever, daemon=True).start()
print('XGO body + MCU ABI emulation on :7802, telemetry :8766', flush=True)
ThreadingHTTPServer(('0.0.0.0', 8766), HTTP).serve_forever()
