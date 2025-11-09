"""
Seed test data for Loneliness Combat Engine demo.

Creates realistic test users with different isolation patterns:
1. Low Risk - Active social life
2. Moderate Risk - Declining social activity
3. High Risk - Severe isolation pattern requiring crisis resources

Usage:
    python seed_test_data.py
"""

import sys
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

# Add backend to path
sys.path.insert(0, "backend")

from backend.models.database import SessionLocal, init_db
from backend.models.user import User
from backend.models.baseline import Baseline
from backend.models.permissions import Permission
from backend.models.risk_assessment import RiskAssessment
from backend.models.interventions import Intervention


def clear_test_data(db: Session):
    """Clear existing test data."""
    print("Clearing existing test data...")

    # Delete in reverse dependency order
    db.query(Intervention).delete()
    db.query(RiskAssessment).delete()
    db.query(Baseline).delete()
    db.query(Permission).delete()
    db.query(User).delete()

    db.commit()
    print("✓ Test data cleared")


def create_low_risk_user(db: Session) -> User:
    """
    Create a low-risk user with healthy social patterns.

    Profile: Active student, regular social events, positive mood
    """
    print("\nCreating low-risk user (healthy social life)...")

    user = User(
        email="healthy.student@tamu.edu",
        name="Alex Chen",
        google_id="test_google_id_001",
        interests="hiking, board games, photography, coffee",
        location="College Station, TX",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Permissions (all enabled)
    permission = Permission(
        user_id=user.id,
        calendar_enabled="true",
        spotify_enabled="true",
        github_enabled="false",
        weather_enabled="true",
        discord_enabled="false",
    )
    db.add(permission)

    # Baseline (established 2 weeks ago)
    baseline = Baseline(
        user_id=user.id,
        social_event_frequency=3.5,  # ~3-4 events per week
        social_event_types=["study_group", "dinner", "game_night", "workout"],
        mood_baseline={
            "valence": 0.68,
            "energy": 0.72,
            "listening_hours_per_week": 14,
        },
        music_patterns={
            "top_genres": ["indie", "pop", "electronic"],
            "late_night_percentage": 15,
        },
        communication_frequency=45.0,  # 45 messages per day
        is_established="true",
        observation_start=datetime.utcnow() - timedelta(days=21),
        established_at=datetime.utcnow() - timedelta(days=7),
    )
    db.add(baseline)

    # Recent risk assessment (low risk)
    risk = RiskAssessment(
        user_id=user.id,
        score=18,
        level="low",
        factors={
            "spotify_score": 12.5,
            "calendar_score": 15.0,
            "baseline_score": 10.0,
            "total_score": 18.3,
        },
        assessed_at=datetime.utcnow() - timedelta(hours=2),
    )
    db.add(risk)

    db.commit()
    print(f"✓ Created low-risk user: {user.email} (Risk: {risk.score})")
    return user


def create_moderate_risk_user(db: Session) -> User:
    """
    Create a moderate-risk user showing isolation patterns.

    Profile: Transfer student, declining social activity, mood shift
    """
    print("\nCreating moderate-risk user (isolation pattern)...")

    user = User(
        email="isolated.student@tamu.edu",
        name="Jordan Kim",
        google_id="test_google_id_002",
        interests="coding, anime, guitar, reading",
        location="College Station, TX",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Permissions (Calendar + Spotify enabled)
    permission = Permission(
        user_id=user.id,
        calendar_enabled="true",
        spotify_enabled="true",
        github_enabled="false",
        weather_enabled="false",
        discord_enabled="false",
    )
    db.add(permission)

    # Baseline (established - shows previous healthy behavior)
    baseline = Baseline(
        user_id=user.id,
        social_event_frequency=2.5,  # Used to be 2-3 events per week
        social_event_types=["club_meeting", "dinner", "movie"],
        mood_baseline={
            "valence": 0.58,
            "energy": 0.65,
            "listening_hours_per_week": 18,
        },
        music_patterns={
            "top_genres": ["lo-fi", "indie", "soundtrack"],
            "late_night_percentage": 22,
        },
        communication_frequency=28.0,
        is_established="true",
        observation_start=datetime.utcnow() - timedelta(days=28),
        established_at=datetime.utcnow() - timedelta(days=14),
    )
    db.add(baseline)

    # Recent risk assessment (moderate risk)
    risk = RiskAssessment(
        user_id=user.id,
        score=62,
        level="moderate",
        factors={
            "spotify_score": 58.5,
            "calendar_score": 65.0,
            "baseline_score": 10.0,
            "total_score": 62.2,
        },
        assessed_at=datetime.utcnow() - timedelta(hours=1),
    )
    db.add(risk)

    # Previous intervention (not yet responded)
    intervention = Intervention(
        user_id=user.id,
        risk_score=60,
        suggestion=(
            "I noticed you've been skipping some social events lately. "
            "There's a low-key board game night at MSC this Friday - "
            "structured activities like this can be easier than just 'hanging out'. "
            "Want me to add it to your calendar?"
        ),
        event_id="tamu_board_game_001",
        event_source="tamu",
        created_at=datetime.utcnow() - timedelta(days=2),
    )
    db.add(intervention)

    db.commit()
    print(f"✓ Created moderate-risk user: {user.email} (Risk: {risk.score})")
    return user


def create_high_risk_user(db: Session) -> User:
    """
    Create a high-risk user requiring crisis resources.

    Profile: Post-breakup, severe social withdrawal, mood decline
    """
    print("\nCreating high-risk user (severe isolation)...")

    user = User(
        email="crisis.student@tamu.edu",
        name="Taylor Martinez",
        google_id="test_google_id_003",
        interests="music, writing, art",
        location="College Station, TX",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Permissions (all enabled for maximum context)
    permission = Permission(
        user_id=user.id,
        calendar_enabled="true",
        spotify_enabled="true",
        github_enabled="true",
        weather_enabled="true",
        discord_enabled="false",
    )
    db.add(permission)

    # Baseline (established - shows drastic decline from baseline)
    baseline = Baseline(
        user_id=user.id,
        social_event_frequency=4.0,  # Was very social
        social_event_types=["dinner", "party", "study_group", "concert", "sports"],
        mood_baseline={
            "valence": 0.72,
            "energy": 0.70,
            "listening_hours_per_week": 16,
        },
        music_patterns={
            "top_genres": ["pop", "rock", "dance"],
            "late_night_percentage": 18,
        },
        communication_frequency=65.0,
        is_established="true",
        observation_start=datetime.utcnow() - timedelta(days=35),
        established_at=datetime.utcnow() - timedelta(days=21),
    )
    db.add(baseline)

    # Recent risk assessment (high risk - triggers crisis resources)
    risk = RiskAssessment(
        user_id=user.id,
        score=82,
        level="high",
        factors={
            "spotify_score": 88.5,
            "calendar_score": 85.0,
            "baseline_score": 10.0,
            "total_score": 82.4,
        },
        assessed_at=datetime.utcnow() - timedelta(minutes=30),
    )
    db.add(risk)

    # Multiple interventions (escalating)
    interventions = [
        Intervention(
            user_id=user.id,
            risk_score=68,
            suggestion=(
                "Hey, I've noticed you canceled 3 social events this week. "
                "No judgment - sometimes we need space. But I also see you used to "
                "really enjoy hanging out with people. Want to talk about what's going on?"
            ),
            created_at=datetime.utcnow() - timedelta(days=7),
            accepted="false",
            responded_at=datetime.utcnow() - timedelta(days=6),
        ),
        Intervention(
            user_id=user.id,
            risk_score=75,
            suggestion=(
                "I'm seeing some patterns that concern me - you're listening to a lot more "
                "sad music late at night, and you've stopped seeing friends. "
                "This might be a good time to talk to someone who can help. "
                "TAMU Counseling Services: 979-845-4427 (free for students)"
            ),
            created_at=datetime.utcnow() - timedelta(days=3),
        ),
    ]
    for intervention in interventions:
        db.add(intervention)

    db.commit()
    print(f"✓ Created high-risk user: {user.email} (Risk: {risk.score})")
    return user


def create_no_baseline_user(db: Session) -> User:
    """
    Create a new user without baseline data.

    Tests edge case: system uses defaults when no baseline exists
    """
    print("\nCreating new user (no baseline)...")

    user = User(
        email="new.student@tamu.edu",
        name="Sam Rodriguez",
        google_id="test_google_id_004",
        interests="soccer, cooking",
        location="College Station, TX",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Permissions (only Calendar enabled)
    permission = Permission(
        user_id=user.id,
        calendar_enabled="true",
        spotify_enabled="false",
        github_enabled="false",
        weather_enabled="false",
        discord_enabled="false",
    )
    db.add(permission)

    # Baseline (not yet established)
    baseline = Baseline(
        user_id=user.id,
        is_established="false",
        observation_start=datetime.utcnow() - timedelta(days=3),
    )
    db.add(baseline)

    db.commit()
    print(f"✓ Created new user (no baseline): {user.email}")
    return user


def print_summary(db: Session):
    """Print summary of seeded data."""
    print("\n" + "=" * 60)
    print("TEST DATA SUMMARY")
    print("=" * 60)

    users = db.query(User).all()
    print(f"\nTotal users: {len(users)}")

    for user in users:
        risk = db.query(RiskAssessment).filter(
            RiskAssessment.user_id == user.id
        ).order_by(RiskAssessment.assessed_at.desc()).first()

        baseline = db.query(Baseline).filter(Baseline.user_id == user.id).first()

        print(f"\n{user.name} ({user.email})")
        print(f"  Risk Score: {risk.score if risk else 'N/A'} ({risk.level if risk else 'N/A'})")
        print(f"  Baseline: {'Established' if baseline and baseline.is_established == 'true' else 'Not established'}")

        interventions = db.query(Intervention).filter(
            Intervention.user_id == user.id
        ).count()
        print(f"  Interventions: {interventions}")

    print("\n" + "=" * 60)
    print("Demo-ready users created successfully!")
    print("=" * 60)

    print("\nRECOMMENDED DEMO FLOW:")
    print("1. Use 'isolated.student@tamu.edu' for main demo")
    print("   - Shows moderate risk with clear isolation pattern")
    print("   - Has baseline for comparison")
    print("   - Demonstrates personalized intervention")
    print("\n2. Use 'crisis.student@tamu.edu' to show crisis escalation")
    print("   - Demonstrates high-risk detection")
    print("   - Shows crisis resource inclusion")
    print("\n3. Use 'healthy.student@tamu.edu' to show low risk")
    print("   - Demonstrates system doesn't over-diagnose")
    print("\n4. Use 'new.student@tamu.edu' to test edge cases")
    print("   - Tests graceful handling of missing baseline")


def main():
    """Main seeding function."""
    print("=" * 60)
    print("LONELINESS COMBAT ENGINE - TEST DATA SEEDER")
    print("=" * 60)

    # Initialize database
    print("\nInitializing database...")
    init_db()
    print("✓ Database initialized")

    # Get database session
    db = SessionLocal()

    try:
        # Clear existing test data
        clear_test_data(db)

        # Create test users
        create_low_risk_user(db)
        create_moderate_risk_user(db)
        create_high_risk_user(db)
        create_no_baseline_user(db)

        # Print summary
        print_summary(db)

    except Exception as e:
        print(f"\n❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
