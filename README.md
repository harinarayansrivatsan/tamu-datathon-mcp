# Loneliness Combat Engine - MCP Server

> **A mental health-focused Model Context Protocol server that detects social isolation patterns and provides AI-powered interventions for college students.**

Built for the TAMU Datathon 2025 - Build-Your-Own-MCP Challenge

## 🎯 Project Overview

In an era where college students face unprecedented levels of loneliness and social isolation, the Loneliness Combat Engine serves as an intelligent "context-aware middleware" that empowers AI assistants to detect early warning signs of social withdrawal and provide personalized, empathetic interventions.

This MCP server acts as a bridge between real-world behavioral data (calendars, music listening habits) and AI models, enabling them to understand a student's social wellness and intervene before isolation becomes severe.

### The Problem We're Solving

- **1 in 3 college students** experience significant loneliness
- Traditional mental health systems are **reactive, not proactive**
- Students often don't recognize their own social isolation patterns
- Generic wellness advice fails because **it lacks personal context**

### Our Solution

An MCP server that:
1. **Monitors behavioral signals** from Google Calendar and Spotify
2. **Detects isolation patterns** using a multi-factor risk algorithm
3. **Generates personalized interventions** via AI (Google Gemini)
4. **Recommends anxiety-appropriate events** from Meetup and Eventbrite
5. **Exposes tools to AI assistants** through the Model Context Protocol

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Assistant                         │
│              (Claude, ChatGPT, etc.)                    │
└────────────────────┬────────────────────────────────────┘
                     │ MCP Protocol
                     ▼
┌─────────────────────────────────────────────────────────┐
│           Loneliness Combat Engine (MCP Server)         │
│  ┌─────────────────┐        ┌─────────────────┐        │
│  │ Detection Agent │        │Intervention Agent│        │
│  │  - Risk Scoring │        │ - Gemini AI      │        │
│  │  - Pattern Anal.│        │ - Event Matching │        │
│  └─────────────────┘        └─────────────────┘        │
└────────────────────┬────────────────────────────────────┘
                     │ APIs & Data Sources
        ┌────────────┼────────────┬──────────────┐
        ▼            ▼            ▼              ▼
 ┌──────────┐ ┌──────────┐ ┌──────────┐  ┌──────────┐
 │  Google  │ │ Spotify  │ │  Meetup  │  │Eventbrite│
 │ Calendar │ │   API    │ │   API    │  │   API    │
 └──────────┘ └──────────┘ └──────────┘  └──────────┘
```

## 🔍 How It Works

### 1. Data Collection (with user permission)

**Google Calendar Analysis:**
- Social event frequency over time
- Declined invitation patterns
- Friend interaction networks
- Time-of-day isolation patterns

**Spotify Pattern Analysis:**
- Music mood shifts (valence/energy levels)
- Late-night listening patterns (11 PM - 4 AM)
- Genre diversity changes
- Repeat listening (rumination detection)

### 2. Risk Assessment

Our **multi-factor risk algorithm** calculates a loneliness score (0-100):

```python
Risk Score = (Calendar Signals × 0.5) + (Spotify Signals × 0.4) + (Baseline × 0.1)

