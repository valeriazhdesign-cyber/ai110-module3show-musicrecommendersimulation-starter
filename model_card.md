# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder is a classroom simulation of a content-based music recommender. Given a listener's stated taste (a favorite genre, a favorite mood, and a target energy level), it ranks a small song catalog and returns the top matches with a plain-language explanation for each score.

- It generates a ranked list of songs plus human-readable reasons ("genre match (+2.0), energy similarity (+1.46)").
- It assumes the user can articulate their taste as a few simple attributes up front — it does not learn from behavior like skips or replays.
- This is for classroom exploration only. It is not intended for real users: the catalog is tiny (18 songs), hand-labeled, and not representative of any real streaming library.

---

## 3. How the Model Works

Every song in the catalog gets scored against the user's stated preferences, then the full list is sorted from highest to lowest score and the top few are returned.

- **Features used per song:** genre, mood, energy, tempo, valence, danceability, acousticness, and (added as an Optional Extension) popularity, release decade, detailed mood tags, instrumentalness, and liveness.
- **User preferences considered:** a favorite genre, a favorite mood, a target energy level, whether the user likes acoustic songs, and optionally a target decade, a detailed mood tag, and an instrumental preference.
- **How it turns those into a score:** a matching genre, mood, energy-closeness, acousticness preference, mood-tag match, decade match, and instrumental preference each contribute points; popularity contributes a small continuous bonus scaled by `popularity / 100`. The exact weights depend on which **scoring mode** is active (see below) — energy always uses the *closeness* curve (`1 - |song.energy - target_energy|`), never a raw threshold.
- **Scoring modes (Strategy pattern, Optional Extension):** `balanced` (the original recipe: genre 2.0 / mood 1.0 / energy 1.5), `genre-first` (genre 4.0), `mood-first` (mood 3.0, mood tag 2.0), and `energy-focused` (energy 3.5). Switch modes with `python -m src.main <mode>`.
- **Diversity penalty (Optional Extension):** `recommend_songs(..., diversify=True)` greedily re-ranks the scored list so that each additional pick from an already-selected artist is penalized, so one artist can't quietly fill the whole top 5.
- **What changed from the starter logic:** the starter's `load_songs`, `score_song`, `recommend_songs`, and `Recommender.recommend`/`explain_recommendation` were all placeholders (`TODO`s that returned empty lists or the first `k` songs unchanged). All of that logic was implemented from scratch, and a broken import in `main.py` (`from recommender import ...`, which fails when run as `python -m src.main`) was fixed to `from src.recommender import ...`.

---

## 4. Data

- **Catalog size:** 18 songs (the original 10 plus 8 added to broaden genre/mood coverage).
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, metal, folk, r&b, reggae, country, edm — 15 distinct genres across 18 songs, so most genres have only a single song.
- **Moods represented:** happy, chill, intense, relaxed, moody, focused, confident, calm, aggressive, nostalgic, romantic, laidback, uplifting, euphoric.
- **What we added:** 8 songs spanning genres/moods that weren't in the starter file (hip-hop, classical, metal, folk, r&b, reggae, country, edm) so the catalog could support more varied test profiles.
- **What's missing:** there's no representation of lyrics, vocals, language, cultural/regional genres, or multiple songs per genre — so the system can't yet distinguish "good pop song for this listener" from "the only pop song we happen to have."

---

## 5. Strengths

