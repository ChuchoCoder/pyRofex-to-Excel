"""
Test symbol display formatting for options vs regular securities.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from pyRofex_To_Excel.utils.helpers import clean_symbol_for_display


def run_symbol_display_checks() -> bool:
    """Run symbol display checks and return True when all cases pass."""
    
    print("=" * 70)
    print("SYMBOL DISPLAY FORMATTING TEST")
    print("=" * 70)
    
    test_cases = [
        # (symbol, is_option, expected_result, description)
        ("MERV - XMEV - GGAL - 24hs", False, "GGAL - 24hs", "Regular stock keeps suffix"),
        ("MERV - XMEV - GFGV38566O - 24hs", True, "GFGV38566O", "Option removes - 24hs suffix"),
        ("MERV - XMEV - GFGV38566O - CI", True, "GFGV38566O", "Option removes - CI suffix"),
        ("MERV - XMEV - GFGC7000AG - CI", True, "GFGC7000AG", "Option removes - CI suffix"),
        ("MERV - XMEV - GFGV88566O - 24hs", True, "GFGV88566O", "Option removes suffix"),
        ("MERV - XMEV - PESOS - 3D", False, "PESOS - 3D", "Caucion keeps suffix"),
        ("MERV - XMEV - COME - 24hs", False, "COME - 24hs", "Stock keeps suffix"),
        ("MERV - XMEV - YPFD - 48hs", False, "YPFD - 48hs", "Stock with 48hs keeps suffix"),
        ("MERV - XMEV - GFGC47566O - 24hs", True, "GFGC47566O", "Option removes suffix"),
        ("MERV - XMEV - GFGC47566O - CI", True, "GFGC47566O", "Option removes - CI suffix"),
        ("GGAL - 24hs", False, "GGAL - 24hs", "Already clean symbol unchanged"),
        ("GFGV38566O", True, "GFGV38566O", "Already clean option unchanged"),
    ]
    
    print("\n🔍 Testing Symbol Display Formatting:")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for symbol, is_option, expected, description in test_cases:
        result = clean_symbol_for_display(symbol, is_option=is_option)
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        print(f"{status} | {description}")
        print(f"       Input:    {symbol}")
        print(f"       Expected: {expected}")
        print(f"       Got:      {result}")
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    
    if failed == 0:
        print("✅ All tests passed!")
    else:
        print(f"❌ {failed} tests failed")
    
    print("=" * 70)
    
    return failed == 0


def test_symbol_display_formatting():
    """Test that symbol display formatting works correctly for options and securities."""
    assert run_symbol_display_checks()


if __name__ == "__main__":
    success = run_symbol_display_checks()
    sys.exit(0 if success else 1)
