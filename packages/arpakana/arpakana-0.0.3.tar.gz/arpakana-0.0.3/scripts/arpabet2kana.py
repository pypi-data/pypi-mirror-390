"""CLI wrapper around :func:`arpakana.arpabet.arpabet_to_kana`."""

from __future__ import annotations

import argparse
import sys

from arpakana.arpabet import arpabet_to_kana


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert ARPAbet tokens to Katakana")
    parser.add_argument("phonemes", nargs="*", help="Space-separated ARPAbet tokens")
    parser.add_argument(
        "-u",
        "--unknown",
        default="?",
        help="Fallback string for unmapped phonemes (default: '?')",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.phonemes:
        tokens = args.phonemes
    else:
        data = sys.stdin.read().strip()
        tokens = data.split()

    if not tokens:
        parser.error("No ARPAbet tokens provided")

    result = arpabet_to_kana(tokens, unknown=args.unknown)
    print(result)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
