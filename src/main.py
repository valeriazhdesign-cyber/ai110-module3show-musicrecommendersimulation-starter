"""
Command line runner for the Music Recommender Simulation.

Loads the song catalog and runs several distinct user profiles through the
recommender so their outputs can be compared side by side.

Usage:
    python -m src.main                     # balanced mode (default)
    python -m src.main genre-first          # switch scoring mode
    python -m src.main mood-first --diversify
    python -m src.main --list-modes
"""

import sys
from tabulate import tabulate

from src.recommender import load_songs, recommend_songs, STRATEGIES

# Distinct taste profiles used to stress test the scoring logic (Phase 4).
USER_PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.85},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.35},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    # Adversarial: conflicting preferences (high energy + sad mood) with no
    # genre in the catalog that matches "screamo" -- tests whether the
    # system degrades gracefully when nothing matches well.
    "Adversarial Conflict": {"genre": "screamo", "mood": "sad", "energy": 0.9},
}


def print_recommendations(profile_name: str, user_prefs: dict, recommendations) -> None:
    print(f"=== {profile_name} (genre={user_prefs['genre']}, mood={user_prefs['mood']}, energy={user_prefs['energy']}) ===\n")
    rows = [
        [rank, song["title"], song["artist"], f"{score:.2f}", explanation]
        for rank, (song, score, explanation) in enumerate(recommendations, start=1)
    ]
    print(tabulate(rows, headers=["#", "Title", "Artist", "Score", "Reasons"], tablefmt="github"))
    print()


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    diversify = "--diversify" in sys.argv

    if "--list-modes" in sys.argv:
        print("Available scoring modes:", ", ".join(STRATEGIES.keys()))
        return

    mode = args[0] if args else "balanced"
    if mode not in STRATEGIES:
        print(f"Unknown mode '{mode}'. Available modes: {', '.join(STRATEGIES.keys())}")
        return
    strategy = STRATEGIES[mode]

    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print(f"Scoring mode: {strategy.name}" + (" (diversity penalty on)" if diversify else ""))
    print()

    for profile_name, user_prefs in USER_PROFILES.items():
        recommendations = recommend_songs(user_prefs, songs, k=5, strategy=strategy, diversify=diversify)
        print_recommendations(profile_name, user_prefs, recommendations)


if __name__ == "__main__":
    main()
