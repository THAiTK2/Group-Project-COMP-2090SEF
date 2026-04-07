import sqlite3
from pathlib import Path


class DatabaseManager:
    """SQLite database manager for MSUTMS."""

    def __init__(self, db_path=None):
        base_dir = Path(__file__).resolve().parent
        self.db_path = Path(db_path) if db_path else base_dir / "msutms.db"
        self.initialize_schema()

    def get_connection(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON;")
        return connection

    def initialize_schema(self):
        with self.get_connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS students (
                    member_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    gpa REAL NOT NULL,
                    attendance_rate REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS coaches (
                    member_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    specialization TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS teachers (
                    member_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS teams (
                    team_name TEXT PRIMARY KEY,
                    sport_type TEXT NOT NULL,
                    coach_id TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    FOREIGN KEY (coach_id) REFERENCES coaches(member_id)
                        ON UPDATE CASCADE
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS team_members (
                    team_name TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    PRIMARY KEY (team_name, student_id),
                    FOREIGN KEY (team_name) REFERENCES teams(team_name)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES students(member_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS accounts (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL,
                    member_id TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS competition_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT NOT NULL,
                    sport_type TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    competition_name TEXT NOT NULL,
                    result TEXT NOT NULL CHECK(result IN ('win','loss','draw')),
                    opponent TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (team_name) REFERENCES teams(team_name)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                );
                """
            )
            self._migrate_competition_records_schema(connection)
            connection.commit()

    @staticmethod
    def _migrate_competition_records_schema(connection):
        """Hard-migrate legacy competition_records that still contain details_json."""
        columns = connection.execute("PRAGMA table_info(competition_records)").fetchall()
        column_names = {str(row["name"]) for row in columns}
        if "details_json" not in column_names:
            return

        connection.execute("PRAGMA foreign_keys = OFF;")
        connection.executescript(
            """
            CREATE TABLE competition_records_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_name TEXT NOT NULL,
                sport_type TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                competition_name TEXT NOT NULL,
                result TEXT NOT NULL CHECK(result IN ('win','loss','draw')),
                opponent TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (team_name) REFERENCES teams(team_name)
                    ON UPDATE CASCADE
                    ON DELETE CASCADE
            );

            INSERT INTO competition_records_new(
                id,
                team_name,
                sport_type,
                year,
                month,
                competition_name,
                result,
                opponent,
                created_at
            )
            SELECT
                id,
                team_name,
                sport_type,
                year,
                month,
                competition_name,
                CASE
                    WHEN lower(result) IN ('win','loss','draw') THEN lower(result)
                    ELSE 'draw'
                END,
                opponent,
                created_at
            FROM competition_records;

            DROP TABLE competition_records;
            ALTER TABLE competition_records_new RENAME TO competition_records;
            """
        )
        connection.execute("PRAGMA foreign_keys = ON;")
