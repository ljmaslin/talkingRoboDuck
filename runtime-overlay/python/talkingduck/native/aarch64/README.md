# Bundled ARM64 atomic runtime

`libatomic.so.1` is the real `libatomic.so.1.2.0` from Debian bookworm's
`libatomic1:arm64` version `12.2.0-14+deb12u1`. It is needed by Vosk's ARM64
wheel. Recognizer preloads it with RTLD_GLOBAL before importing Vosk. x86-64
does not load this ARM library. This avoids modifying the App Lab image.

Debian/GCC copyright and licensing, including GCC Runtime Library Exception,
are retained verbatim in COPYRIGHT. Source package:
https://sources.debian.org/src/gcc-12/12.2.0-14%2Bdeb12u1/

The app manifest hashes the library. It is not a microphone driver and does
not provide ALSA device permissions.