Where:
- Calendar Signals: social event decline, invitation decline, contact reduction
- Spotify Signals: listening spikes, late-night activity, valence drops, repetition
- Baseline: 14-day personal behavioral baseline
```

**Risk Levels:**
- **Low (0-25)**: Healthy social engagement
- **Mild (26-50)**: Minor social withdrawal
- **Moderate (51-75)**: Concerning isolation patterns
- **High (76-100)**: Critical intervention needed

### 3. AI-Powered Intervention

Using **Google Gemini 1.5-Pro**, the system generates:
- Empathetic, personalized messages
- Anxiety-appropriate activity suggestions
- Crisis resources for high-risk cases
- Actionable next steps

### 4. Event Recommendations

Filters events from Meetup and Eventbrite based on:
- User's anxiety level (group size limits)
- Personal interests
- Location (College Station, TX)
- Event structure (lower anxiety for structured activities)

## 🛠️ MCP Tools Exposed

These tools become available to any AI assistant connected via MCP:

### Core Assessment Tools

**`assess_loneliness_risk(user_id, user_message)`**
- **Purpose:** Comprehensive risk assessment with intervention generation
- **Returns:** Risk score, risk level, behavioral patterns, personalized intervention plan
- **Example Use:** AI assistant proactively checks user's wellness during conversation

**`analyze_loneliness_risk(user_id, calendar_enabled, spotify_enabled)`**
- **Purpose:** Detailed risk analysis with specific behavioral signals
- **Returns:** Risk breakdown by data source with contributing factors
- **Example Use:** Generate detailed wellness reports

**`generate_intervention(user_id, risk_score, risk_level, interests)`**
- **Purpose:** Create personalized support strategies using Gemini AI
- **Returns:** Empathetic message, recommended activities, crisis resources
- **Example Use:** AI suggests specific events after detecting isolation

### Behavioral Analysis Tools

**`analyze_calendar_patterns(user_id, days_back)`**
- **Purpose:** Detect social withdrawal from calendar data
- **Returns:** Event frequency, decline rates, friend interaction stats
- **Example:** "Your social events dropped 60% in the last 2 weeks"

**`analyze_spotify_patterns(user_id, days_back)`**
- **Purpose:** Mood shift detection via music listening
- **Returns:** Valence/energy changes, late-night listening, genre diversity
- **Example:** "Your late-night listening increased 3x with 40% sadder music"

**`find_events(anxiety_level, interests, location)`**
- **Purpose:** Discover anxiety-appropriate social opportunities
- **Returns:** Curated events from Meetup and Eventbrite
- **Example:** For high anxiety → small groups (< 15 people), structured activities

**`get_social_event_frequency(user_id, days_back)`**
- **Purpose:** Track social engagement metrics over time
- **Returns:** Events per week, trend direction, statistical significance

**`get_mood_metrics(user_id, days_back)`**
- **Purpose:** Music-based mood analysis
- **Returns:** Average valence, energy levels, listening patterns

### MCP Resources

**`user://baselines/{user_id}`**
- Access user's 14-day behavioral baseline data
- Used for personalized anomaly detection

**`user://permissions/{user_id}`**
- Check which data sources user has authorized
- Ensures privacy-respecting operations

## 🚀 Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account (for Calendar + Gemini APIs)
- Spotify Developer account
- Meetup API key
- Eventbrite API token

### 1. Clone the Repository

```bash
git clone https://github.com/harinarayansrivatsan/tamu-datathon-mcp.git
cd tamu-datathon-mcp
```

### 2. Backend Setup (MCP Server)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Configure `.env` with your API keys:**

```env
# Google APIs
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/auth/google/callback
GEMINI_API_KEY=your_gemini_api_key

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/spotify/callback

# Event APIs
MEETUP_API_KEY=your_meetup_api_key
EVENTBRITE_API_TOKEN=your_eventbrite_token

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Database
DATABASE_URL=sqlite:///./loneliness_combat.db
```

**Initialize the database:**

```bash
python -m backend.scripts.init_db
```

**Run the MCP server:**

```bash
# Development mode
uvicorn backend.main:app --reload --port 8000

# Production mode
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Frontend Setup (Optional - for testing UI)

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Configure .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_SECRET=your_nextauth_secret
```

**Run the frontend:**

```bash
npm run dev
```

Visit `http://localhost:3000`

### 4. Connect to an AI Assistant via MCP

**For Claude Desktop:**

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "loneliness-combat": {
      "command": "uvicorn",
      "args": [
        "backend.main:app",
        "--host", "127.0.0.1",
        "--port", "8000"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your_google_client_id",
        "GEMINI_API_KEY": "your_gemini_api_key"
      }
    }
  }
}
```

**For Other MCP Clients:**

Connect to `http://127.0.0.1:8000` using the MCP protocol.

## 💡 Example Prompts & Use Cases

### Example 1: Proactive Check-In

**User to AI:** "Hey, how's my social life looking lately?"

**AI uses MCP tools:**
```
1. assess_loneliness_risk(user_id="user123", user_message="...")
2. Returns: risk_score=45, risk_level="mild"
3. Intervention: "Noticed you've declined a few invites recently..."
```

**AI Response:**
> "I've noticed you've declined a few social invitations over the past two weeks, and your calendar shows 40% fewer social events than usual. Your music listening also suggests you might be feeling a bit down (more mellow tracks late at night).
>
> Nothing alarming, but I wanted to check in! There's a small game night at the TAMU Student Center this Friday (8 people) and a coding workshop on Saturday. Either sound interesting? Sometimes small steps help."

