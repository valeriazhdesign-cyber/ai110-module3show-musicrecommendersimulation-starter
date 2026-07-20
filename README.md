# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Apple Music and Spotify combine two complementary strategies: collaborative filtering, which predicts what a listener will enjoy based on patterns across *other* users with similar taste (people who liked X also played Y), and content-based filtering, which recommends songs based on how closely their own attributes match what a listener already prefers, independent of anyone else's behavior. Apple Music also layers human editorial curation on top of both, using its algorithm mainly to decide which hand-picked playlists and songs get surfaced to which listeners, rather than generating picks from scratch. My version is a content-based recommender, since it has no multi-user listening history to draw on: it builds a `UserProfile` from a handful of stated preferences (favorite genre, favorite mood, target energy) and scores each song by how closely its `genre`, `mood`, `energy`, and `valence` match that profile — rewarding closeness to the target on the continuous features rather than simply favoring the highest energy or most upbeat songs across the board.

Some prompts to answer:

- What features does each `Song` use in your system
  - `genre`, `mood`, `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`
- What information does your `UserProfile` store
  - `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic` (dataclass form) / `genre`, `mood`, `energy` (the simpler dict form used by `src/main.py`)
- How does your `Recommender` compute a score for each song
  - See the **Algorithm Recipe** below — it awards fixed points for exact matches and a sliding-scale bonus for how close a song's energy is to the target.
- How do you choose which songs to recommend
  - Every song in the catalog is scored independently, then the full list is sorted from highest to lowest score and the top `k` are returned.

### Algorithm Recipe

| Rule | Points | Notes |
|---|---|---|
| Genre match | +2.0 | Exact match between song genre and the user's favorite genre |
| Mood match | +1.0 | Exact match between song mood and the user's favorite mood |
| Energy similarity | up to +1.5 | `1.5 * (1 - |song.energy - target_energy|)`, so a perfect match earns the full 1.5 and the bonus shrinks the further apart they are — this rewards *closeness*, not just high energy |
| Acousticness preference match (OOP interface only) | +0.5 | Awarded when the user's `likes_acoustic` flag agrees with whether the song's `acousticness` is at or above 0.5 |

Genre counts for the most because it's the strongest, least ambiguous signal of taste; mood is a secondary softer signal; energy uses a similarity curve instead of a binary match because "high energy" only helps a listener who actually wants high energy. A likely bias upfront: because genre is worth 2x a mood match, a song that matches genre but nothing else can still outrank a song that matches mood *and* has near-perfect energy — the system may over-trust genre labels over the more nuanced "vibe" attributes.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` against the expanded 18-song catalog and four distinct user profiles (three realistic, one adversarial with conflicting preferences):

```
Loaded songs: 18

=== High-Energy Pop (genre=pop, mood=happy, energy=0.85) ===

1. Sunrise City — Score: 4.46
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+1.455)
2. Gym Hero — Score: 3.38
   Because: genre match (+2.0), energy similarity (+1.38)
3. Rooftop Lights — Score: 2.37
   Because: mood match (+1.0), energy similarity (+1.365)
4. Storm Runner — Score: 1.41
   Because: energy similarity (+1.41)
5. Night Drive Loop — Score: 1.35
   Because: energy similarity (+1.35)

=== Chill Lofi (genre=lofi, mood=chill, energy=0.35) ===

1. Library Rain — Score: 4.50
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+1.5)
2. Midnight Coding — Score: 4.39
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+1.395)
3. Focus Flow — Score: 3.42
   Because: genre match (+2.0), energy similarity (+1.425)
4. Spacewalk Thoughts — Score: 2.40
   Because: mood match (+1.0), energy similarity (+1.395)
5. Coffee Shop Stories — Score: 1.47
   Because: energy similarity (+1.47)

=== Deep Intense Rock (genre=rock, mood=intense, energy=0.9) ===

1. Storm Runner — Score: 4.49
   Because: genre match (+2.0), mood match (+1.0), energy similarity (+1.485)
2. Gym Hero — Score: 2.46
   Because: mood match (+1.0), energy similarity (+1.455)
3. Neon Pulse Overdrive — Score: 1.43
   Because: energy similarity (+1.425)
4. Iron Maw — Score: 1.40
   Because: energy similarity (+1.395)
5. Sunrise City — Score: 1.38
   Because: energy similarity (+1.38)

=== Adversarial Conflict (genre=screamo, mood=sad, energy=0.9) ===

1. Storm Runner — Score: 1.49
   Because: energy similarity (+1.485)
2. Gym Hero — Score: 1.46
   Because: energy similarity (+1.455)
3. Neon Pulse Overdrive — Score: 1.43
   Because: energy similarity (+1.425)
4. Iron Maw — Score: 1.40
   Because: energy similarity (+1.395)
5. Sunrise City — Score: 1.38
   Because: energy similarity (+1.38)
```

The adversarial profile (`genre="screamo"`, which doesn't exist in the catalog, plus a conflicting `mood="sad"` with high `energy=0.9`) is telling: with no genre or mood to match on, every recommendation falls back to energy similarity alone, and the ranking becomes indistinguishable from "sort by energy." The system degrades gracefully (it doesn't crash or return nothing) but it also silently stops personalizing — it never tells the user "I couldn't match your genre."

> Note: the output above reflects the original Phase 2/3 recipe (genre/mood/energy only), captured before the Optional Extensions below added popularity, mood tags, and decade scoring. See **Optional Extensions** for current output including those attributes.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

**Weight Shift experiment:** halved the genre weight (2.0 → 1.0) and doubled the energy weight (1.5 → 3.0), then reran all four profiles.

Before (original weights) vs. after (shifted weights), for "High-Energy Pop":

