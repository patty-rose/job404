"""
Behavioral question bank — generic coaching frameworks.
Personal projects and story mappings live in profile.py (gitignored).

Setup: cp questions/profile.example.py questions/profile.py
       then fill in your own projects.
"""

try:
    from questions.profile import RESUME_STORIES, QUESTION_STORIES
except ImportError:
    try:
        from profile import RESUME_STORIES, QUESTION_STORIES
    except ImportError:
        RESUME_STORIES = {}
        QUESTION_STORIES = {}


STAR_REMINDER = """\
S — Situation  Set the scene in one or two sentences. Don't bury the action in backstory.
T — Task       Your specific role or responsibility. What was needed from YOU?
A — Action     What did YOU do? (Most of your answer lives here — use "I" not "we".)
R — Result     What changed? Quantify if possible. Tie it back to the team or product.

Tips:
  • Spend most time on Action — that's where your competency shows.
  • Attach a number if you can: "reduced by X%", "ran for N hours", "covered N edge cases".
  • End on the Result, not the process. Interviewers remember the last thing you say.
  • Prepare 2–3 versatile stories. A good story answers many questions."""


CATEGORIES = {
    "intro":       "Introduction & Background",
    "motivation":  "Motivation & Goals",
    "technical":   "Technical Experience & Skills",
    "projects":    "Project Deep Dives",
    "teamwork":    "Teamwork & Culture",
    "situational": "Situational / Unexpected",
}


def _stories_for(question_id: str) -> list[str]:
    """Return story IDs for a question, falling back to all stories if no mapping."""
    if question_id in QUESTION_STORIES:
        return QUESTION_STORIES[question_id]
    return list(RESUME_STORIES.keys())


# ─── QUESTIONS ────────────────────────────────────────────────────────────────

