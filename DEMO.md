# Loneliness Combat Engine - Demo Video Script

**Duration:** 3-5 minutes
**Goal:** Show how an MCP server can detect social isolation and provide AI-powered interventions

---

## 🎬 Opening (0:00 - 0:30)

### Visual
- Show title card: "Loneliness Combat Engine"
- Subtitle: "An MCP Server for Mental Health"
- Quick stats overlay: "1 in 3 college students experience significant loneliness"

### Script

> "Hey everyone! For the TAMU Datathon MCP Challenge, I built the **Loneliness Combat Engine** - an MCP server that helps AI assistants detect when college students are becoming socially isolated... and intervene before it becomes a crisis.
>
> The challenge was to build a 'smart context engine' that makes AI more personal and aware. I chose to tackle one of the biggest problems on college campuses: **loneliness**."

---

## 🧠 The Problem (0:30 - 1:00)

### Visual
- Split screen: lonely student on one side, generic mental health advice on the other
- Animated diagram showing "reactive" vs "proactive" care

### Script

> "Here's the issue: Traditional mental health support is **reactive**. Students have to recognize they're struggling, ask for help, and wait for an appointment. By then, they're already in crisis.
>
> But what if an AI assistant could **proactively detect** early warning signs by analyzing everyday behavioral data - like your calendar and music listening habits - and provide personalized support **before** things get bad?"

---

## 🏗️ The Solution (1:00 - 2:00)

### Visual
- Animated architecture diagram (show data flow):
  - Google Calendar → MCP Server → Risk Analysis
  - Spotify → MCP Server → Risk Analysis
  - Risk Analysis → Gemini AI → Personalized Intervention
  - Final output → AI Assistant (Claude/ChatGPT)

### Script

> "That's what my MCP server does. Here's how it works:
>
> **Step 1: Data Collection** (with user permission)
> - I connect to **Google Calendar** to track social event frequency, declined invitations, and friend interaction patterns
> - I analyze **Spotify listening habits** - because research shows late-night music listening and mood shifts (like listening to sadder songs) are strong indicators of emotional distress
>
> **Step 2: Risk Assessment**
> - My detection agent calculates a 'loneliness risk score' from 0 to 100 using a multi-factor algorithm
> - It combines calendar signals (50% weight), Spotify signals (40% weight), and personal baseline behavior (10% weight)
> - The system learns each student's 'normal' behavior over 14 days, so alerts are truly unusual for *that individual*
>
> **Step 3: AI-Powered Intervention**
> - Using **Google Gemini**, my intervention agent generates empathetic, personalized messages
> - It recommends anxiety-appropriate activities - like small group events for students with high social anxiety
> - For high-risk cases, it provides immediate crisis resources
>
> **Step 4: Event Recommendations**
> - The server connects to **Meetup** and **Eventbrite** APIs to find real local events in College Station
> - Events are filtered based on the student's anxiety level, interests, and current emotional state"

---

## 💻 Live Demo (2:00 - 3:30)

### Demo Scenario 1: Mild Risk Detection

#### Visual
- Screen recording of AI chat interface
- Show user typing: "Hey, how am I doing socially lately?"

#### Script

> "Let me show you this in action. I'll connect an AI assistant to my MCP server.
>
> **[User asks: 'Hey, how am I doing socially lately?']**
>
> Behind the scenes, the AI calls my MCP tool `assess_loneliness_risk()`. Watch what happens..."

#### Visual
- Show MCP tool call (optional: debug view showing API calls)
- Display results:
  - Risk Score: 45 (Mild)
  - Calendar: 40% fewer social events than baseline
  - Spotify: Increased late-night listening, valence drop from 0.7 to 0.4

#### Script

> **[AI Response]:**
> 'I've noticed you've declined a few social invitations over the past two weeks, and your calendar shows 40% fewer social events than usual. Your music listening also suggests you might be feeling a bit down - more mellow tracks late at night.
>
> Nothing alarming, but I wanted to check in! There's a small game night at the TAMU Student Center this Friday (8 people) and a coding workshop on Saturday. Either sound interesting?'
>
> **See how the AI is being proactive?** It detected a subtle pattern, acknowledged it empathetically, and suggested specific events matched to the user's comfort level."

---

### Demo Scenario 2: High Risk / Crisis Detection

#### Visual
- New chat window
- User message: "I just don't feel like going out anymore"

#### Script

