"""Generate a CMUdict-based word list covering all stressless ARPAbet trigrams."""

from __future__ import annotations

import argparse
import collections.abc as cabc
import logging
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from heapq import heapify, heappop, heappush
from pathlib import Path
from typing import cast

logger = logging.getLogger(__name__)

CMUDICT_URL = (
    "https://raw.githubusercontent.com/cmusphinx/cmudict/refs/heads/master/cmudict.dict"
)

Trigram = tuple[str, str, str]

START_SENTINEL = "<s>"
END_SENTINEL = "</s>"


@dataclass(frozen=True)
class CMUDictEntry:
    """Represents a single CMUdict pronunciation."""

    word: str
    raw_phonemes: tuple[str, ...]
    normalized: tuple[str, ...]


def load_cmudict(url: str) -> list[CMUDictEntry]:
    """Download CMUdict and return entries with digit-stripped phonemes.

    Args:
        url: Raw URL pointing to ``cmudict.dict``.

    Returns:
        A list of entries, each containing the surface word and normalized phonemes.
    """

    entries: list[CMUDictEntry] = []

    with urllib.request.urlopen(url) as response:  # nosec B310
        for raw_line in _iter_lines(response):
            if not raw_line or raw_line.startswith(";;;"):
                continue
            try:
                word, phoneme_blob = raw_line.split(maxsplit=1)
            except ValueError:
                continue
            raw_phonemes, normalized = _parse_phonemes(phoneme_blob)
            if not normalized:
                continue
            entries.append(
                CMUDictEntry(
                    word=word,
                    raw_phonemes=raw_phonemes,
                    normalized=normalized,
                )
            )

    logger.info("Loaded %d CMUdict entries with >=1 phoneme", len(entries))
    return entries


def _iter_lines(response: cabc.Iterable[bytes]) -> cabc.Iterator[str]:
    """Yield decoded lines from a byte iterator without trailing whitespace."""

    for chunk in response:
        yield chunk.decode("utf-8").strip()


def _parse_phonemes(phoneme_blob: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return raw phonemes and versions without trailing stress digits."""

    content = phoneme_blob.split("#", 1)[0].strip()
    if not content:
        return tuple(), tuple()
    raw_tokens = tuple(token for token in content.split() if token)
    normalized = tuple(token.rstrip("0123456789") for token in raw_tokens)
    return raw_tokens, normalized


def select_trigram_cover(entries: cabc.Sequence[CMUDictEntry]) -> list[CMUDictEntry]:
    """Pick a subset of entries whose trigrams cover the full CMUdict trigram set.

    Args:
        entries: CMUdict entries (stressless), ordered deterministically.

    Returns:
        Entries selected by a greedy set-cover heuristic.
    """

    trigram_to_indices: dict[Trigram, set[int]] = defaultdict(set)
    entry_trigrams: list[set[Trigram]] = []
    filtered_entries: list[CMUDictEntry] = []

    for entry in entries:
        padded = (
            START_SENTINEL,
            START_SENTINEL,
            *entry.normalized,
            END_SENTINEL,
            END_SENTINEL,
        )
        trigrams = {cast("Trigram", padded[i : i + 3]) for i in range(len(padded) - 2)}
        idx = len(filtered_entries)
        filtered_entries.append(entry)
        entry_trigrams.append(set(trigrams))
        for trigram in trigrams:
            trigram_to_indices[trigram].add(idx)

    remaining = set(trigram_to_indices)
    heap: list[tuple[int, int]] = [
        (-len(trigrams), idx) for idx, trigrams in enumerate(entry_trigrams)
    ]
    heapify(heap)

    selection: list[int] = []

    while remaining and heap:
        neg_count, idx = heappop(heap)
        trigrams = entry_trigrams[idx]
        if not trigrams:
            continue
        current_size = len(trigrams)
        if -neg_count != current_size:
            heappush(heap, (-current_size, idx))
            continue

        selection.append(idx)
        _consume_trigrams(idx, remaining, trigram_to_indices, entry_trigrams, heap)

    if remaining:
        raise RuntimeError("Failed to cover all trigrams")

    logger.info(
        "Selected %d entries to cover %d trigrams",
        len(selection),
        len(trigram_to_indices),
    )

    return sorted(
        (filtered_entries[idx] for idx in selection), key=lambda entry: entry.word
    )


def _consume_trigrams(
    idx: int,
    remaining: set[Trigram],
    trigram_to_indices: dict[Trigram, set[int]],
    entry_trigrams: list[set[Trigram]],
    heap: list[tuple[int, int]],
) -> None:
    """Remove covered trigrams and update candidate counts."""

    for trigram in tuple(entry_trigrams[idx]):
        if trigram not in remaining:
            continue
        remaining.remove(trigram)
        for other_idx in trigram_to_indices[trigram]:
            other_trigrams = entry_trigrams[other_idx]
            if trigram in other_trigrams:
                other_trigrams.remove(trigram)
                if other_idx != idx:
                    heappush(heap, (-len(other_trigrams), other_idx))
    entry_trigrams[idx].clear()


def write_wordlist(entries: cabc.Sequence[CMUDictEntry], destination: Path) -> None:
    """Write the selected entries to ``destination`` with tab-separated phonemes."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as handle:
        for entry in entries:
            handle.write(entry.word)
            handle.write("\t")
            handle.write(" ".join(entry.raw_phonemes))
            handle.write("\n")

    logger.info("Wrote %d entries to %s", len(entries), destination)


def parse_args(argv: cabc.Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=CMUDICT_URL, help="Raw URL to cmudict.dict")
    parser.add_argument(
        "--output",
        default="tests/data/cmudict_trigram_wordlist.txt",
        help="Destination file for the generated word list",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (e.g. DEBUG, INFO, WARNING)",
    )
    return parser.parse_args(argv)


def configure_logging(level_name: str) -> None:
    """Configure root logging using a simple format."""

    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")


def main(argv: cabc.Sequence[str] | None = None) -> None:
    """CLI entry point."""

    args = parse_args(argv)
    configure_logging(args.log_level)

    entries = load_cmudict(args.url)
    selection = select_trigram_cover(entries)
    write_wordlist(selection, Path(args.output))


if __name__ == "__main__":
    main()
