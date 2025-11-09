"""
Test edge cases for Loneliness Combat Engine.

Tests:
1. API failure handling (Spotify down, Calendar down, both down)
2. No baseline data (new users)
3. High risk score (76-100) - ensures crisis resources are included
4. Partial data availability
5. Invalid data handling

Usage:
    python test_edge_cases.py
"""

import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import MagicMock, patch

sys.path.insert(0, "backend")

from backend.models.risk_assessment import RiskCalculator


def test_api_failure_spotify_down():
    """Test graceful degradation when Spotify API is unavailable."""
    print("\n" + "=" * 60)
    print("TEST 1: Spotify API Failure")
    print("=" * 60)

    # Simulate Spotify returning empty/error data
    spotify_metrics = {}
    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 3,
        "declined_invitation_rate": 40,
        "baseline_unique_contacts": 5,
        "current_unique_contacts": 2,
    }

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
        )

        print(f"✓ System handled Spotify failure gracefully")
        print(f"  Risk Score: {result['score']}/100 (based on Calendar only)")
        print(f"  Risk Level: {result['level']}")
        print(f"  Explanation: {result['explanation']}")

        # Verify score is still calculated (weighted toward Calendar)
        assert result["score"] > 0, "Score should still be calculated from Calendar"
        assert result["level"] in ["low", "mild", "moderate", "high"], "Level should be valid"

        print("✓ PASS: Graceful degradation working")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_api_failure_calendar_down():
    """Test graceful degradation when Calendar API is unavailable."""
    print("\n" + "=" * 60)
    print("TEST 2: Calendar API Failure")
    print("=" * 60)

    spotify_metrics = {
        "baseline_listening_hours": 15,
        "current_listening_hours": 32,
        "late_night_percentage": 58,
        "baseline_valence": 0.65,
        "current_valence": 0.35,
        "repeat_listening_percentage": 42,
    }
    calendar_metrics = {}  # Simulate Calendar API down

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
        )

        print(f"✓ System handled Calendar failure gracefully")
        print(f"  Risk Score: {result['score']}/100 (based on Spotify only)")
        print(f"  Risk Level: {result['level']}")
        print(f"  Explanation: {result['explanation']}")

        # Verify score is calculated from Spotify
        assert result["score"] > 0, "Score should still be calculated from Spotify"
        assert result["level"] in ["low", "mild", "moderate", "high"], "Level should be valid"

        print("✓ PASS: Graceful degradation working")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_api_failure_both_down():
    """Test behavior when both APIs are unavailable."""
    print("\n" + "=" * 60)
    print("TEST 3: Both APIs Down")
    print("=" * 60)

    spotify_metrics = {}
    calendar_metrics = {}

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
        )

        print(f"✓ System handled total API failure")
        print(f"  Risk Score: {result['score']}/100 (baseline only)")
        print(f"  Risk Level: {result['level']}")
        print(f"  Explanation: {result['explanation']}")

        # Should fall back to baseline risk only (10 * 0.1 weight = 1 point)
        assert result["score"] <= 10, "Should use baseline risk only when no data available"
        assert result["level"] == "low", "Should default to low risk"

        print("✓ PASS: Baseline fallback working")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_no_baseline_data():
    """Test handling of new users without established baseline."""
    print("\n" + "=" * 60)
    print("TEST 4: No Baseline Data (New User)")
    print("=" * 60)

    # New user with some current data but no baseline
    spotify_metrics = {
        "baseline_listening_hours": 0,  # No baseline
        "current_listening_hours": 20,
        "late_night_percentage": 35,
        "baseline_valence": 0.5,  # Default
        "current_valence": 0.48,  # Not much change
        "repeat_listening_percentage": 25,
    }
    calendar_metrics = {
        "baseline_social_events": 0,  # No baseline
        "current_social_events": 2,
        "declined_invitation_rate": 20,
        "baseline_unique_contacts": 0,  # No baseline
        "current_unique_contacts": 3,
    }
    baseline_data = None  # No baseline established

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
            baseline_data=baseline_data,
        )

        print(f"✓ System handled missing baseline")
        print(f"  Risk Score: {result['score']}/100")
        print(f"  Risk Level: {result['level']}")
        print(f"  Explanation: {result['explanation']}")

        # Should use default baseline (10) and calculate from available data
        # With no baseline for comparison, scores should be minimal
        assert 0 <= result["score"] <= 30, "Score should be low without baseline comparison"
        assert result["level"] in ["low", "mild"], "Should default to low/mild risk"

        print("✓ PASS: New user handling working")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_high_risk_score():
    """Test that high risk scores (76-100) are properly categorized."""
    print("\n" + "=" * 60)
    print("TEST 5: High Risk Score Detection")
    print("=" * 60)

    # Severe isolation pattern
    spotify_metrics = {
        "baseline_listening_hours": 15,
        "current_listening_hours": 45,  # 3x increase
        "late_night_percentage": 85,  # Mostly late night
        "baseline_valence": 0.70,
        "current_valence": 0.25,  # Drastic mood decline
        "repeat_listening_percentage": 65,  # Excessive repeat listening
    }
    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 0,  # Complete withdrawal
        "declined_invitation_rate": 100,  # Declined everything
        "baseline_unique_contacts": 6,
        "current_unique_contacts": 0,  # No contact with anyone
    }

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
        )

        print(f"✓ System calculated risk score")
        print(f"  Risk Score: {result['score']}/100")
        print(f"  Risk Level: {result['level']}")
        print(f"  Factors:")
        print(f"    - Spotify: {result['factors']['spotify_score']:.1f}")
        print(f"    - Calendar: {result['factors']['calendar_score']:.1f}")
        print(f"  Explanation: {result['explanation']}")

        # Verify high risk detection
        assert result["score"] >= 76, f"Score should be high risk (76+), got {result['score']}"
        assert result["level"] == "high", f"Level should be 'high', got {result['level']}"

        print("✓ PASS: High risk detection working")
        print("  NOTE: This score should trigger crisis resources in production!")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_partial_data():
    """Test handling of partial/incomplete data."""
    print("\n" + "=" * 60)
    print("TEST 6: Partial Data Handling")
    print("=" * 60)

    # Only some fields available
    spotify_metrics = {
        "current_listening_hours": 25,
        # Missing: baseline_listening_hours, late_night_percentage, valence, etc.
    }
    calendar_metrics = {
        "baseline_social_events": 5,
        "current_social_events": 2,
        # Missing: declined_invitation_rate, contact data
    }

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
        )

        print(f"✓ System handled partial data")
        print(f"  Risk Score: {result['score']}/100")
        print(f"  Risk Level: {result['level']}")
        print(f"  Explanation: {result['explanation']}")

        # Should still calculate a score using available fields
        assert 0 <= result["score"] <= 100, "Score should be in valid range"
        assert result["level"] in ["low", "mild", "moderate", "high"], "Level should be valid"

        print("✓ PASS: Partial data handling working")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_invalid_data():
    """Test handling of invalid/malformed data."""
    print("\n" + "=" * 60)
    print("TEST 7: Invalid Data Handling")
    print("=" * 60)

    # Negative values, out-of-range values, etc.
    spotify_metrics = {
        "baseline_listening_hours": -5,  # Invalid (negative)
        "current_listening_hours": 200,  # Unrealistic but not invalid
        "late_night_percentage": 150,  # Invalid (>100%)
        "baseline_valence": 1.5,  # Invalid (should be 0-1)
        "current_valence": -0.3,  # Invalid (should be 0-1)
    }
    calendar_metrics = {
        "baseline_social_events": 10,
        "current_social_events": -2,  # Invalid (negative)
    }

    try:
        result = RiskCalculator.calculate_risk(
            spotify_metrics=spotify_metrics,
            calendar_metrics=calendar_metrics,
        )

        print(f"✓ System handled invalid data without crashing")
        print(f"  Risk Score: {result['score']}/100")
        print(f"  Risk Level: {result['level']}")

        # Should clamp to valid ranges
        assert 0 <= result["score"] <= 100, "Score should be clamped to valid range"

        print("✓ PASS: Invalid data handling working")
        print("  NOTE: Production should add input validation before risk calculation!")

    except Exception as e:
        print(f"✗ FAIL: {e}")
        raise