> "Now let me show you a more serious case. Same user, but three weeks later...
>
> **[User says: 'I just don't feel like going out anymore']**
>
> The MCP server detects this is much more serious:"

#### Visual
- Show MCP results:
  - Risk Score: 82 (High/Critical)
  - Calendar: 0 social events in 21 days, 5 declined invitations
  - Spotify: 3x baseline listening, valence 0.25 (very sad music)

#### Script

> **[AI Response]:**
> 'I'm concerned about you. Your calendar shows you haven't had any social interactions in three weeks, and you've turned down multiple invitations. Your music listening patterns also suggest you're struggling emotionally.
>
> **I strongly encourage you to reach out for support:**
> - TAMU Counseling Services: (979) 845-4427
> - 988 Suicide & Crisis Lifeline
> - Crisis Text Line: Text HOME to 741741
>
> You don't have to face this alone.'
>
> **This is critical:** For high-risk cases, the server immediately provides professional resources. This is about **early intervention**, not replacing therapists."

---

## 🔧 Technical Highlights (3:30 - 4:00)

### Visual
- Quick code snippets or architecture diagram
- List of MCP tools exposed

#### Script

> "From a technical perspective, this server exposes **8 MCP tools** that any AI assistant can use:
> - `assess_loneliness_risk` - comprehensive assessment
> - `analyze_calendar_patterns` - social withdrawal detection
> - `analyze_spotify_patterns` - mood shift analysis
> - `find_events` - anxiety-appropriate event discovery
> - ...and more
>
> It also provides **MCP resources** like user baselines and permissions - so AI assistants can access the right context at the right time.
>
> The backend uses **FastAPI** for async performance, **SQLAlchemy** for data persistence, and **Google Gemini** for empathetic message generation. Everything is encrypted and privacy-respecting - users control which data sources to enable."

---

## 🎯 Why This Matters for the Challenge (4:00 - 4:30)

### Visual
- Text overlay: Challenge criteria
  - ✓ Unique data sources (Spotify mood analysis, calendar friend graphs)
  - ✓ Clever integration (multi-modal behavioral fusion)
  - ✓ Contextual intelligence (baseline-driven anomaly detection)
  - ✓ Practical value (addresses $79B college mental health crisis)
  - ✓ Robustness (async, error handling, encryption)

### Script

> "Why does this meet the challenge criteria?
>
> **Creativity:**
> - I'm using **Spotify as a mental health signal** - analyzing valence, energy, and late-night listening patterns
> - My **calendar friend graph** detects not just fewer events, but *which relationships* are declining
> - The system is **personalized** - it learns your baseline over 14 days so alerts are truly unusual for *you*
>
> **Utility:**
> - This addresses a **real, massive problem** - college mental health issues cost billions in dropout rates and treatment
> - It's **proactive, not reactive** - catching students before they reach crisis
> - It's **scalable** - one MCP server can support thousands of students through their AI assistants
> - And it's **privacy-respecting** with explicit consent and encrypted storage"

---

## 🚀 Future Vision (4:30 - 5:00)

### Visual
- Mockup of expanded features
- Campus counseling integration diagram

### Script

> "This is just the beginning. Imagine if this integrated with:
> - **Campus counseling services** - automatic warm handoffs for high-risk students
> - **GitHub API** - detecting late-night coding marathons (another isolation signal)
> - **Fitness trackers** - correlating physical activity with mood
> - **Course management systems** - noticing when students stop attending study groups
>
> The Model Context Protocol makes all of this possible. By giving AI assistants **rich, personal context**, we can build tools that truly understand and support students' mental health."

---

## 🎬 Closing (5:00 - 5:15)

### Visual
- Return to title card
- Show GitHub repo + QR code
- Contact info

### Script

> "Thanks for watching! The code is open source on GitHub - check it out, try it yourself, and let me know what you think.
>
> And remember: **If you or someone you know is struggling, help is available 24/7.** You're not alone.
>
> 988 Suicide & Crisis Lifeline - call or text anytime."

---

## 🎥 Production Tips

### Before Recording

1. **Test all demos** - Make sure MCP server is running and responses are fast
2. **Prepare sample data** - Seed database with realistic user patterns
3. **Clean up UI** - Ensure chat interface looks polished
4. **Script practice** - Read through 2-3 times for smooth delivery

### During Recording

**Visual Best Practices:**
- **Screen resolution:** 1920x1080 minimum
- **Font size:** Increase terminal/editor font to 18-20pt for visibility
- **Window management:** Use split-screen for architecture diagrams + live demo
- **Annotations:** Add arrows/highlights in post-production to emphasize key points

**Audio Best Practices:**
- Use a decent microphone (even smartphone earbuds are better than laptop mic)
- Record in a quiet room
- Speak clearly and slightly slower than normal conversation
- Add background music at 10-15% volume (royalty-free)

**Pacing:**
- **Keep it moving** - 3-5 minutes goes fast
- **Show, don't just tell** - Prioritize live demos over talking heads
- **Hook early** - Open with the problem + quick solution preview in first 30 seconds

### Editing Checklist

- [ ] Add title cards for each section
- [ ] Include text overlays for key stats (e.g., "Risk Score: 82")
- [ ] Highlight MCP tool calls in demo (zoom or box)
- [ ] Add transitions between sections (simple fade is fine)
- [ ] Include captions/subtitles (accessibility + engagement)
- [ ] Background music (subtle, not distracting)
- [ ] End screen with GitHub link + call-to-action

---

## 📋 Quick Reference: Key Talking Points

### What Makes This Creative?
1. **Spotify as mental health signal** (novel data source)
2. **Calendar friend graphs** (relationship-level analysis)
3. **Baseline-driven detection** (personalized to each student)
4. **Multi-modal fusion** (calendar + music + more)

### What Makes This Useful?
1. **Proactive, not reactive** (early intervention)
2. **Privacy-respecting** (explicit consent, encryption)
3. **Scalable** (one server → thousands of students)
4. **Actionable** (specific events, not generic advice)

### Technical Highlights
1. **8 MCP tools + 2 resources** exposed to AI
2. **FastAPI async** for concurrent API calls
3. **Google Gemini** for empathetic generation
4. **Multi-factor risk algorithm** with explainable scores
5. **OAuth 2.0 + Fernet encryption** for security

### The "Wow" Moment
- Show the AI detecting a pattern the user didn't even notice themselves
- Demonstrate personalized event recommendations (small groups for high anxiety)
- Reveal the crisis detection with immediate professional resources

---

## 🎤 Sample Opening Lines (Pick Your Style)

**Dramatic:**
> "Right now, on college campuses across America, students are sitting alone in their dorm rooms, convincing themselves they're fine. But their calendars tell a different story. And so does their Spotify. Let me show you what I mean..."

**Casual:**
> "Hey! So for this datathon, I wanted to tackle a problem I've seen firsthand in college: it's really easy to become isolated without even realizing it. So I built an MCP server that basically gives AI assistants a 'social wellness radar'..."

**Technical:**
> "The Model Context Protocol challenge asked us to build a smart context engine. I built one that turns everyday behavioral data - calendars, music listening - into mental health insights. Here's how it works..."

**Problem-First:**
> "Imagine you're a college student. You've declined a few social invites because you're busy. You're listening to music alone at 2 AM because you can't sleep. These seem normal, right? But together, they're early warning signs of serious isolation. That's what my MCP server detects..."

---

## 📊 Optional: Metrics to Mention

If you have real or simulated data to back up your demo:

- "Detected 85% of high-risk cases in our test dataset"
- "Average intervention generated in under 3 seconds"
- "Analyzed 2,000+ calendar events and 10,000+ Spotify tracks"
- "Found events in 30+ categories across College Station"

---

## 🆘 Troubleshooting Common Demo Issues

**Issue:** MCP server takes too long to respond
- **Solution:** Pre-cache sample data; use smaller date ranges in demo

**Issue:** API rate limits during demo
- **Solution:** Use mocked data for demo; show real API calls in supplementary footage

**Issue:** Event recommendations return no results
- **Solution:** Seed with pre-fetched events from Meetup/Eventbrite

**Issue:** Audio/video out of sync
- **Solution:** Record screen and audio separately, sync in post

---

## ✅ Pre-Demo Checklist

### 1 Week Before
- [ ] Test all MCP tools with sample data
- [ ] Set up demo database with realistic user scenarios
- [ ] Write and practice script
- [ ] Prepare slides/diagrams for architecture explanation

### 1 Day Before
- [ ] Full run-through of demo (record practice version)
- [ ] Check all API keys are working
- [ ] Verify screen recording software works
- [ ] Prepare backup recordings in case live demo fails

### Day Of
- [ ] Start MCP server and verify it's running
- [ ] Test chat interface with sample queries
- [ ] Clear browser cache/history for clean demo
- [ ] Close unnecessary applications (clean desktop)
- [ ] Check microphone levels
- [ ] Have script visible on second monitor

### During Recording
- [ ] Take a deep breath
- [ ] Smile (it affects your voice tone)
- [ ] Speak to the camera, not the screen
- [ ] Pause between sections (easier to edit)
- [ ] If you mess up, just restart that section (don't restart entire video)

---

## 🎁 Bonus: Social Media Snippets

**30-Second Version (Twitter/X, Instagram Reel):**
> "Built an MCP server that detects college student loneliness by analyzing calendars + Spotify. When a student starts declining invites + listening to sad music at 2am, the AI intervenes. Early detection = better outcomes. #TAMUDatathon #MCP"

**Thumbnail Text Ideas:**
- "AI That Detects Loneliness"
- "Smart Context for Mental Health"
- "Before Crisis Becomes Crisis"

---

Good luck with your demo! Remember: the goal is to show **why this matters** (mental health crisis) and **how MCP makes it possible** (smart context for AI). Keep it focused, keep it human, and show the real impact. 🚀
