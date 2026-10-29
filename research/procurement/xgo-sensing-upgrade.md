# XGO sensing upgrade — checked 28 October 2026

The ordered XGO kit includes a QMI8658A balance IMU, not a depth sensor,
camera, microphone or speaker. This was an omission in the earlier comparison.
The original procurement total excludes these upgrades; do not treat it as
a price for a sensor-equipped equivalent of Pollen Microduck.

## Depth sensor: proposed physical integration

| Part | UK price including VAT | Listing |
| --- | ---: | --- |
| Pimoroni PIM622 VL53L5CX 8×8 ToF breakout | £19.50 | https://thepihut.com/products/vl53l5cx-8x8-time-of-flight-tof-array-sensor-breakout |
| JST-SH 4-pin plug-to-plug cable, 200 mm, SKU 104965 | £1.00 | https://thepihut.com/products/stemma-qt-qwiic-jst-sh-4-pin-cable-200mm-long |
| UK Royal Mail 1st Class delivery, advertised 1–2 days after dispatch | £3.80 | https://thepihut.com/pages/delivery |
| **Subtotal** | **£24.30** | Excludes printed bracket and M2.5 fixings |

Both parts listed in stock at check; final SO50 checkout and availability
remain untested. The sensor is 19×19×4.6 mm, with two M2.5 holes 13.6 mm apart:
https://shop.pimoroni.com/products/vl53l5cx-time-of-flight-tof-sensor-breakout .
These are design dimensions, not an existing fitted XGO mount.

Proposed first mount: a light forward-facing bracket on the body, with the
optical windows uncovered and clear of the moving beak/legs. A head mount
would require transforming depth using head joint angles. Do not cover the
sensor with arbitrary transparent plastic; cover-glass crosstalk is a real
calibration issue. Mount clearance and fastener length await physical inspection.

With power off, connect the breakout's Qw/ST socket to UNO Q's Qwiic socket
using the keyed cable. Qwiic carries GND, **3.3V**, SDA and SCL; no soldering,
separate power supply or level shifter is expected for these two Qwiic ports.
Never connect the robot battery to the sensor. Verify socket access in the
assembled controller stack before ordering a final cable length.

Arduino's manual identifies this bus as **Wire1 / I2C4**, MCU PD13 SDA / PD12
SCL, separate from the XGO IMU's **Wire / D20 SDA / D21 SCL**. The sensor's
7-bit address is **0x29** (the PCB's historical 0x52 marking is the 8-bit form).
https://docs.arduino.cc/tutorials/uno-q/user-manual/?queryID=bbb993e8bdbcff412df9e47ab674ffd1

Software work remains: adapt and compile a VL53L5CX driver for the UNO Q MCU,
initialise it before motor arming, schedule reads without disrupting the
100 Hz motor/IMU loop, publish timestamped zones and valid/invalid status
through Arduino Bridge, then implement the physical range adapter in Python.
The current firmware and ZIP do **not** implement this driver. Published Pico
or Raspberry Pi support does not prove UNO Q compatibility.

The virtual sensor is an ideal 8-ray horizontal slice, 45° field of view and
1.2 m limit. It is not a validated emulation of the full 64-zone VL53L5CX:
it omits reflectivity, sunlight, glass, invalid zones, tilt, cover calibration,
ground rejection and interference. Real avoidance must handle these and stairs.
Matching the sensor chip alone does not provide Pollen's SLAM software.
Pollen reports practical mapping returns mostly below a metre:
https://pollen-robotics.com/microduck/blog/microduck-slam/ .

## Camera: additional parts, not included in £24.30

Candidate: **Waveshare WAV-21635 5MP OV5640 autofocus USB camera, £27.90
including VAT**, matching USB cable included; listed four units at check.
https://thepihut.com/products/5mp-ov5640-auto-focus-usb-camera-board
This is a UVC camera candidate, not a tested or mechanically fitted XGO upgrade.
Do not buy a bare Raspberry Pi CSI camera assuming its ribbon plugs into UNO Q.

UNO Q supports USB cameras through a USB-C hub. Its documented initial SBC
setup uses a hub with external USB-C Power Delivery. Candidate **Anker 332
A8355H11**, **£21.38 tax included**, in-stock listing:
https://gsmnet.uk/products/anker-332-usb-c-hub-2-x-usb-a-2-x-usb-c-1-x-hdmi-gray-a8355h11 .
Shipping not quoted; no specific UNO Q compatibility test exists for this hub.
Manufacturer port specification:
https://www.anker.com/products/a8355 .

**Camera + candidate hub subtotal: £49.28**, before delivery, external power,
mounting and any extra power cable. With depth sensor/cable: **£69.78 parts**.
This is not a complete mobile-vision price. Existing suitable hub/charger may
avoid some purchases. USB host mode can require explicit setup when the UNO Q
is powered from the robot rather than USB-C:
https://docs.arduino.cc/tutorials/uno-q/host-mode/ .

User requested budgeting for both hub and PSU. Candidate bench PSU: **Raspberry
Pi 27W USB-C power supply, UK white SC1149, £11.50 including VAT**, in stock,
with captive USB-C lead. Its standard PD profiles include 5V/3A:
https://thepihut.com/products/raspberry-pi-27w-usb-c-power-supply .
This matches the UNO Q's requested voltage/current on paper; operation through
the selected hub still needs a bench check. Connect the PSU to the hub's PD
input, the hub's upstream cable to UNO Q, and the camera to a hub USB data port.
It is mains power for initial supported testing, not battery-powered wandering.

Depth sensor + cable + camera + candidate hub + PSU = **£81.28 parts**.
The Pi Hut's advertised £3.80 postage would make **£85.08 plus the hub supplier's
unquoted delivery**, plus mounting/fixings. Use **£95 as a provisional bench
upgrade allowance**, not a delivered checkout quote. The hub's dispatch origin,
SO50 delivery cost/ETA and actual UNO Q negotiation are not verified; do not
order it as a guaranteed complete mobile solution. Camera/hub/audio mobile
power hardware is still outside this allowance.
Current power documentation describes a VBUS back-drive path but warns that
available peripheral power shares the board budget:
https://docs.arduino.cc/tutorials/uno-q/power-specification?queryID=2aa1d01e13483af851bf99090e9e0e3c .
Do not assume the XGO expansion board's regulator has spare current for a
camera/hub/audio. A compact battery-powered solution needs measured load,
regulator and backfeed checks; the matched XGO board's continuous accessory
current is not documented. No arbitrary battery wiring is prescribed here.

Recommend depth sensing first for obstacle avoidance. Vision/person following
is a separate hardware, mounting, power and software step. Audio remains
additional; neither this depth sensor nor the listed camera is a speaker.
