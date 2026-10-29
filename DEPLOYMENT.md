# Deploy Talking XGO Duck on your Arduino UNO Q

The deliverable is `artifacts/talking-xgo-0.2.0.zip`, an Arduino App Lab project.
It contains the XGO firmware source, controller, five supplied XGO ONNX models,
vendor calibration/control interface, our offline speech service, and the Vosk
English model. It contains no MuJoCo simulator, browser graphics library,
Pollen daemon, old `.deb` installer or API key.

1. Assemble and commission the kit using its matching hardware instructions.
2. Set up the UNO Q in Arduino App Lab. Import the ZIP as an application.
3. Follow XGO's first-time Bridge preparation in `xgo-runtime/README.md`:
   after the board libraries are downloaded, stop the app, run
   `python3 tools/prepare-bridge.py` and `sudo bash tools/router-2m.sh` on the UNO Q,
   then run the application. These configure the 2 Mbps Bridge; they are not PC
   simulation setup commands.
4. Use `http://<board-ip>:9527` for the supplied calibration and movement UI.
   Check actual servo IDs, centers and IMU before enabling motor torque.
5. `/talk.html` is our speech panel. For browser microphone input, reach it via
   HTTPS or a localhost port-forward to the board's port 9527. Plain
   `http://<board-ip>` supports typed controls but browsers block microphone capture
   there. Recognition and commands run on UNO Q, not in the browser. See
   https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia .

The app's `python/requirements.txt` is in Arduino's documented location. App Lab
installs Python dependencies; initial setup can require downloads. The bundled
speech model does not need a paid service. This is not an offline, complete board
OS image or proof that all dependencies are preinstalled on the shipping board.
The small ARM64 libatomic dependency required by Vosk is bundled and preloaded,
with its copyright and source reference; no manual apt installation is needed.
Desktop architecture checks use Debian bookworm/Python 3.12 under ARM64 emulation,
not the shipping App Lab image. Confirm that environment on arrival.

## Physical audio

Microphone capture defaults to disabled. Browser recording is the initial audio
adapter. After adding USB audio, `TALKING_DUCK_AUDIO_SOURCE=alsa` selects the
continuous ALSA adapter and `TALKING_DUCK_ALSA_DEVICE` selects the microphone.
That path requires `arecord` and the audio device to be made available in the
actual App Lab container. These OS/device permissions must be checked on the
board. No robot microphone or speaker was included in the ordered kit.

Motor-noise handling, speech playback, conversation and person following remain
hardware/integration work. No cloud LLM or paid requests are enabled.

## Supported voice controls

Require **Duck** before each spoken movement: Duck stand up, Duck walk forward,
Duck stop, Duck pick, Duck open beak, Duck close beak, Duck rest. Walk expires
after at most two seconds. Stop cancels travel while policy balance stays enabled.
Rest releases motor torque and requires the robot to be supported. Manual typed
commands use the same action adapter without the spoken prefix requirement.

Sit is recognised but explicitly refused: the supplied XGO runtime has no loaded
sit/stand policy. A training task alone is not a deployable policy. Do not copy
another robot's model into that slot.

## Depth sensing and wandering

Wandering is included in the Python package, but disabled unless a range
adapter is configured. The desktop Compose environment alone sets
`TALKING_DUCK_RANGE_URL=http://body:8766/ranges`. This is external simulated
sensor data, not a PC navigation service. Do not set that address on a real duck.

The ordered kit has no depth sensor or camera. The proposed sensor is a
VL53L5CX breakout on the UNO Q's 3.3V Qwiic / `Wire1` bus. A physical driver,
timestamped Arduino Bridge readings, mounting and testing still need work.
See [the detailed integration and cost notes](research/procurement/xgo-sensing-upgrade.md).
The simulator's ideal eight-ray slice is not the sensor's full 8×8 measurement
model and does not validate stairs, glass, moving objects or surface effects.

With a configured sensor, `wander` / `explore` starts continuous reactive
walking and turning; `stop` cancels it while keeping balance enabled. The
voice forms require Duck. The behaviour is local and uses no LLM or paid API.

## What has actually been tested

The desktop simulator extracts exactly this ZIP and runs its real Controller,
recognition and command adapter. Only Arduino Bridge transport and the MCU/body
are replaced by test equipment. The Arduino App Lab framework and STM32 firmware
are not executed by the desktop test. The shipping board and real acoustics have
not been tested. See `artifacts/xgo-integration.json` for measured desktop checks.

Arduino app format: https://github.com/arduino/arduino-app-cli/blob/main/docs/app-specification.md

Upstream runtime: https://github.com/LuwuDynamics/xgoduck_runtime_arduino
