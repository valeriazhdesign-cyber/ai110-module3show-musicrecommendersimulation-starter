import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

# --- Algorithm Recipe ---
# Weights live inside ScoringStrategy instances (see below) instead of module
# constants, so a "mode" can be swapped without touching the scoring code
# itself (Challenge 2: Strategy pattern). BALANCED is the original recipe
# from Phase 2/3.


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py

    The five fields below `acousticness` are Challenge 1 additions
    (advanced song features). They default so existing callers/tests that
    only pass the original fields keep working unchanged.
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: str = "2020s"
    mood_tags: str = ""  # semicolon-separated, e.g. "nostalgic;calm"
    instrumentalness: float = 0.0
    liveness: float = 0.0

    def mood_tag_list(self) -> List[str]:
        return [tag for tag in self.mood_tags.split(";") if tag]


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    The three Optional fields are Challenge 1 additions so a user can
    (optionally) express a taste for a decade, a detailed mood tag, or
    instrumental music. They default to "no preference" so existing tests
    that only pass the original four fields keep working unchanged.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_decade: Optional[str] = None
    favorite_mood_tag: Optional[str] = None
    prefers_instrumental: bool = False


# ---------------------------------------------------------------------------
# Challenge 2: Multiple Scoring Modes (Strategy pattern)
#
# Rather than one subclass per mode (which would duplicate the scoring
# arithmetic four times), each "strategy" is the same algorithm parameterized
# by a different weights dict. They're still fully interchangeable objects
# with a common `score()` interface, which is the part of the Strategy
# pattern that actually matters here: recommend_songs()/Recommender.recommend()
# depend only on that interface, not on which mode is active.
# ---------------------------------------------------------------------------
class ScoringStrategy:
    """A named, swappable set of weights for turning matches into points."""

    def __init__(self, name: str, weights: Dict[str, float]):
        self.name = name
        self.weights = weights

    def _energy_points(self, song_energy: float, target_energy: float) -> float:
        similarity = max(0.0, 1.0 - abs(song_energy - target_energy))
        return round(similarity * self.weights["energy"], 4)

    def score_dict(self, user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
        w = self.weights
        score = 0.0
        reasons: List[str] = []

        if "genre" in user_prefs and song.get("genre") == user_prefs["genre"]:
            score += w["genre"]
            reasons.append(f"genre match (+{w['genre']})")

        if "mood" in user_prefs and song.get("mood") == user_prefs["mood"]:
            score += w["mood"]
            reasons.append(f"mood match (+{w['mood']})")

        if "energy" in user_prefs and "energy" in song:
            pts = self._energy_points(float(song["energy"]), float(user_prefs["energy"]))
            if pts > 0:
                score += pts
                reasons.append(f"energy similarity (+{pts})")

        mood_tag = user_prefs.get("mood_tag")
        if mood_tag and mood_tag in str(song.get("mood_tags", "")).split(";"):
            score += w["mood_tag"]
            reasons.append(f"mood tag match (+{w['mood_tag']})")

        decade = user_prefs.get("decade")
        if decade and decade == song.get("release_decade"):
            score += w["decade"]
            reasons.append(f"decade match (+{w['decade']})")

        if "popularity" in song:
            pts = round((float(song["popularity"]) / 100.0) * w["popularity"], 4)
            if pts > 0:
                score += pts
                reasons.append(f"popularity bonus (+{pts})")

        if user_prefs.get("prefers_instrumental") and float(song.get("instrumentalness", 0)) >= 0.5:
            score += w["instrumental"]
            reasons.append(f"instrumental preference match (+{w['instrumental']})")

        if "likes_acoustic" in user_prefs:
            is_acoustic = float(song.get("acousticness", 0)) >= 0.5
            if user_prefs["likes_acoustic"] == is_acoustic:
                score += w["acoustic"]
                reasons.append(f"acousticness preference match (+{w['acoustic']})")

        return round(score, 4), reasons

    def score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        w = self.weights
        score = 0.0
        reasons: List[str] = []

        if song.genre == user.favorite_genre:
            score += w["genre"]
            reasons.append(f"genre match (+{w['genre']})")

        if song.mood == user.favorite_mood:
            score += w["mood"]
            reasons.append(f"mood match (+{w['mood']})")

        pts = self._energy_points(song.energy, user.target_energy)
        if pts > 0:
            score += pts
            reasons.append(f"energy similarity (+{pts})")

        if user.favorite_mood_tag and user.favorite_mood_tag in song.mood_tag_list():
            score += w["mood_tag"]
            reasons.append(f"mood tag match (+{w['mood_tag']})")

        if user.target_decade and user.target_decade == song.release_decade:
            score += w["decade"]
            reasons.append(f"decade match (+{w['decade']})")

        pop_pts = round((song.popularity / 100.0) * w["popularity"], 4)
        if pop_pts > 0:
            score += pop_pts
            reasons.append(f"popularity bonus (+{pop_pts})")

        if user.prefers_instrumental and song.instrumentalness >= 0.5:
            score += w["instrumental"]
            reasons.append(f"instrumental preference match (+{w['instrumental']})")

        is_acoustic = song.acousticness >= 0.5
        if user.likes_acoustic == is_acoustic:
            score += w["acoustic"]
            reasons.append(f"acousticness preference match (+{w['acoustic']})")

        return round(score, 4), reasons


# The original Phase 2/3 recipe: genre matters most, mood second, energy a
# close-similarity bonus. New Challenge 1 attributes are weighted lightly so
# they nudge results without overriding the core recipe.
BALANCED = ScoringStrategy("balanced", {
    "genre": 2.0, "mood": 1.0, "energy": 1.5,
    "mood_tag": 1.0, "decade": 0.5, "popularity": 0.5,
    "instrumental": 0.5, "acoustic": 0.5,
})

# Genre-First: leans hard on genre, everything else is a tiebreaker.
GENRE_FIRST = ScoringStrategy("genre-first", {
    "genre": 4.0, "mood": 0.5, "energy": 1.0,
    "mood_tag": 0.5, "decade": 0.25, "popularity": 0.25,
    "instrumental": 0.25, "acoustic": 0.25,
})

# Mood-First: mood and detailed mood tags dominate over genre.
MOOD_FIRST = ScoringStrategy("mood-first", {
    "genre": 0.5, "mood": 3.0, "energy": 1.0,
    "mood_tag": 2.0, "decade": 0.25, "popularity": 0.25,
    "instrumental": 0.25, "acoustic": 0.25,
})

# Energy-Focused: closeness to the target energy dominates the score.
ENERGY_FOCUSED = ScoringStrategy("energy-focused", {
    "genre": 0.5, "mood": 0.5, "energy": 3.5,
    "mood_tag": 0.5, "decade": 0.25, "popularity": 0.25,
    "instrumental": 0.25, "acoustic": 0.25,
})

STRATEGIES: Dict[str, ScoringStrategy] = {
    s.name: s for s in (BALANCED, GENRE_FIRST, MOOD_FIRST, ENERGY_FOCUSED)
}


def _artist_of(song) -> str:
    return song.artist if isinstance(song, Song) else song.get("artist", "")


def _apply_diversity_penalty(scored: List[Tuple], k: int, artist_penalty: float) -> List[Tuple]:
    """
    Challenge 3: Diversity and Fairness Logic.

    Greedily re-ranks candidates so that repeated picks from the same artist
    cost progressively more (linear penalty scaling with how many of that
    artist are already selected), instead of hard-blocking repeats outright.
    """
    remaining = list(scored)
    picked: List[Tuple] = []
    artist_counts: Dict[str, int] = {}

    while remaining and len(picked) < k:
        best_index = None
        best_effective_score = None
        for i, (song, score, explanation) in enumerate(remaining):
            count = artist_counts.get(_artist_of(song), 0)
            effective_score = score - artist_penalty * count
            if best_effective_score is None or effective_score > best_effective_score:
                best_effective_score = effective_score
                best_index = i
        song, score, explanation = remaining.pop(best_index)
        artist_counts[_artist_of(song)] = artist_counts.get(_artist_of(song), 0) + 1
        picked.append((song, score, explanation))

    return picked


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(
        self,
        user: UserProfile,
        k: int = 5,
        strategy: Optional[ScoringStrategy] = None,
        diversify: bool = False,
        artist_penalty: float = 1.5,
    ) -> List[Song]:
        strategy = strategy or BALANCED
        scored = [
            (song, *strategy.score_song(user, song))
            for song in self.songs
        ]
        # normalize to (song, score, reasons) then to the tuple shape the
        # diversity helper expects: (song, score, explanation)
        scored = [(song, score, ", ".join(reasons)) for song, score, reasons in scored]
        scored.sort(key=lambda item: item[1], reverse=True)

        if diversify:
            top = _apply_diversity_penalty(scored, k, artist_penalty)
        else:
            top = scored[:k]

        return [song for song, _, _ in top]

    def explain_recommendation(self, user: UserProfile, song: Song, strategy: Optional[ScoringStrategy] = None) -> str:
        strategy = strategy or BALANCED
        score, reasons = strategy.score_song(user, song)
        if not reasons:
            return f"Score {score}: no strong matches with this user's preferences."
        return f"Score {score}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    numeric_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness",
                       "popularity", "instrumentalness", "liveness")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = dict(row)
            song["id"] = int(song["id"])
            for field_name in numeric_fields:
                if field_name in song:
                    song[field_name] = float(song[field_name])
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict, strategy: Optional[ScoringStrategy] = None) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    strategy = strategy or BALANCED
    return strategy.score_dict(user_prefs, song)


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    strategy: Optional[ScoringStrategy] = None,
    diversify: bool = False,
    artist_penalty: float = 1.5,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    strategy = strategy or BALANCED
    scored = []
    for song in songs:
        score, reasons = strategy.score_dict(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)

    if diversify:
        return _apply_diversity_penalty(scored, k, artist_penalty)
    return scored[:k]