QUESTIONS = [

    # ── INTRODUCTION & BACKGROUND ────────────────────────────────────────────

    {
        "id": "tell_me_about_yourself",
        "prompt": "Tell me about yourself.",
        "category": "intro",
        "coaching": """\
Your opening pitch. Deliver it practiced and confident — this question frames everything else.

Structure (~90 seconds):
  1. Current identity: what kind of engineer are you, what's your primary domain?
  2. Most recent role: company/team/what you built; key moment of ownership or growth
  3. Transition: why you left (one sentence, factual, no dwelling)
  4. What differentiates you: prior career, domain expertise, unique perspective
  5. Closer: what specifically draws you to THIS company (prep this for every interview)

Tips:
  • Don't lead with your education or chronological history — lead with who you are now.
  • The layoff/gap is one sentence. Don't over-explain or apologize.
  • The closer must be specific to the company. Generic closers are immediately detectable.
  • End with energy — this sets the tone for the whole interview.\
""",
        "follow_ups": [
            "What's a specific project you're most proud of?",
            "What does 'growing toward senior' look like in practice for you?",
            "What drew you to engineering from your previous career?",
        ],
        "stories": _stories_for("tell_me_about_yourself"),
    },

    {
        "id": "describe_your_background",
        "prompt": "Walk me through your resume / background.",
        "category": "intro",
        "coaching": """\
More chronological than 'tell me about yourself', but still a story of growth — not a list.

Structure:
  1. Start at your most relevant role: team, what you were building, your level
  2. Key growth moment: when did your responsibilities expand significantly?
  3. Expanded scope: cross-team work, full-stack ownership, new domains
  4. Transition: brief and factual
  5. What you're looking for now — lead into the conversation

Make it a narrative arc: "I joined as X, grew into Y, and I'm now looking for Z."\
""",
        "follow_ups": [
            "How did you manage owning a product as a relatively junior engineer?",
            "What was the biggest technical challenge you owned independently?",
        ],
        "stories": _stories_for("describe_your_background"),
    },

    # ── MOTIVATION & GOALS ───────────────────────────────────────────────────

    {
        "id": "what_are_you_looking_for",
        "prompt": "What are you looking for in your next role?",
        "category": "motivation",
        "coaching": """\
Lead with growth and impact, not just a job or stability.

Strong answer framework:
  1. Technical growth direction (senior, tech lead — be specific about the trajectory)
  2. Type of work (what kinds of problems excite you?)
  3. Team culture (what environment brings out your best work?)
  4. Optionally: tie back to this company ("...and what I've seen here suggests that fit")

What makes this answer land:
  • "Technical leadership opportunities" signals ambition
  • "Mentorship — giving and receiving" is genuine and memorable
  • Being specific beats generic ("collaborative team" < "a team that does X")

What to avoid: anything that sounds like "I just need a job" or is purely about compensation.\
""",
        "follow_ups": [
            "What does technical leadership look like in practice for you right now?",
            "Can you give an example of mentoring someone, even informally?",
            "What would make you feel like you're growing versus stagnating?",
        ],
        "stories": [],
    },

    {
        "id": "why_interested_in_company",
        "prompt": "Why are you interested in [this company]?",
        "category": "motivation",
        "coaching": """\
This MUST be specific to the company. Generic answers are immediately detectable.

Framework:
  1. Something about their product or mission (not just "cool company")
  2. Something about the technical problem space (why it's interesting to YOU)
  3. A culture or team signal you picked up (from the JD, research, or today's conversation)

Structure:
  "I'm drawn to [Company] because [specific product/mission]. The engineering problem of [X]
  is genuinely interesting to me — [why it connects to your background]. And from what I've
  seen in [JD / this conversation], the team culture of [specific thing] is what I'm looking for."

Prep a specific version for EVERY company before the interview.
This question is a gimme if you've done homework, a red flag if you haven't.\
""",
        "follow_ups": [
            "What specifically about the product have you used or researched?",
            "What do you know about our engineering challenges?",
        ],
        "stories": [],
    },

    {
        "id": "where_do_you_see_yourself",
        "prompt": "Where do you see yourself in 3–5 years?",
        "category": "motivation",
        "coaching": """\
Growth-oriented without sounding like you're positioning to leave after 2 years.

Framework:
  1. Short term: grow into senior — technical depth, leading projects, mentoring others
  2. Medium term: explore tech lead or staff trajectory depending on context
  3. Anchor to this company: "...and I see [Company] as the right place for that because [X]"

Avoid:
  • "I want to be a CTO" (too far, sounds rehearsed)
  • "Just keep growing" (too vague, low ambition signal)
  • Anything that implies you'll leave for a startup/management in 18 months

Aim for: senior → tech lead trajectory, tied to the company's scale.\
""",
        "follow_ups": [
            "What's the gap between where you are now and senior in your mind?",
            "What would a tech lead role require that you're not doing yet?",
        ],
        "stories": [],
    },

    # ── TECHNICAL EXPERIENCE & SKILLS ────────────────────────────────────────

    {
        "id": "frontend_vs_backend",
        "prompt": "What's your experience with React / frontend vs backend?",
        "category": "technical",
        "coaching": """\
Be honest about the balance and own it confidently.

Key points:
  • Name your ratio (e.g., "about 70/30 backend to frontend")
  • Explain why: was it the team structure, your preference, or both?
  • Emphasize what you CAN do on the frontend — don't just apologize for it
  • If you enjoyed owning features end-to-end, say so — it's a strength

What NOT to do: claim frontend parity if you don't have it.
They'll find out fast in a screen or on the job.\
""",
        "follow_ups": [
            "Walk me through a feature where you owned both frontend and backend.",
            "What's the most complex React work you've done?",
            "Are you comfortable picking up frontend work for a feature independently?",
        ],
        "stories": [],
    },

    {
        "id": "ruby_on_rails",
        "prompt": "Are you comfortable with Ruby on Rails, or open to learning it?",
        "category": "technical",
        "coaching": """\
Be honest: if you don't have production Rails experience, say so — but lead with adaptability.

Strong answer structure:
  1. State your actual backend framework experience (e.g., Django, Express, Spring)
  2. Draw the conceptual parallel: both are MVC frameworks with ORM layers — the patterns transfer
  3. Show you've already started: have you built anything in Rails yet? Even a toy project matters.
  4. Frame it as excitement, not just willingness: "I'm genuinely looking forward to learning it"

The key signal: "I've already started" beats "I'm a fast learner" every time.
Initiative is more convincing than generic adaptability claims.\
""",
        "follow_ups": [
            "What have you built so far in Rails?",
            "How long do you estimate before you'd be productive in a Rails codebase?",
            "What's your process for ramping up in an unfamiliar framework?",
        ],
        "stories": [],
    },

    {
        "id": "python_experience",
        "prompt": "What's your Python experience?",
        "category": "technical",
        "coaching": """\
Be clear and confident. State years of professional use and what you built with it.

Framework:
  • How many years, and was it production? (professional experience > side projects)
  • What kind of work: APIs, ETL/data scripts, background jobs, testing?
  • Any notable Python-specific patterns you reached for: generators, decorators, async?
  • Testing approach in Python?

Keep it brief and confident. Offer a specific project example if they want to dig in.
Don't over-explain if your experience is strong — let it land.\
""",
        "follow_ups": [
            "Have you worked with async Python?",
            "What Python libraries do you reach for most?",
            "How do you approach testing in Python?",
        ],
        "stories": _stories_for("python_experience"),
    },

    {
        "id": "experience_with_databases",
        "prompt": "What's your experience with databases — SQL, PostgreSQL, etc.?",
        "category": "technical",
        "coaching": """\
Be honest about your SQL level — they may test it in the screen.

Framework:
  • ORM experience: how did you interact with the DB day-to-day? (migrations, queries, indexing)
  • Direct SQL: what's your comfort level with raw queries?
  • Be specific about any gaps: "I'm comfortable with standard queries and joins;
    window functions and complex aggregations are an area I've been building"
  • Production experience matters: migrations on live data, query optimization, schema design

Don't claim fluency you don't have. A bad answer here is being caught in a screen
after saying you know SQL well.\
""",
        "follow_ups": [
            "Can you write a GROUP BY query with a HAVING clause?",
            "Have you dealt with slow queries or query optimization in production?",
            "What's your experience with migrations on a production database?",
        ],
        "stories": [],
    },

    # ── PROJECT DEEP DIVES ────────────────────────────────────────────────────

    {
        "id": "most_complex_fullstack_feature",
        "prompt": "What was the most complex full-stack feature you developed?",
        "category": "projects",
        "coaching": """\
This was asked in a real interview — be ready for it.

What makes a strong answer:
  • Full stack means you touched UI, API, and data layer — describe all three briefly
  • Lead with what made it COMPLEX (not just big): the hard technical decision,
    the cross-system coordination, the scale challenge, the ambiguous requirements
  • Use STAR: situation, what you built, the hard part, the outcome
  • Include: what you'd do differently (shows engineering maturity)

Use 's' to pull up your project stories for concrete examples.
Pick the one with the strongest technical challenge.\
""",
        "follow_ups": [
            "How did you handle the API contract between frontend and backend?",
            "What broke and how did you debug it?",
            "If you could redesign it, what would you do differently?",
        ],
        "stories": _stories_for("most_complex_fullstack_feature"),
    },

    {
        "id": "project_deep_dive_1",
        "prompt": "Walk me through [your primary backend/technical project] in depth.",
        "category": "projects",
        "coaching": """\
This is the full STAR deep-dive on your strongest technical project.

What to cover:
  1. Why it mattered: what was broken, missing, or needed?
  2. What you built: describe the architecture or approach at the right level of detail
  3. The hard problem: what was the non-obvious challenge?
  4. Your solution: explain the key technical decision clearly — this is your CS/engineering moment
  5. Execution details: scale, constraints, coordination required
  6. Result: specific and concrete

The technical highlight is what interviewers remember.
Be able to explain your key design decision clearly and concisely.

Press 's' to review your story bullets.\
""",
        "follow_ups": [
            "How did you test it before running in production?",
            "What would you do differently now?",
            "How did you handle rollback or failure mid-way?",
            "What did you learn about scale/performance from this?",
        ],
        "stories": _stories_for("project_deep_dive_1"),
    },

    {
        "id": "project_deep_dive_2",
        "prompt": "Tell me about a personal project or side project you've built.",
        "category": "projects",
        "coaching": """\
Personal projects signal initiative, curiosity, and engineering judgment.

What makes a strong answer:
  1. The problem: what were you trying to solve, and why existing tools didn't cut it
  2. Your insight: what did YOU see that shaped the architecture?
  3. Key design decisions: what tradeoffs did you make and why?
  4. What it does now: does it actually work and do you use it?
  5. What you'd add next (shows continued thinking)

This demonstrates: systems thinking, taste, self-direction.
The best personal project stories show that you build things for real reasons,
not just to have something on a resume.

Press 's' to review your story bullets.\
""",
        "follow_ups": [
            "Why did you build it this way vs [obvious alternative]?",
            "What broke or surprised you during the build?",
            "What would you add if you spent another week on it?",
        ],
        "stories": _stories_for("project_deep_dive_2"),
    },

    {
        "id": "project_proud_of",
        "prompt": "Tell me about a project you're proud of.",
        "category": "projects",
        "coaching": """\
Choose based on context — match the project to what the role cares about.

What makes a 'proud of' answer land:
  1. You took genuine ownership — not just "was assigned to"
  2. There was a hard problem and you solved it (ideally independently or creatively)
  3. There was a real, specific result
  4. Optional: emotional resonance — why did it feel like a milestone?

The "proud" part should come through naturally — don't announce it, show it.
The best version of this answer makes the interviewer feel the satisfaction too.

Press 's' to see your projects and pick the best fit for this conversation.\
""",
        "follow_ups": [
            "What specifically made you proud of it vs other projects?",
            "What was the hardest part?",
            "What would you change now with hindsight?",
        ],
        "stories": _stories_for("project_proud_of"),
    },

    {
        "id": "solved_problem_independently",
        "prompt": "Tell me about a time you solved a difficult problem independently.",
        "category": "projects",
        "coaching": """\
The 'independently' angle is important — lean into it.

What to emphasize:
  • You discovered the problem (or the harder sub-problem) yourself
  • You didn't wait to be told what to do — you diagnosed and designed the solution
  • You sought review/validation after forming your approach, not before
  • This is the junior-to-mid transition marker: going from "what should I do?" to "here's what I'm doing"

STAR structure:
  S: What was the system/situation?
  T: What problem emerged that no one handed you?
  A: How did you diagnose it, design a solution, and execute?
  R: What was the outcome + what did it signal about your growth?

Press 's' to review your project stories for a strong example.\
""",
        "follow_ups": [
            "How did you know your approach was the right one?",
            "What would you have done if your solution hadn't worked?",
            "How did you validate the result?",
        ],
        "stories": _stories_for("solved_problem_independently"),
    },

    # ── TEAMWORK & CULTURE ───────────────────────────────────────────────────

    {
        "id": "describe_your_best_team",
        "prompt": "Tell me about a team experience you're proud of.",
        "category": "teamwork",
        "coaching": """\
This is a culture-fit question. What you say you value in teams signals who you are.

What to hit:
  1. Specific team context (who, what you were building)
  2. What made the collaboration work: trust, communication, shared ownership, support
  3. Your role in contributing to that culture — not just receiving it
  4. Why it mattered to you personally

Avoid vague praise: "everyone was great!" → not memorable.
Specific: "we had a norm where anyone could push back on a design in review,
and we'd argue it out in the PR comments — that felt healthy" → memorable.

If you have a background that shapes how you view teams (teaching, managing, coaching),
this is a natural place to connect it.\
""",
        "follow_ups": [
            "What would you do if you joined a team that didn't have that culture?",
            "How do you contribute to team culture proactively?",
        ],
        "stories": [],
    },

    {
        "id": "cross_team_collaboration",
        "prompt": "Tell me about a time you worked across teams or with cross-functional partners.",
        "category": "teamwork",
        "coaching": """\
Focus on HOW you communicated and coordinated — not just what you built.

Strong answers hit:
  • Who the other teams were and why their involvement mattered
  • How you kept them informed and aligned (proactive communication > reactive)
  • How you handled conflicting priorities or timelines
  • What you learned about working across organizational boundaries

Common mistake: describing the technical work in detail but skipping the collaboration story.
The question is about the people coordination, not the code.

Press 's' to see if any of your projects involved cross-team work.\
""",
        "follow_ups": [
            "How did you handle disagreements across teams?",
            "How did you keep stakeholders aligned when priorities shifted?",
        ],
        "stories": _stories_for("cross_team_collaboration"),
    },

    {
        "id": "mentorship",
        "prompt": "Tell me about your experience with mentorship — giving or receiving.",
        "category": "teamwork",
        "coaching": """\
Both directions matter. Have an example for each if you can.

RECEIVING: Think about a time a mentor helped you level up — not just gave you an answer,
but helped you think differently. What was the dynamic? What changed for you?

GIVING: You don't need to have been a senior engineer to have mentored someone.
Code reviews, explaining concepts, onboarding a new teammate, writing clear docs
for future engineers — these all count. If you have a teaching/coaching background,
connect it here — it's differentiating.

Be specific. "I care about mentorship" without an example is noise.
With a concrete example, it becomes a real signal.\
""",
        "follow_ups": [
            "How would you support a junior engineer who was struggling but not asking for help?",
            "What's the best thing a mentor did for you?",
        ],
        "stories": [],
    },

    # ── SITUATIONAL / UNEXPECTED ─────────────────────────────────────────────

    {
        "id": "reason_for_leaving",
        "prompt": "Why did you leave your last job?",
        "category": "situational",
        "coaching": """\
Direct, factual, brief. Then move on.

If it was a layoff:
  "[Company] did a significant reduction in force. It was a business decision, not performance related."
  That's it. Don't over-explain. Don't get emotional. Don't bad-mouth the company.

If they ask about your performance before the layoff:
  Mention what you were working toward ("I was working toward a promotion, leading more complex
  cross-team projects") — brief, then redirect.

If you left voluntarily:
  Be honest: better growth opportunity, misalignment with direction, team changes.
  Frame it as forward-looking, not as running away from something.

Always end by redirecting to what you're excited about next.\
""",
        "follow_ups": [
            "How are you doing with the transition?",
            "What are you most excited about in your next role?",
        ],
        "stories": [],
    },

    {
        "id": "timeline_other_interviews",
        "prompt": "What's your timeline? Are you interviewing elsewhere?",
        "category": "situational",
        "coaching": """\
Be honest but measured. You don't owe details.

Strong answer:
  "I'm actively applying and have a few conversations in progress.
  I'm being thoughtful about where I land though."

This signals: active (not desperate), has options (don't undersell), selective (not just throwing apps).

If they push for a hard timeline:
  "I'd like to have something in the next 4–6 weeks, but I'm prioritizing fit over speed."

If you have a competing offer with a deadline: be honest about it.
Companies generally respect that and may accelerate. Lying about offers backfires.\
""",
        "follow_ups": [
            "If we moved quickly, could you be available in 2 weeks?",
            "What would make you choose one offer over another?",
        ],
        "stories": [],
    },

    {
        "id": "salary_expectations",
        "prompt": "What are your salary expectations?",
        "category": "situational",
        "coaching": """\
Know your number before the conversation. Don't make one up on the spot.

Do your research:
  • Levels.fyi, Glassdoor, LinkedIn Salary, Blind for your level and location
  • Factor in: base, bonus frequency/size, equity type (RSU vs options, vesting), 401k match

In the conversation:
  • State your range confidently — don't apologize for having a number
  • Add: "I'm open to discussing the full package — I care about the role and growth too"
  • If they push back: "What's the budget for this role?" — put it on them

If the range doesn't overlap:
  Find out before you invest more time. It's okay to ask early in the process.\
""",
        "follow_ups": [
            "Is that firm or is there flexibility?",
            "How did you arrive at that number?",
        ],
        "stories": [],
    },

    {
        "id": "qa_engineer_question",
        "prompt": "Would you be open to a QA engineer role, or are you primarily looking for SWE?",
        "category": "situational",
        "coaching": """\
Unexpected question — happened in a real interview. Be clear about your intent.

If you're SWE-focused:
  "I'm primarily looking for a software engineering role. I respect QA work and understand
  how it contributes to quality — but my career trajectory is toward backend/full-stack
  engineering and technical depth."

If QA is embedded in their SWE workflow:
  "I'm always interested in quality practices — engineers who think about testing deeply
  write better software. But my interest is in a building-focused SWE role."

Don't hedge so much you imply you'd take anything.
Clarity is respected even if it's not the answer they want.\
""",
        "follow_ups": [
            "Do you have experience writing automated tests?",
            "How do you think about quality in your engineering work?",
        ],
        "stories": [],
    },

    {
        "id": "greatest_weakness",
        "prompt": "What's your greatest weakness or area for improvement?",
        "category": "situational",
        "coaching": """\
Pick something real. Not a fake "I work too hard."

What makes a strong weakness answer:
  1. It's genuine — interviewers can tell when you're dodging
  2. It's relevant but not disqualifying for the role
  3. You're actively working on it (not just "I'm aware of it")
  4. You can show some progress

Good categories to draw from:
  • A technical skill gap you've been actively closing (SQL, a framework, systems design)
  • A scope/estimation challenge ("I used to underestimate complexity on large features")
  • Communication in ambiguous situations ("early in my career I'd wait too long to escalate")

Structure: name it → what you've done about it → brief progress signal.
End on forward momentum, not on the weakness.\
""",
        "follow_ups": [
            "Can you give a specific example where that weakness affected your work?",
            "What specifically has changed in how you approach that area?",
        ],
        "stories": [],
    },

    {
        "id": "failure_or_mistake",
        "prompt": "Tell me about a time you failed or made a significant mistake.",
        "category": "situational",
        "coaching": """\
Tests self-awareness, honesty, and resilience. Pick something real.

Rules:
  1. Own it fully — don't blame others or circumstances
  2. Show what you learned or changed because of it
  3. Keep proportional: serious enough to show real consequences, not so catastrophic it's alarming
  4. End on what changed, not on the failure itself

Good source material:
  • A technical decision that turned out wrong (and what you'd do differently)
  • A communication gap that caused a delay or misalignment
  • A real interview failure (e.g., blanking on a SQL question in a screen)
    "I was asked to write a query live and blanked on HAVING vs WHERE. I've since
    deliberately practiced SQL outside the ORM to close that gap." — honest, shows growth.

STAR: what happened → what you did (or failed to do) → what changed\
""",
        "follow_ups": [
            "What would you do differently?",
            "How did you recover from it?",
        ],
        "stories": _stories_for("failure_or_mistake"),
    },
]


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def get_by_category(category: str) -> list[dict]:
    return [q for q in QUESTIONS if q["category"] == category]


def get_all_ids() -> list[str]:
    return [q["id"] for q in QUESTIONS]