- For profiles whose genre/mood exist in the catalog (Chill Lofi, High-Energy Pop, Deep Intense Rock), the top result is consistently the song that matches on all three signals — the ranking "feels" right and matches intuition (e.g., "Storm Runner," a 0.91-energy rock/intense track, is the clear #1 for the Deep Intense Rock profile).
- The energy-similarity curve correctly distinguishes "closer to target" from "just higher" — a mid-energy song beats a maxed-out one when the user's target energy is moderate, which is the whole point of using a similarity score instead of a raw threshold.
- Every recommendation comes with a specific, itemized reason list, so a user (or a grader) can audit exactly why a song scored the way it did rather than trusting a black box.

---

## 6. Limitations and Bias

The system over-relies on genre as a signal: because a genre match is worth twice as much as a mood match, and because most genres in the catalog only have one song, the recommender effectively narrows to "find the one song in this genre" rather than reasoning about vibe more holistically. In the weight-shift experiment (doubling energy's weight, halving genre's), the #1 recommendation didn't change for any realistic profile — genre-heavy songs were already dominant enough that the shift only reordered the middle of the list. That's a mild filter-bubble risk in miniature: a system that leans this hard on one categorical label will keep recommending within that label's silo even when a listener's actual mood/energy preferences would be better served by a song labeled differently. The Adversarial Conflict test (`genre="screamo"`, not in the catalog, with `mood="sad"` and `energy=0.9`) also exposed a silent-degradation limitation — when neither genre nor mood exist to match against, the system quietly falls back to ranking by energy alone, with no signal to the user that their genre/mood couldn't be honored.

**Popularity bias (found while implementing the Optional Extensions):** adding a small popularity bonus was meant to be a minor nudge, but it was strong enough to flip a real ranking outcome. In the Adversarial Conflict profile, "Storm Runner" (popularity 70) originally ranked #1 on energy similarity alone; once the popularity bonus was added, "Gym Hero" (popularity 82) overtook it despite a very slightly worse energy match. Any system that factors in raw popularity — even lightly — will structurally favor already-popular items over lesser-known ones that might be a better content match, which is the same dynamic that lets popular tracks snowball on real platforms. The diversity penalty (Optional Extension, Challenge 3) helps with artist concentration but does not address this popularity-favoring effect at all, since it penalizes repeated *artists*, not repeated *popularity tiers*.

---

## 7. Evaluation

We tested four user profiles end-to-end through `python -m src.main`:

- **High-Energy Pop** (`genre=pop, mood=happy, energy=0.85`) — a realistic, well-represented profile.
- **Chill Lofi** (`genre=lofi, mood=chill, energy=0.35`) — a realistic profile at the opposite end of the energy spectrum.
- **Deep Intense Rock** (`genre=rock, mood=intense, energy=0.9`) — a realistic profile testing a third genre/mood pair.
- **Adversarial Conflict** (`genre=screamo, mood=sad, energy=0.9`) — an edge case designed to see whether the scoring logic breaks or degrades gracefully when the genre doesn't exist in the catalog and the mood/energy combination is internally unusual (very high energy paired with sadness).

**Profile comparisons:**

- *High-Energy Pop vs. Chill Lofi:* the Pop profile surfaces high-energy, happy pop/indie-pop tracks (Sunrise City, Gym Hero, Rooftop Lights), while the Lofi profile surfaces low-energy, chill/focused lofi and ambient tracks (Library Rain, Midnight Coding, Focus Flow) — the two lists share zero songs in their top 5, which makes sense since they're near-opposite ends of the energy scale and target different genres entirely.
- *Deep Intense Rock vs. Adversarial Conflict:* both profiles ask for `energy=0.9`, and their top 5 lists overlap heavily (Storm Runner, Gym Hero, Neon Pulse Overdrive, Iron Maw, Sunrise City all appear in both) — because Adversarial Conflict's genre/mood don't exist in the catalog, it collapses into "whatever the Rock profile would rank by energy alone," confirming that once genre/mood stop contributing, energy similarity becomes the *entire* ranking signal.

What surprised us: the adversarial profile didn't produce nonsense or an error — it produced a perfectly reasonable-*looking* list, just one that was secretly not personalized at all beyond energy. That's arguably a more concerning failure mode than an obvious error, since a user wouldn't know their genre/mood preference was silently ignored.

---

## 8. Future Work

- Surface a warning when a user's requested genre or mood doesn't exist anywhere in the catalog, instead of silently falling back to an energy-only ranking.
- Extend the diversity penalty (currently artist-only) to also dampen repeated popularity tiers, so it addresses the popularity-bias finding above and not just artist concentration.
- Bring valence, danceability, and liveness into the scoring recipe (currently descriptive-only), so more of the "vibe" attributes contribute alongside the categorical mood tag.
- Let a user combine two scoring modes (e.g., a genre-first/energy-focused blend) instead of picking exactly one strategy at a time.

---

## 9. Personal Reflection

The most useful thing this project made concrete is that a "recommendation" from a system like this is just a sorted list produced by adding up a few numbers — there's no hidden understanding of music, only whatever attributes got written into the CSV. The energy-similarity curve was the one design decision that had to be gotten right on purpose (rewarding *closeness* to a target rather than "more is better"), and testing it against an adversarial profile was what revealed the quieter bias: when the categorical signals (genre, mood) can't fire at all, the system doesn't fail loudly, it just silently narrows to ranking by the one remaining numeric feature. That's a small-scale version of a real concern with production recommenders — a system can look like it's working (returning a clean, confident-looking list) while actually operating on far less information than a user would assume.
