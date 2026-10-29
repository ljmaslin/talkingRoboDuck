# Working on Talking XGO Duck

Initialise the pinned submodules and run `python tools/bootstrap_project.py`.
The exact upstream commits are recorded in `upstream-revisions.json` and the
Git submodule entries. Do not update these independently.

## Source boundaries

- Edit our application under `runtime-overlay/python/talkingduck/`.
- Run `python tools/bootstrap_project.py --skip-model` to copy that source
  into the prepared `xgo-runtime` checkout before running tests/builds.
- If editing vendor integration/controller/firmware directly in `xgo-runtime`,
  run `python tools/export_runtime_overlay.py` afterwards. This captures changes
  to tracked upstream files in `runtime-overlay/upstream.patch` and copies our
  application files back to their tracked overlay. Review the diff before committing.
- `assets/talk.html` and `assets/talk-client.js` are generated from `viewer/`
  by `tools/build_xgo_app.py`, so edit their source in `viewer/`.
- `xgo-rl` and `research/xgoduck_hardware` remain pinned upstream dependencies.

The runtime submodule is intentionally dirty after setup. The root status hides
worktree dirtiness for that submodule; `git -C xgo-runtime status --short` still
shows it. Our changes must be captured in the overlay before committing the root
repository. No application changes should exist solely in a local submodule.

`bootstrap_project.py` applies the integration patch only if it passes Git's
check; conflicting tracked vendor edits cause setup to stop. The overlay is
the canonical source for our Python additions and replaces their prepared copies.
Commit or export direct edits before running setup.

## Verification

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/build_xgo_app.py
docker compose -f xgo-sim/compose.yaml up -d --build
node viewer/serve.mjs
```

With the viewer and containers running, use separate terminals for
`python xgo-sim/test_integration.py` and `python xgo-sim/test_wandering.py`.
These move/reset the simulation: run one at a time and avoid manual control
during tests. The room test lasts 90 seconds and checks actual travel,
avoidance turns, contacts, balance and stopping. Neither test uses paid AI.

Hardware claims require actual board/sensor measurements. The simulator
substitutes MCU I/O and an ideal distance sensor; it does not execute the STM32
firmware or establish real obstacle avoidance. See ARCHITECTURE.md and DEPLOYMENT.md.
