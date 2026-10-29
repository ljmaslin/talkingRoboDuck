# Third-party code and provenance

The project now targets XGO-Duck only. Upstream names and historical attribution
inside XGO's repositories are retained because XGO derives from earlier work.
They are not alternate robot backends in this application.

- `xgo-runtime/`: pinned Git submodule referencing Luwu Dynamics XGO runtime,
  extended locally by `runtime-overlay/`. No
  top-level software license was present in that checkout; confirm reuse terms
  before distributing a derivative outside this personal development project.
- `xgo-rl/`: Luwu's downstream training code, Apache-2.0 per its LICENSE. Keep
  its internal package names, license and asset notices. The workspace selects
  XGO's MJCF, policies and Feetech 1910 model. It does not load the original
  Microduck model or Pollen robot daemon. File-level model terms remain applicable.
- `xgo-rl/vendor/bam`: Rhoban Better Actuator Models, Apache-2.0. This sim uses
  the XGO 1910 M6 parameters with its STS3215-compatible motor formulation.
- `viewer/vendor`: Three.js 0.164.x, MIT license retained in THREE-LICENSE.txt.
- `models/vosk-model-small-en-us-0.15`: Vosk English model, Apache-2.0; upstream
  https://alphacephei.com/vosk/models . It is included in the App Lab package.
- Our speech/transport/test additions retain the Apache-2.0 LICENSE at root.
- `xgo-runtime/python/talkingduck/native/aarch64`: Debian libatomic1 ARM64
  12.2.0-14+deb12u1, GCC Runtime Library Exception; full Debian/GCC copyright
  and source reference accompany it. Needed by Vosk's ARM wheel.

Our Apache-2.0 license covers our additions, not a relicensing of the upstream
runtime. This repository records upstream Git links and our integration patch;
setup fetches and prepares the full application locally. Generated deployment
ZIPs are excluded from Git. No credentials are included.