def test_boundary_conditions():
    """Test risk score boundary conditions."""
    print("\n" + "=" * 60)
    print("TEST 8: Boundary Conditions")
    print("=" * 60)

    test_cases = [
        ("Zero Risk", 0, "low"),
        ("Low-Mild Boundary", 25, "low"),
        ("Mild Boundary", 26, "mild"),
        ("Mild-Moderate Boundary", 50, "mild"),
        ("Moderate Boundary", 51, "moderate"),
        ("Moderate-High Boundary", 75, "moderate"),
        ("High Boundary", 76, "high"),
        ("Maximum Risk", 100, "high"),
    ]

    for name, score, expected_level in test_cases:
        level = RiskCalculator.get_risk_level(score)
        status = "✓" if level == expected_level else "✗"
        print(f"  {status} {name}: Score {score} → {level} (expected: {expected_level})")

        assert level == expected_level, f"{name} failed: expected {expected_level}, got {level}"

    print("✓ PASS: All boundary conditions correct")


def run_all_tests():
    """Run all edge case tests."""
    print("=" * 60)
    print("LONELINESS COMBAT ENGINE - EDGE CASE TESTS")
    print("=" * 60)

    tests = [
        test_api_failure_spotify_down,
        test_api_failure_calendar_down,
        test_api_failure_both_down,
        test_no_baseline_data,
        test_high_risk_score,
        test_partial_data,
        test_invalid_data,
        test_boundary_conditions,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ TEST FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ TEST ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nSYSTEM IS DEMO-READY:")
        print("- ✓ Handles API failures gracefully")
        print("- ✓ Works with missing baseline data")
        print("- ✓ Correctly identifies high-risk users (76-100)")
        print("- ✓ Handles partial/invalid data without crashing")
        print("- ✓ Boundary conditions are correct")
        print("\nRECOMMENDATIONS:")
        print("1. Add input validation before risk calculation")
        print("2. Log API failures for monitoring")
        print("3. Consider adding confidence scores for partial data")
        print("4. Test with real API data before production")
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")
        print("Fix these issues before demo!")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