---

### Example 2: Crisis Detection

**User to AI:** "I just don't feel like going out anymore."

**AI uses MCP tools:**
```
1. assess_loneliness_risk(user_id="user456", user_message="...")
2. Returns: risk_score=82, risk_level="high"
3. Calendar: 0 social events in 3 weeks, 5 declined invitations
4. Spotify: 3x baseline listening, valence 0.25 (very sad music)
```

**AI Response:**
> "I'm concerned about you. Your calendar shows you haven't had any social interactions in three weeks, and you've turned down multiple invitations. Your music listening patterns also suggest you're struggling emotionally.
>
> **I strongly encourage you to reach out for support:**
> - TAMU Counseling Services: (979) 845-4427
> - 988 Suicide & Crisis Lifeline: Call or text 988
> - Crisis Text Line: Text HOME to 741741
>
> You don't have to face this alone. Would you be open to talking to someone today?"

---

### Example 3: Event Matching for High Anxiety

**User to AI:** "I want to meet people but large groups make me anxious."

**AI uses MCP tools:**
```
1. analyze_loneliness_risk(user_id="user789")
2. find_events(anxiety_level="high", interests=["technology", "gaming"], location="College Station")
3. Filters to groups < 15 people, structured activities
```

**AI Response:**
> "I found some smaller, structured activities that might feel more comfortable:
>
> 1. **Tech Coffee Chat** - Thursday 3pm at Breakaway Cafe
>    - 6-8 people, casual conversation about web development
>    - Low pressure, easy to leave anytime
>
> 2. **Board Game Night** - Friday 7pm at Northgate Game Shop
>    - 10-12 people, structured gameplay (less awkward small talk)
>    - Focus on the game, not forced socializing
>
> Both have clear activities so there's no pressure to constantly chat. Want me to add one to your calendar?"

---

### Example 4: Trend Analysis

**User to AI:** "Track my social wellness over the semester."

**AI uses MCP tools:**
```
1. get_social_event_frequency(user_id="user123", days_back=90)
2. get_mood_metrics(user_id="user123", days_back=90)
3. Access user://baselines/user123 for comparison
```

**AI Response:**
> **Your Social Wellness Report (Last 90 Days):**
>
> **September (Start of Semester):**
> - Social events: 4.2/week
> - Music mood (valence): 0.68 (upbeat)
> - Risk level: Low
>
> **October (Midterms):**
> - Social events: 1.8/week (-57%)
> - Music mood: 0.45 (declining)
> - Risk level: Moderate
> - Pattern: Late-night studying correlated with social decline
>
> **November (Current):**
> - Social events: 2.5/week (improving!)
> - Music mood: 0.58 (recovering)
> - Risk level: Mild
>
> **Insight:** You tend to isolate during high-stress academic periods. Consider scheduling at least one social activity during finals week to maintain balance.

## 🎓 Why This Matters (For the Challenge)

### ⭐ Creativity & Originality (50%)

**Unique Data Sources:**
- **Spotify as a mental health signal** - Novel use of music listening patterns (valence, late-night activity, genre diversity) as mood indicators
- **Calendar friend graphs** - Constructs social networks from calendar attendees to detect relationship withdrawal
- **Multi-modal behavioral fusion** - Combines passive signals (music, calendars) rather than explicit self-reporting

**Clever Integration:**
- **Baseline-driven anomaly detection** - 14-day personalization period ensures alerts are truly unusual for each individual
- **Anxiety-appropriate filtering** - Event recommendations adapt to user's current emotional state (smaller groups when stressed)
- **Explainable risk scores** - Shows exactly which behaviors contributed to the score (transparent AI)

**Contextual Intelligence:**
- **Noise filtering** - Excludes work meetings and recurring events to focus on genuine social activity
- **Time-context awareness** - Weights late-night behavior more heavily (stronger isolation indicator)
- **Longitudinal tracking** - Detects trends over weeks, not just point-in-time snapshots

### ⚙️ Utility & Technical Merit (50%)

