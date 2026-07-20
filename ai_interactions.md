# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Challenge 1 (Add Advanced Song Features): add 5+ complex song attributes not already in `data/songs.csv`, wire them into the scoring logic in `src/recommender.py` so they actually affect rankings, and keep everything backward compatible with the existing tests and CLI.

**Prompts used:**

- "Add five new attributes to the song catalog — popularity (0-100), release decade, detailed mood tags, instrumentalness, and liveness — and make sure the scoring logic in recommender.py accounts for them without breaking the existing `Song`/`UserProfile` dataclasses that `tests/test_recommender.py` constructs with only the original fields."
- "Popularity is going to introduce a popularity bias — score it as a small continuous bonus instead of a hard match, and call that bias out explicitly wherever the model documents limitations."

**What did the agent generate or change?**

- `data/songs.csv`: added `popularity`, `release_decade`, `mood_tags` (semicolon-separated), `instrumentalness`, and `liveness` columns for all 18 songs.
- `src/recommender.py`: added the five new fields to the `Song` dataclass (all with defaults) and three new *optional* fields to `UserProfile` (`target_decade`, `favorite_mood_tag`, `prefers_instrumental`), plus scoring for mood-tag match, decade match, popularity bonus, and instrumental-preference match in both the dict-based (`score_song`) and dataclass-based (`Recommender`) scoring paths.
- `src/main.py`: no changes needed for this challenge specifically (the new attributes flow through automatically via `load_songs`/`recommend_songs`).

**What did you verify or fix manually?**

- Confirmed `pytest` still passes — the new `Song`/`UserProfile` fields all default, so the tests (which only pass the original constructor arguments) were unaffected.
- Ran the CLI before/after adding popularity scoring and noticed it actually *changed a ranking*: in the "Adversarial Conflict" profile, "Storm Runner" (popularity 70) was previously the #1 result on energy alone, but after the popularity bonus was added, "Gym Hero" (popularity 82) took over #1 despite a slightly lower raw energy match. That's a real, observable popularity-bias effect worth flagging in the model card rather than something we introduced by accident — documented under Limitations and Bias.
- Manually spot-checked the CSV values (decade, mood tags, instrumentalness/liveness) for plausibility against the existing genre/mood/energy values for each song rather than trusting the generated numbers blindly.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

Strategy pattern — for Challenge 2 (Multiple Scoring Modes).

**How did AI help you brainstorm or implement it?**

Asked the assistant to brainstorm a modular way to support multiple ranking strategies ("Genre-First," "Mood-First," "Energy-Focused") without duplicating the scoring arithmetic once per mode. The first instinct was one subclass per mode (classic GoF Strategy), but the assistant pointed out that since every mode uses the *identical* formula and only the weights differ, one subclass per mode would just copy-paste the same `if genre_match: ...` logic four times with different numbers — a maintenance risk if the recipe itself ever changed. Instead we used a single `ScoringStrategy` class parameterized by a weights dict, with four named instances (`BALANCED`, `GENRE_FIRST`, `MOOD_FIRST`, `ENERGY_FOCUSED`). This keeps the important property of the Strategy pattern — `recommend_songs()`/`Recommender.recommend()` depend only on the common `score_dict()`/`score_song()` interface, not on which mode is active — while avoiding duplicated logic.

**How does the pattern appear in your final code?**

`src/recommender.py`: the `ScoringStrategy` class and the four strategy instances, collected in the `STRATEGIES` dict. `recommend_songs()`, `score_song()`, and `Recommender.recommend()`/`explain_recommendation()` all accept an optional `strategy` argument and default to `BALANCED` if none is passed. `src/main.py` exposes the modes on the CLI (`python -m src.main genre-first`, `--list-modes`), so a user can switch strategies without touching any code.
