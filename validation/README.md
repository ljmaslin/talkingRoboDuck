# Recorded validation — 28 October 2026

These reports describe the tested development build, not fresh measurements on
the reader's machine or actual XGO hardware. Package hashes in the integration,
ARM64 and wandering reports refer to the same local deployment ZIP. Generated
ZIPs are not committed; a rebuild can have a different archive hash.

- 11 unit tests passed, including command rejection, cancellation, missing
  sensors, disconnected sensors, stale/replayed/invalid readings and trapped turns.
- `xgo-integration.json`: nine end-to-end checks using synthetic WAV speech,
  Vosk, the real XGO controller and MuJoCo/BAM physics. Includes unavailable sit,
  measured standing/walking, expiry, and stop cancellation.
- `xgo-wandering-check.json`: 90 seconds, 8.42 m measured path, 14 obstacle
  avoidance turns and zero wall/box contact steps. Uses an ideal eight-ray
  depth slice, not a physical VL53L5CX or a full 64-zone model.
- `xgo-arm64-check.json`: 60 packaged files verified; all five ONNX models
  loaded and six speech fixtures checked under ARM64 emulation.
- `xgo-browser-check.json`: measured geometry displayed without browser
  exceptions in isolated headless Chrome. Its software-renderer FPS is not a
  benchmark of the user's GPU. No live microphone permission test is implied.

Hardware calibration, driver timing, real audio, physical depth sensing,
camera/mounting/power and on-board performance remain unvalidated.