**Practical Value:**
- **Addresses a $79B problem** - College mental health crisis costs billions in dropout and treatment
- **Proactive, not reactive** - Intervenes before students reach crisis (when intervention is most effective)
- **Privacy-respecting** - User controls which data sources to enable; encrypted token storage
- **Accessible at scale** - AI assistants can monitor thousands of students 24/7

**Robustness:**
- **Async architecture** - FastAPI with async/await for concurrent API calls
- **Error handling** - Graceful degradation if APIs fail (uses available data sources)
- **Token encryption** - OAuth tokens stored with Fernet encryption
- **Crisis protocols** - Immediate escalation to professional resources for high-risk cases

**Efficiency:**
- **Smart summarization** - Risk scores condensed to 0-100 with clear categories
- **Caching** - Baseline data cached to reduce API calls
- **Signal vs. noise** - Filters out work meetings, recurring events, and other non-social signals
- **Lightweight MCP resources** - Only exposes essential context, not raw data dumps

## 🔐 Privacy & Ethics

This project handles sensitive mental health data. Key safeguards:

- **Explicit consent required** - Users must OAuth into each data source
- **Encrypted token storage** - All OAuth tokens encrypted at rest
- **Data minimization** - Only analyzes patterns, doesn't store message contents
- **Crisis protocols** - High-risk cases trigger immediate professional resource sharing
- **No surveillance** - Users control when and what to analyze
- **Transparency** - Risk scores show contributing factors (explainable AI)

**Note:** This is a prototype for educational purposes. Production deployment would require:
- HIPAA compliance review
- Clinical validation of risk algorithm
- Partnership with campus counseling services
- Informed consent workflows

## 📊 Technical Stack

**Backend:**
- FastAPI (async Python web framework)
- SQLAlchemy ORM + SQLite
- MCP (Model Context Protocol) v1.21.0
- Google Gemini 1.5-Pro (AI generation)
- OAuth 2.0 (Google, Spotify)
- Cryptography (Fernet encryption)

**Frontend:**
- Next.js 15 (React 19)
- NextAuth.js (authentication)
- Tailwind CSS + Radix UI
- Lucide React icons

**APIs:**
- Google Calendar API
- Spotify Web API
- Google Gemini API
- Meetup API
- Eventbrite API

**Development:**
- pytest (testing)
- black + ruff (code quality)
- mypy (type checking)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest backend/tests/test_detection_agent.py
```

## 📁 Project Structure

```
tamu-datathon-mcp/
├── backend/
│   ├── agents/
│   │   ├── detection_agent.py      # Risk assessment logic
│   │   └── intervention_agent.py   # AI intervention generation
│   ├── api/
│   │   ├── auth.py                 # OAuth flows
│   │   ├── calendar_api.py         # Google Calendar integration
│   │   ├── spotify_api.py          # Spotify integration
│   │   └── events_api.py           # Meetup/Eventbrite
│   ├── mcp_server/
│   │   └── server.py               # MCP tool definitions
│   ├── models/
│   │   └── database.py             # SQLAlchemy models
│   ├── utils/
│   │   ├── risk_calculator.py      # Risk scoring algorithm
│   │   └── baseline_tracker.py     # Behavioral baselines
│   ├── main.py                     # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx                # Landing page
│   │   └── chat/page.tsx           # AI chatbot UI
│   ├── components/
│   │   └── ui/                     # Reusable UI components
│   └── package.json
├── README.md
├── DEMO.md
└── .env.example
```

## 🤝 Contributing

This was built for the TAMU Datathon 2025 Build-Your-Own-MCP Challenge. For questions or contributions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

MIT License - see LICENSE file for details

## 🏆 Acknowledgments

- **TAMU Datathon 2025** - For the Build-Your-Own-MCP Challenge
- **Anthropic** - For the Model Context Protocol specification
- **Google** - For Gemini API and Calendar API
- **Spotify** - For their comprehensive music analytics API

## 📧 Contact

Built by [Your Name/Team Name]

- GitHub: [@harinarayansrivatsan](https://github.com/harinarayansrivatsan)
- Email: [your-email@example.com]
- Devpost: [Your Devpost Profile]

---

**Remember:** If you or someone you know is struggling with loneliness or mental health:
- **TAMU Counseling Services:** (979) 845-4427
- **988 Suicide & Crisis Lifeline:** Call or text 988
- **Crisis Text Line:** Text HOME to 741741

You're not alone. Help is available 24/7.
