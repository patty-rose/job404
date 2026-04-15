"""
Personal interview profile — TEMPLATE.

Setup:
    cp questions/profile.example.py questions/profile.py
    # then edit profile.py with your own projects and story mappings

profile.py is gitignored. Your personal data stays local.
This file is the committed template — keep it generic.
"""

# ─── YOUR PROJECTS / RESUME STORIES ──────────────────────────────────────────
# Add one entry per project or significant work experience.
# These appear when you press 's' during behavioral practice.
# The key (e.g. "project_1") is the ID you'll reference in QUESTION_STORIES below.

RESUME_STORIES = {
    "project_1": {
        "label": "Project Name — Company (Backend / Full Stack / etc.)",
        "bullets": [
            "Situation: What was the business problem or technical context?",
            "Task: What were you specifically responsible for?",
            "Action: What did you build or do? Include key technical decisions.",
            "Challenge: What was the hard part, and how did you solve it?",
            "Result: What was the outcome? Quantify if possible.",
            "Signal: What does this story say about you as an engineer?",
        ],
    },
    "project_2": {
        "label": "Second Project — Company or Personal",
        "bullets": [
            "Situation: ...",
            "Task: ...",
            "Action: ...",
            "Challenge: ...",
            "Result: ...",
        ],
    },
    # Add more entries as needed.
}


# ─── QUESTION → STORY MAPPINGS ────────────────────────────────────────────────
# Optional. Map behavioral question IDs to the story IDs above.
# When you press 's' on a question, only the mapped stories are shown.
# If a question has no mapping here, all stories are shown instead.
#
# Question IDs (from behavioral.py):
#   tell_me_about_yourself, describe_your_background,
#   what_are_you_looking_for, why_interested_in_company,
#   where_do_you_see_yourself, frontend_vs_backend, ruby_on_rails,
#   python_experience, experience_with_databases,
#   most_complex_fullstack_feature, project_deep_dive_1,
#   project_deep_dive_2, project_proud_of, solved_problem_independently,
#   describe_your_best_team, cross_team_collaboration, mentorship,
#   reason_for_leaving, timeline_other_interviews, salary_expectations,
#   qa_engineer_question, greatest_weakness, failure_or_mistake

QUESTION_STORIES = {
    "tell_me_about_yourself":        ["project_1", "project_2"],
    "most_complex_fullstack_feature": ["project_1"],
    "project_deep_dive_1":           ["project_1"],
    "project_deep_dive_2":           ["project_2"],
    "project_proud_of":              ["project_1", "project_2"],
    "solved_problem_independently":  ["project_1"],
    "cross_team_collaboration":      ["project_1"],
    "failure_or_mistake":            [],   # leave empty = show all stories
}