```
Before: 1. Sunrise City — 4.46 (genre +2.0, mood +1.0, energy +1.455)
After:  1. Sunrise City — 4.91 (genre +1.0, mood +1.0, energy +2.91)
```

The #1 song didn't change for any of the three realistic profiles — genre + mood + high energy songs were already the strongest candidates, so shifting weight toward energy just widened their lead rather than changing the winner. The bigger effect showed up further down the list: songs that only matched on energy (like "Storm Runner" for the Pop profile) jumped several ranks because their similarity bonus nearly doubled, while genre-only matches lost ground. For the Adversarial Conflict profile — where nothing matches genre or mood — the ranking was already 100% energy-driven, so the experiment didn't change its order at all, only its raw scores. This confirms the system is most sensitive to weight tuning in the "partial match" middle of the list, and least sensitive at the extremes (a perfect triple match, or a total mismatch).

- We did not add tempo or danceability to the score in the main recipe — see "Ideas for Improvement" in `model_card.md`.

---

## Limitations and Risks

- The catalog is tiny (18 songs across 15 genres) — several genres have only one representative song, so a genre match is really just "is this the one song we have in that genre," not a robust signal of taste.
- Genre is weighted 2x higher than mood, so the system tends to trust a broad genre label over the more specific mood/energy attributes that arguably capture "vibe" more accurately. Two songs in the same genre can feel completely different, but the recipe treats any genre match the same.
- It has no memory of listening history, skips, or likes — it is purely content-based, so it can't get better over time or account for the fact that people's taste doesn't only depend on static song attributes.
- It does not understand lyrics, vocals, or cultural context at all — a "happy" mood label is just a tag in the CSV, not something derived from the song itself.
- When a user's stated genre/mood doesn't exist in the catalog (see the "Adversarial Conflict" profile above), the system silently falls back to ranking by energy alone with no warning that personalization failed.

You will go deeper on this in your model card.

---

## Optional Extensions

All four optional challenges were implemented:

**Challenge 1 — Advanced Song Features:** added `popularity` (0-100), `release_decade`, `mood_tags` (detailed tags like "euphoric;energetic"), `instrumentalness`, and `liveness` to `data/songs.csv` and `Song`/`UserProfile`. Popularity now contributes a small continuous bonus (`popularity/100 * weight`), mood tags and decade contribute match bonuses, and instrumentalness contributes a preference-match bonus. See `ai_interactions.md` for the agentic workflow used.

**Challenge 2 — Multiple Scoring Modes (Strategy pattern):** `src/recommender.py` now has a `ScoringStrategy` class parameterized by weights, with four interchangeable instances: `balanced` (the original recipe), `genre-first`, `mood-first`, and `energy-focused`. Switch modes from the CLI:

```bash
python -m src.main genre-first
python -m src.main mood-first --diversify
python -m src.main --list-modes
```

**Challenge 3 — Diversity and Fairness Logic:** `recommend_songs(..., diversify=True)` applies a greedy re-ranking penalty so repeated picks from the same artist cost progressively more, instead of one artist quietly dominating the top 5. In the Chill Lofi profile, LoRoom's two songs ("Midnight Coding" and "Focus Flow") both land in the top 3 by raw score; with `--diversify` on, "Focus Flow" drops below "Spacewalk Thoughts" (a different artist) to make room for variety.

**Challenge 4 — Visual Summary Table:** CLI output is now a `tabulate`-formatted table (`#`, Title, Artist, Score, Reasons) instead of plain print statements.

Sample output showing genre-first mode with the diversity penalty on:

```
Loaded songs: 18
Scoring mode: genre-first (diversity penalty on)

=== Chill Lofi (genre=lofi, mood=chill, energy=0.35) ===

|   # | Title               | Artist         |   Score | Reasons                                                                                      |
|-----|---------------------|----------------|---------|------------------------------------------------------------------------------------------------|
|   1 | Library Rain        | Paper Lanterns |    5.62 | genre match (+4.0), mood match (+0.5), energy similarity (+1.0), popularity bonus (+0.12)     |
|   2 | Midnight Coding     | LoRoom         |    5.57 | genre match (+4.0), mood match (+0.5), energy similarity (+0.93), popularity bonus (+0.1375)  |
|   3 | Spacewalk Thoughts  | Orbit Bloom    |    4.08 | mood match (+3.0)... |
```

A side effect worth flagging: adding a popularity bonus changed a ranking outcome. In the Adversarial Conflict profile (no genre/mood match at all), "Storm Runner" (popularity 70) used to rank #1 on energy similarity alone; after the popularity bonus was added, "Gym Hero" (popularity 82) overtook it despite a very slightly worse energy match. That's a real, small-scale demonstration of popularity bias — see `model_card.md` for the full discussion.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this

Building even this small a recommender made it obvious that "prediction" here is really just arithmetic on labels someone already assigned — the system has no independent understanding of what makes a song "happy" or "intense," it only knows whether a string matches another string, or how close two floats are. That's a useful reminder that a real system's quality is capped by the quality and granularity of its underlying data and taste-profile representation, not just its scoring cleverness. A collaborative-filtering system (recommending based on what similar *users* liked) would behave completely differently here, since it doesn't need any of these hand-labeled attributes at all — it would need enough users and interaction data instead.

The bias risk that stood out most was the fixed weighting: because genre counts for 2x what mood does, and because the catalog isn't evenly distributed across genres, the system will structurally favor whichever genres happen to be well represented, regardless of whether they're the best match for a listener's actual mood or energy preference. That's the same mechanism behind real "filter bubble" concerns — a system that keeps recommending what's already popular/represented in its training data, rather than what's genuinely closest to a user's taste, can narrow what people are exposed to over time.



