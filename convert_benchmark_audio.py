"""Compatibility entry point for audio preparation.

Audio preparation reads raw_audio/ and writes cleaned_audio/ without mutating
the authoritative benchmark manifest.
"""

from validate_and_prep import main


if __name__ == "__main__":
    raise SystemExit(main())
