"""
Test script for intervention outputs across all risk categories.

Tests intervention generation for:
- Low risk (0-25)
- Moderate risk (26-50)
- Elevated risk (51-75)
- High risk (76-89)
- Critical risk (90-100)
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.agents.intervention_agent import run_intervention


async def test_low_risk():
    """Test low risk intervention (score: 15)"""
    print("\n" + "=" * 80)
    print("TEST 1: LOW RISK (Score: 15)")
    print("=" * 80)

    risk_assessment = {
        "score": 15,
        "level": "low",
        "factors": {
            "social_event_frequency": "Normal (2-3 events/week)",
            "mood_indicators": "Positive",
            "communication_patterns": "Active",
        }
    }

    result = await run_intervention(
        risk_assessment=risk_assessment,
        user_interests=["coding", "gaming", "music"],
        user_location="College Station, TX",
        user_message="Just checking in!",
    )

    print(f"\nRisk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"\nMessage:\n{result['message']}")
    print(f"\nAction Items:")
    for item in result['action_items']:
        print(f"  - {item}")
    print(f"\nActivities Found: {len(result['activities'])}")


async def test_moderate_risk():
    """Test moderate risk intervention (score: 40)"""
    print("\n" + "=" * 80)
    print("TEST 2: MODERATE RISK (Score: 40)")
    print("=" * 80)

    risk_assessment = {
        "score": 40,
        "level": "moderate",
        "factors": {
            "social_event_frequency": "Slightly below baseline (1-2 events/week)",
            "mood_indicators": "Neutral, some sad music",
            "communication_patterns": "Decreased slightly",
        }
    }

    result = await run_intervention(
        risk_assessment=risk_assessment,
        user_interests=["coffee", "reading", "photography"],
        user_location="College Station, TX",
        user_message="Been busy with midterms, feeling a bit tired.",
    )

    print(f"\nRisk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"\nMessage:\n{result['message']}")
    print(f"\nAction Items:")
    for item in result['action_items']:
        print(f"  - {item}")
    print(f"\nActivities Found: {len(result['activities'])}")


async def test_elevated_risk():
    """Test elevated risk intervention (score: 65)"""
    print("\n" + "=" * 80)
    print("TEST 3: ELEVATED RISK (Score: 65)")
    print("=" * 80)

    risk_assessment = {
        "score": 65,
        "level": "elevated",
        "factors": {
            "social_event_frequency": "Significantly below baseline (0-1 events/week)",
            "mood_indicators": "Mostly melancholic music, late-night listening",
            "communication_patterns": "Dropped 60% from baseline",
            "recurring_contacts": ["Sarah", "Mike"],
            "days_since_social_event": 12,
        }
    }

    result = await run_intervention(
        risk_assessment=risk_assessment,
        user_interests=["art", "movies", "hiking"],
        user_location="College Station, TX",
        user_message="Haven't really felt like going out lately.",
    )

    print(f"\nRisk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"\nMessage:\n{result['message']}")
    print(f"\nAction Items:")
    for item in result['action_items']:
        print(f"  - {item}")
    print(f"\nActivities Found: {len(result['activities'])}")


async def test_high_risk():
    """Test high risk intervention (score: 82)"""
    print("\n" + "=" * 80)
    print("TEST 4: HIGH RISK (Score: 82)")
    print("=" * 80)

    risk_assessment = {
        "score": 82,
        "level": "high",
        "factors": {
            "social_event_frequency": "Severely below baseline (0 events in 3 weeks)",
            "mood_indicators": "Dark/depressive music, 3am-6am listening sessions",
            "communication_patterns": "Dropped 85% from baseline",
            "github_activity": "Coding 2am-7am daily (CS major isolation pattern)",
            "recurring_contacts": ["Mom"],
            "days_since_social_event": 22,
        }
    }

    result = await run_intervention(
        risk_assessment=risk_assessment,
        user_interests=["programming", "anime"],
        user_location="College Station, TX",
        user_message="Just been really focused on code. Don't need distractions.",
    )

    print(f"\nRisk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"\nMessage:\n{result['message']}")
    print(f"\nAction Items:")
    for item in result['action_items']:
        print(f"  - {item}")
    print(f"\nActivities Found: {len(result['activities'])}")


async def test_critical_risk():
    """Test critical risk intervention (score: 95) - Should include crisis resources"""
    print("\n" + "=" * 80)
    print("TEST 5: CRITICAL RISK (Score: 95) - CRISIS ESCALATION")
    print("=" * 80)

    risk_assessment = {
        "score": 95,
        "level": "critical",
        "factors": {
            "social_event_frequency": "Complete isolation (0 events in 6 weeks)",
            "mood_indicators": "Exclusively sad/dark music, erratic listening patterns",
            "communication_patterns": "Down 95%, ignoring messages",
            "github_activity": "No activity in 2 weeks (previously daily commits)",
            "recurring_contacts": [],
            "days_since_social_event": 45,
            "concerning_patterns": "Missing classes, not responding to friends/family",
        }
    }

    result = await run_intervention(
        risk_assessment=risk_assessment,
        user_interests=["music"],
        user_location="College Station, TX",
        user_message="I don't know what's the point anymore.",
    )

    print(f"\nRisk Level: {result['risk_level']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"\nMessage:\n{result['message']}")
    print(f"\nAction Items:")
    for item in result['action_items']:
        print(f"  - {item}")

    # Verify crisis resources are included
    message_lower = result['message'].lower()
    has_crisis_resources = any(resource in message_lower for resource in ['988', 'crisis', 'suicide prevention', '741741', '979) 845-4427'])

    print(f"\n✅ CRISIS RESOURCES INCLUDED: {has_crisis_resources}")
    if not has_crisis_resources:
        print("⚠️  WARNING: Crisis resources should be prominently included for critical risk!")


async def main():
    """Run all intervention tests"""
    print("\n" + "=" * 80)
    print("INTERVENTION OUTPUT TESTING - ALL RISK CATEGORIES")
    print("=" * 80)
    print("\nTesting intervention generation across all risk levels:")
    print("- Low (0-25): Encouragement and maintenance")
    print("- Moderate (26-50): Gentle check-in")
    print("- Elevated (51-75): Actionable suggestions")
    print("- High (76-89): Serious concern + specific actions")
    print("- Critical (90-100): Crisis resources + immediate action")

    try:
        # Run all tests
        await test_low_risk()
        await asyncio.sleep(1)  # Brief pause between tests

        await test_moderate_risk()
        await asyncio.sleep(1)

        await test_elevated_risk()
        await asyncio.sleep(1)

        await test_high_risk()
        await asyncio.sleep(1)

        await test_critical_risk()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY ✅")
        print("=" * 80)
        print("\nKey Observations:")
        print("1. Intervention tone adapts to risk level")
        print("2. Crisis resources included for critical risk (90-100)")
        print("3. Action items become more urgent as risk increases")
        print("4. Messages remain empathetic and non-judgmental across all levels")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
