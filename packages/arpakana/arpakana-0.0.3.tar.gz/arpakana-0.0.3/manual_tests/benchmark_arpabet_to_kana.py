"""Simple benchmark runner for arpabet_to_kana."""

import time
from pathlib import Path

from arpakana import arpabet_to_kana


def quick_benchmark():
    """Run a quick benchmark of arpabet_to_kana."""

    # Find data file
    data_file = Path(__file__).parent / "data" / "cmudict_trigram_wordlist.txt"

    if not data_file.exists():
        print(f"Error: Data file not found at {data_file}")
        return

    # Load data
    entries = []
    with data_file.open(encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                word = parts[0]
                phonemes = parts[1]
                entries.append((word, phonemes))

    print(f"Running benchmark with {len(entries)} entries...")

    # Single run benchmark
    start_time = time.perf_counter()

    for word, phonemes in entries:
        try:
            kana = arpabet_to_kana(phonemes)
        except Exception as e:
            print(f"Error converting {word}: {e}")

    end_time = time.perf_counter()
    total_time = end_time - start_time

    # Print results
    print(f"Total time: {total_time:.4f}s")
    print(f"Entries per second: {len(entries) / total_time:.1f}")
    print(f"Time per entry: {total_time / len(entries) * 1000:.3f}ms")

    # Show some sample results
    print("\nSample results:")
    for _i, (word, phonemes) in enumerate(entries[:5]):
        try:
            kana = arpabet_to_kana(phonemes)
            print(f"  {word}: {phonemes} → {kana}")
        except Exception as e:
            print(f"  {word}: {phonemes} → ERROR: {e}")


if __name__ == "__main__":
    quick_benchmark()
