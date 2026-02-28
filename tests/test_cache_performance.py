"""
Performance test for InstrumentCache multi-level caching.

This script demonstrates the performance improvements of the new caching strategy.
"""

import sys
import time
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from pyRofex_To_Excel.market_data.instrument_cache import InstrumentCache


def _build_mock_instruments(total: int = 400) -> list[dict]:
    """Create deterministic instruments for isolated cache performance testing."""
    instruments: list[dict] = []

    for idx in range(total):
        is_option = idx % 2 == 0
        symbol = (
            f"MERV - XMEV - GFGV{70000 + idx}O - 24hs"
            if is_option
            else f"MERV - XMEV - STK{idx:04d} - 24hs"
        )
        instruments.append(
            {
                "instrumentId": {"symbol": symbol},
                "cficode": "OCASPS" if is_option else "ESVUFR",
            }
        )

    return instruments


@pytest.mark.performance
def test_cache_performance(tmp_path):
    """Performance test with isolated cache data and bounded execution time."""
    cache = InstrumentCache(cache_dir=tmp_path / "cache", ttl_minutes=30)
    instruments = _build_mock_instruments(total=400)
    cache.save_instruments(instruments)

    stats = cache.get_cache_stats()
    assert stats["memory_cache_active"] is True
    assert stats["total_instruments"] == 400
    assert stats["total_options"] == 200

    # Force file-cache path to ensure no dependence on shared external cache state.
    cache._memory_cache = None
    cache._memory_cache_timestamp = None
    cache._symbol_to_instrument.clear()
    cache._options_symbols = None
    cache._all_symbols = None

    start = time.perf_counter()
    cache_data = cache.get_cached_instruments()
    file_load_ms = (time.perf_counter() - start) * 1000

    assert cache_data is not None
    assert cache_data["count"] == 400
    assert file_load_ms < 3000

    test_symbols = [
        "MERV - XMEV - STK0001 - 24hs",
        "MERV - XMEV - STK0003 - 24hs",
        "MERV - XMEV - GFGV70000O - 24hs",
        "MERV - XMEV - GFGV70002O - 24hs",
        "MERV - XMEV - STK0005 - 24hs",
    ]

    start = time.perf_counter()
    for symbol in test_symbols:
        instrument = cache.get_instrument_by_symbol(symbol)
        assert instrument is not None
    per_symbol_lookup_us = ((time.perf_counter() - start) * 1_000_000) / len(test_symbols)
    assert per_symbol_lookup_us < 10_000

    start = time.perf_counter()
    for _ in range(1000):
        for symbol in test_symbols:
            cache.is_option_symbol(symbol)
    batch_ms = (time.perf_counter() - start) * 1000
    assert batch_ms < 5000

    start = time.perf_counter()
    options_symbols = cache.get_options_symbols()
    options_ms = (time.perf_counter() - start) * 1000

    assert len(options_symbols) == 200
    assert options_ms < 1000


if __name__ == "__main__":
    test_cache_performance(Path(".pytest-cache"))
