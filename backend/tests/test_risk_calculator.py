"""
Test script for RiskCalculator to verify Phase 2 implementation.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from models.risk_assessment import RiskCalculator


def print_separator():
    print("\n" + "=" * 80 + "\n")


def test_scenario_1_low_risk():
    """Test Scenario 1: Low Risk - Normal behavior"""
    print("TEST SCENARIO 1: LOW RISK (Normal Behavior)")
    print_separator()

    spotify_metrics = {
        "baseline_listening_hours": 90,  # 3h/day * 30 days
        "current_listening_hours": 95,   # Slight increase
        "late_night_percentage": 10,      # Minimal late-night listening
        "baseline_valence": 0.6,
        "current_valence": 0.58,          # Slight mood change
        "repeat_listening_percentage": 15, # Normal variety
    }

    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 7,       # Slight decrease
        "declined_invitation_rate": 10,   # Minimal declines
        "declined_invitations_count": 1,
        "baseline_unique_contacts": 5,
        "current_unique_contacts": 5,     # Stable contacts
    }

    result = RiskCalculator.calculate_risk(spotify_metrics, calendar_metrics)

    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"\nFactors Breakdown:")
    print(f"  - Spotify Score: {result['factors']['spotify_score']}")
    print(f"  - Calendar Score: {result['factors']['calendar_score']}")
    print(f"  - Baseline Score: {result['factors']['baseline_score']}")
    print(f"\nExplanation:")
    for explanation in result['explanation']:
        print(f"  - {explanation}")


def test_scenario_2_mild_concern():
    """Test Scenario 2: Mild Concern - Slight withdrawal"""
    print("\n\nTEST SCENARIO 2: MILD CONCERN (Slight Withdrawal)")
    print_separator()

    spotify_metrics = {
        "baseline_listening_hours": 90,
        "current_listening_hours": 150,  # 1.67x increase
        "late_night_percentage": 45,      # Moderate late-night listening
        "baseline_valence": 0.65,
        "current_valence": 0.48,          # Notable mood decline
        "repeat_listening_percentage": 35, # Increased repeat listening
    }

    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 5,       # 37% decline
        "declined_invitation_rate": 30,   # Some declines
        "declined_invitations_count": 2,
        "baseline_unique_contacts": 5,
        "current_unique_contacts": 4,     # Slight contact decline
    }

    result = RiskCalculator.calculate_risk(spotify_metrics, calendar_metrics)

    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"\nFactors Breakdown:")
    print(f"  - Spotify Score: {result['factors']['spotify_score']}")
    print(f"  - Calendar Score: {result['factors']['calendar_score']}")
    print(f"  - Baseline Score: {result['factors']['baseline_score']}")
    print(f"\nExplanation:")
    for explanation in result['explanation']:
        print(f"  - {explanation}")


def test_scenario_3_moderate_risk():
    """Test Scenario 3: Moderate Risk - Clear isolation pattern"""
    print("\n\nTEST SCENARIO 3: MODERATE RISK (Clear Isolation Pattern)")
    print_separator()

    spotify_metrics = {
        "baseline_listening_hours": 90,
        "current_listening_hours": 200,  # 2.22x increase
        "late_night_percentage": 60,      # High late-night listening
        "baseline_valence": 0.7,
        "current_valence": 0.42,          # Significant mood decline (-0.28)
        "repeat_listening_percentage": 50, # High repeat listening (rumination)
    }

    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 2,       # 75% decline
        "declined_invitation_rate": 55,   # High decline rate
        "declined_invitations_count": 4,
        "baseline_unique_contacts": 5,
        "current_unique_contacts": 2,     # 60% contact decline
    }

    result = RiskCalculator.calculate_risk(spotify_metrics, calendar_metrics)

    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"\nFactors Breakdown:")
    print(f"  - Spotify Score: {result['factors']['spotify_score']}")
    print(f"  - Calendar Score: {result['factors']['calendar_score']}")
    print(f"  - Baseline Score: {result['factors']['baseline_score']}")
    print(f"\nExplanation:")
    for explanation in result['explanation']:
        print(f"  - {explanation}")


def test_scenario_4_high_risk():
    """Test Scenario 4: High Risk - Severe isolation"""
    print("\n\nTEST SCENARIO 4: HIGH RISK (Severe Isolation + Crisis Resources Needed)")
    print_separator()

    spotify_metrics = {
        "baseline_listening_hours": 90,
        "current_listening_hours": 280,  # 3.1x increase
        "late_night_percentage": 80,      # Very high late-night listening
        "baseline_valence": 0.72,
        "current_valence": 0.35,          # Drastic mood decline (-0.37)
        "repeat_listening_percentage": 65, # Very high repeat listening
    }

    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 0,       # 100% decline
        "declined_invitation_rate": 80,   # Very high decline rate
        "declined_invitations_count": 6,
        "baseline_unique_contacts": 5,
        "current_unique_contacts": 0,     # Complete social withdrawal
    }

    result = RiskCalculator.calculate_risk(spotify_metrics, calendar_metrics)

    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"\nFactors Breakdown:")
    print(f"  - Spotify Score: {result['factors']['spotify_score']}")
    print(f"  - Calendar Score: {result['factors']['calendar_score']}")
    print(f"  - Baseline Score: {result['factors']['baseline_score']}")
    print(f"\nExplanation:")
    for explanation in result['explanation']:
        print(f"  - {explanation}")


def test_scenario_5_demo():
    """Test Scenario 5: Demo scenario from DATATHON_STRATEGY.md"""
    print("\n\nTEST SCENARIO 5: DEMO SCENARIO (Exam Stress Example)")
    print_separator()

    spotify_metrics = {
        "baseline_listening_hours": 90,   # 15h/week baseline
        "current_listening_hours": 240,   # 40h listening spike (2.67x)
        "late_night_percentage": 65,      # 65% late-night (11pm-3am)
        "baseline_valence": 0.72,
        "current_valence": 0.45,          # Valence dropped from 0.72 to 0.45
        "repeat_listening_percentage": 45,
    }

    calendar_metrics = {
        "baseline_social_events": 8,
        "current_social_events": 2,       # Only 2 social events (baseline: 8)
        "declined_invitation_rate": 50,
        "declined_invitations_count": 4,  # 4 declined invitations
        "baseline_unique_contacts": 5,
        "current_unique_contacts": 2,     # Haven't seen Sarah in 3 weeks
    }

    result = RiskCalculator.calculate_risk(spotify_metrics, calendar_metrics)

    print(f"Risk Score: {result['score']}/100")
    print(f"Risk Level: {result['level']}")
    print(f"\nFactors Breakdown:")
    print(f"  - Spotify Score: {result['factors']['spotify_score']}")
    print(f"  - Calendar Score: {result['factors']['calendar_score']}")
    print(f"  - Baseline Score: {result['factors']['baseline_score']}")
    print(f"\nExplanation:")
    for explanation in result['explanation']:
        print(f"  - {explanation}")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RISKCALCULATOR PHASE 2 TESTING")
    print("=" * 80)

    test_scenario_1_low_risk()
    test_scenario_2_mild_concern()
    test_scenario_3_moderate_risk()
    test_scenario_4_high_risk()
    test_scenario_5_demo()

    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80 + "\n")
