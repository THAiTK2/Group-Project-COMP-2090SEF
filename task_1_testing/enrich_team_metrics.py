"""Enrich team performance extras in data.json.

Usage:
    python3 scripts/enrich_team_metrics.py
    python3 scripts/enrich_team_metrics.py /path/to/data.json
"""

import json
import sys
from pathlib import Path


def canonical_sport(raw_sport):
    mapping = {
        "FootballTeam": "football",
        "BasketballTeam": "basketball",
        "BadmintonTeam": "badminton",
        "SwimmingTeam": "swimming",
        "TrackAndFieldTeam": "track_and_field",
        "HandballTeam": "handball",
        "football": "football",
        "basketball": "basketball",
        "badminton": "badminton",
        "swimming": "swimming",
        "track_and_field": "track_and_field",
        "trackandfield": "track_and_field",
        "athletics": "track_and_field",
        "handball": "handball",
    }
    return mapping.get(str(raw_sport).strip(), str(raw_sport).strip())


def derive_extras(sport_type, metric):
    metric_value = float(metric)

    if sport_type == "football":
        return {
            "shots_on_target": round(max(metric_value * 2.4, 1.0), 2),
            "possession_rate": round(50.0 + min(metric_value * 0.9, 25.0), 2),
            "pass_accuracy": round(75.0 + min(metric_value * 0.7, 15.0), 2),
        }

    if sport_type == "basketball":
        return {
            "assists_per_game": round(max(metric_value * 0.22, 5.0), 2),
            "rebounds_per_game": round(max(metric_value * 0.45, 10.0), 2),
            "turnovers_per_game": round(max(metric_value * 0.12, 3.0), 2),
        }

    if sport_type == "badminton":
        return {
            "smash_win_rate": round(min(metric_value * 0.75, 100.0), 2),
            "unforced_errors": round(max(20.0 - metric_value * 0.12, 2.0), 2),
        }

    if sport_type == "swimming":
        return {
            "relay_points": round(max(metric_value * 0.55, 4.0), 2),
            "avg_finish_rank": round(max(8.0 - metric_value * 0.08, 1.0), 2),
        }

    if sport_type == "track_and_field":
        return {
            "gold_medals": round(max(metric_value * 0.45, 0.0), 2),
            "podium_finishes": round(max(metric_value * 1.4, 1.0), 2),
            "season_best_count": round(max(metric_value * 1.7, 1.0), 2),
        }

    if sport_type == "handball":
        return {
            "save_rate": round(min(25.0 + metric_value * 0.9, 60.0), 2),
            "fast_break_goals": round(max(metric_value * 0.35, 0.5), 2),
            "foul_rate": round(max(12.0 - metric_value * 0.18, 2.0), 2),
        }

    return {}


def enrich_dataset(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    teams = payload.get("teams", [])
    updated = 0

    for team in teams:
        sport_type = canonical_sport(team.get("sport", team.get("sport_type", "")))
        metric = team.get("metric")
        if metric is None:
            continue

        extras = derive_extras(sport_type, metric)
        if not extras:
            continue

        current_extras = team.get("extras", {})
        if not isinstance(current_extras, dict):
            current_extras = {}

        current_extras.update(extras)
        team["extras"] = current_extras
        team["sport_type"] = sport_type
        updated += 1

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return updated


def main():
    if len(sys.argv) > 1:
        file_path = Path(sys.argv[1]).expanduser().resolve()
    else:
        file_path = Path(__file__).resolve().parents[1] / "data.json"

    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    count = enrich_dataset(file_path)
    print(f"Enriched {count} teams in {file_path}")


if __name__ == "__main__":
    main()
