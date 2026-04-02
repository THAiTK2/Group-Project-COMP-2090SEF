"""Seed demo competition records via TeamManagementSystem service.

Usage:
    python3 scripts/seed_competitions.py
"""

from logic import TeamManagementSystem


def main():
    system = TeamManagementSystem()
    seeded = system.seed_demo_competitions(force=False)
    if seeded <= 0:
        existing_count = len(system.list_team_records())
        print(f"Skipped seeding: {existing_count} competition records already exist.")
        return

    print(f"Seeded {seeded} competition records.")


if __name__ == "__main__":
    main()
