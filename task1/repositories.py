import sqlite3


class TeamManagementRepository:
    # Repository layer for create, read, update, delete operations
    DASHBOARD_TABLES = (
        "students",
        "teachers",
        "coaches",
        "teams",
        "team_members",
        "accounts",
        "competition_records",
    )

    TABLE_SORT_KEY = {
        "students": "member_id",
        "teachers": "member_id",
        "coaches": "member_id",
        "teams": "team_name",
        "team_members": "team_name, student_id",
        "accounts": "username",
        "competition_records": "year DESC, month DESC, competition_name ASC",
    }

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _execute(self, query, params=()):
        with self.db_manager.get_connection() as connection:
            connection.execute(query, params)
            connection.commit()

    def _fetchone(self, query, params=()):
        with self.db_manager.get_connection() as connection:
            return connection.execute(query, params).fetchone()

    def _fetchall(self, query, params=()):
        with self.db_manager.get_connection() as connection:
            return connection.execute(query, params).fetchall()

    # students part
    def add_student(self, name, member_id, gpa, attendance_rate):
        try:
            self._execute(
                """
                INSERT INTO students(member_id, name, gpa, attendance_rate)
                VALUES (?, ?, ?, ?)
                """,
                (member_id, name, float(gpa), float(attendance_rate)),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Student ID '{member_id}' already exists.") from error

    def add_student_with_account(
        self,
        name,
        member_id,
        gpa,
        attendance_rate,
        username,
        password,
        role="student",
    ):
        # Transactional create:
        # create student and account together, rollback if any step fails.
        try:
            with self.db_manager.get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO students(member_id, name, gpa, attendance_rate)
                    VALUES (?, ?, ?, ?)
                    """,
                    (member_id, name, float(gpa), float(attendance_rate)),
                )
                connection.execute(
                    """
                    INSERT INTO accounts(username, password, role, member_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, password, role, member_id),
                )
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "accounts.username" in message:
                raise ValueError(f"Username '{username}' already exists.") from error
            if "students.member_id" in message:
                raise ValueError(f"Student ID '{member_id}' already exists.") from error
            raise

    def update_student(self, member_id, name=None, gpa=None, attendance_rate=None):
        row = self.get_student(member_id)
        if row is None:
            raise ValueError(f"Student ID '{member_id}' not found.")

        updated_name = name if name is not None else row["name"]
        updated_gpa = float(gpa) if gpa is not None else float(row["gpa"])
        updated_attendance = (
            float(attendance_rate)
            if attendance_rate is not None
            else float(row["attendance_rate"])
        )
        self._execute(
            """
            UPDATE students
            SET name = ?, gpa = ?, attendance_rate = ?
            WHERE member_id = ?
            """,
            (updated_name, updated_gpa, updated_attendance, member_id),
        )

    def get_student(self, member_id):
        return self._fetchone(
            "SELECT * FROM students WHERE member_id = ?",
            (member_id,),
        )

    def list_students(self):
        return self._fetchall("SELECT * FROM students ORDER BY member_id")

    def list_students_without_account(self):
        return self._fetchall(
            """
            SELECT s.member_id
            FROM students s
            LEFT JOIN accounts a
                ON a.member_id = s.member_id
               AND lower(a.role) = 'student'
            WHERE a.username IS NULL
            ORDER BY s.member_id
            """
        )

    def delete_student(self, member_id):
        self._execute(
            "DELETE FROM students WHERE member_id = ?",
            (member_id,),
        )

    def delete_student_with_account(self, member_id):
        # Transactional delete:
        # remove student account and student record together.
        with self.db_manager.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM accounts
                WHERE member_id = ? AND lower(role) = 'student'
                """,
                (member_id,),
            )
            connection.execute(
                "DELETE FROM students WHERE member_id = ?",
                (member_id,),
            )

    # coaches 
    def add_coach(self, name, member_id, specialization):
        try:
            self._execute(
                """
                INSERT INTO coaches(member_id, name, specialization)
                VALUES (?, ?, ?)
                """,
                (member_id, name, specialization),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Coach ID '{member_id}' already exists.") from error

    def add_coach_with_account(
        self,
        name,
        member_id,
        specialization,
        username,
        password,
        role="coach",
    ):
        # Transactional create:
        # create coach and account together, rollback if any step fails.
        try:
            with self.db_manager.get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO coaches(member_id, name, specialization)
                    VALUES (?, ?, ?)
                    """,
                    (member_id, name, specialization),
                )
                connection.execute(
                    """
                    INSERT INTO accounts(username, password, role, member_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, password, role, member_id),
                )
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "accounts.username" in message:
                raise ValueError(f"Username '{username}' already exists.") from error
            if "coaches.member_id" in message:
                raise ValueError(f"Coach ID '{member_id}' already exists.") from error
            raise

    def update_coach(self, member_id, name=None, specialization=None):
        row = self.get_coach(member_id)
        if row is None:
            raise ValueError(f"Coach ID '{member_id}' not found.")

        updated_name = name if name is not None else row["name"]
        updated_spec = specialization if specialization is not None else row["specialization"]
        self._execute(
            """
            UPDATE coaches
            SET name = ?, specialization = ?
            WHERE member_id = ?
            """,
            (updated_name, updated_spec, member_id),
        )

    def get_coach(self, member_id):
        return self._fetchone(
            "SELECT * FROM coaches WHERE member_id = ?",
            (member_id,),
        )

    def list_coaches(self):
        return self._fetchall("SELECT * FROM coaches ORDER BY member_id")

    def list_coaches_without_account(self):
        return self._fetchall(
            """
            SELECT c.member_id
            FROM coaches c
            LEFT JOIN accounts a
                ON a.member_id = c.member_id
               AND lower(a.role) = 'coach'
            WHERE a.username IS NULL
            ORDER BY c.member_id
            """
        )

    def delete_coach(self, member_id):
        self._execute(
            "DELETE FROM coaches WHERE member_id = ?",
            (member_id,),
        )

    def coach_has_team(self, member_id):
        row = self._fetchone(
            """
            SELECT 1
            FROM teams
            WHERE coach_id = ?
            LIMIT 1
            """,
            (member_id,),
        )
        return row is not None

    def delete_coach_with_account(self, member_id):
        # Transactional delete:
        # remove coach account and coach record together.
        try:
            with self.db_manager.get_connection() as connection:
                connection.execute(
                    """
                    DELETE FROM accounts
                    WHERE member_id = ? AND lower(role) = 'coach'
                    """,
                    (member_id,),
                )
                connection.execute(
                    "DELETE FROM coaches WHERE member_id = ?",
                    (member_id,),
                )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"Coach ID '{member_id}' cannot be deleted because teams still reference this coach."
            ) from error

    # teachers part
    def add_teacher(self, name, member_id, department):
        try:
            self._execute(
                """
                INSERT INTO teachers(member_id, name, department)
                VALUES (?, ?, ?)
                """,
                (member_id, name, department),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Teacher ID '{member_id}' already exists.") from error

    def add_teacher_with_account(
        self,
        name,
        member_id,
        department,
        username,
        password,
        role="teacher",
    ):
        # Transactional create:
        # create teacher and account together, rollback if any step fails.
        try:
            with self.db_manager.get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO teachers(member_id, name, department)
                    VALUES (?, ?, ?)
                    """,
                    (member_id, name, department),
                )
                connection.execute(
                    """
                    INSERT INTO accounts(username, password, role, member_id)
                    VALUES (?, ?, ?, ?)
                    """,
                    (username, password, role, member_id),
                )
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "accounts.username" in message:
                raise ValueError(f"Username '{username}' already exists.") from error
            if "teachers.member_id" in message:
                raise ValueError(f"Teacher ID '{member_id}' already exists.") from error
            raise

    def get_teacher(self, member_id):
        return self._fetchone(
            "SELECT * FROM teachers WHERE member_id = ?",
            (member_id,),
        )

    def list_teachers(self):
        return self._fetchall("SELECT * FROM teachers ORDER BY member_id")

    def delete_teacher(self, member_id):
        self._execute(
            "DELETE FROM teachers WHERE member_id = ?",
            (member_id,),
        )

    def delete_teacher_with_account(self, member_id):
        # Transactional delete:
        # remove teacher account and teacher record together.
        with self.db_manager.get_connection() as connection:
            connection.execute(
                """
                DELETE FROM accounts
                WHERE member_id = ? AND lower(role) = 'teacher'
                """,
                (member_id,),
            )
            connection.execute(
                "DELETE FROM teachers WHERE member_id = ?",
                (member_id,),
            )

    # accounts 
    def add_account(self, username, password, role, member_id):
        try:
            self._execute(
                """
                INSERT INTO accounts(username, password, role, member_id)
                VALUES (?, ?, ?, ?)
                """,
                (username, password, role, member_id),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Username '{username}' already exists.") from error

    def get_account(self, username):
        return self._fetchone(
            "SELECT * FROM accounts WHERE username = ?",
            (username,),
        )

    def update_account_password(self, username, new_password):
        self._execute(
            "UPDATE accounts SET password = ? WHERE username = ?",
            (new_password, username),
        )

    def find_account_by_role_member(self, role, member_id):
        return self._fetchone(
            """
            SELECT * FROM accounts
            WHERE role = ? AND member_id = ?
            LIMIT 1
            """,
            (role, member_id),
        )

    def list_accounts(self):
        return self._fetchall("SELECT * FROM accounts ORDER BY username")

    def delete_accounts_by_role(self, role):
        self._execute(
            "DELETE FROM accounts WHERE lower(role) = ?",
            (str(role).strip().lower(),),
        )

    # teams 
    def add_team(self, team_name, sport_type, coach_id, metric_value):
        try:
            self._execute(
                """
                INSERT INTO teams(team_name, sport_type, coach_id, metric_value)
                VALUES (?, ?, ?, ?)
                """,
                (team_name, sport_type, coach_id, float(metric_value)),
            )
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "teams.team_name" in message:
                raise ValueError(f"Team '{team_name}' already exists.") from error
            raise ValueError(f"Coach ID '{coach_id}' not found.") from error

    def get_team(self, team_name):
        return self._fetchone(
            "SELECT * FROM teams WHERE team_name = ?",
            (team_name,),
        )

    def list_teams(self):
        return self._fetchall("SELECT * FROM teams ORDER BY team_name")

    def delete_team(self, team_name):
        self._execute(
            "DELETE FROM teams WHERE team_name = ?",
            (team_name,),
        )

    def delete_teams_by_coach_id(self, coach_id):
        self._execute(
            "DELETE FROM teams WHERE coach_id = ?",
            (coach_id,),
        )

    def update_team(self, team_name, coach_id=None, metric_value=None):
        row = self.get_team(team_name)
        if row is None:
            raise ValueError(f"Team '{team_name}' not found.")

        updated_coach_id = coach_id if coach_id is not None else row["coach_id"]
        updated_metric = float(metric_value) if metric_value is not None else float(row["metric_value"])

        try:
            self._execute(
                """
                UPDATE teams
                SET coach_id = ?, metric_value = ?
                WHERE team_name = ?
                """,
                (updated_coach_id, updated_metric, team_name),
            )
        except sqlite3.IntegrityError as error:
            raise ValueError(f"Coach ID '{updated_coach_id}' not found.") from error

    # team members part
    def add_team_member(self, team_name, student_id):
        try:
            self._execute(
                """
                INSERT INTO team_members(team_name, student_id)
                VALUES (?, ?)
                """,
                (team_name, student_id),
            )
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "UNIQUE" in message or "PRIMARY KEY" in message:
                return
            if "team_members.team_name" in message:
                raise ValueError(f"Team '{team_name}' not found.") from error
            raise ValueError(f"Student ID '{student_id}' not found.") from error

    def list_team_members(self, team_name=None):
        if team_name is None:
            return self._fetchall(
                "SELECT team_name, student_id FROM team_members ORDER BY team_name, student_id"
            )

        return self._fetchall(
            """
            SELECT team_name, student_id
            FROM team_members
            WHERE team_name = ?
            ORDER BY student_id
            """,
            (team_name,),
        )

    # maintenance part
    def clear_all(self):
        with self.db_manager.get_connection() as connection:
            connection.execute("DELETE FROM competition_records")
            connection.execute("DELETE FROM team_members")
            connection.execute("DELETE FROM teams")
            connection.execute("DELETE FROM accounts")
            connection.execute("DELETE FROM students")
            connection.execute("DELETE FROM coaches")
            connection.execute("DELETE FROM teachers")
            connection.commit()

    # competition records part
    def add_competition_record(
        self,
        team_name,
        sport_type,
        year,
        month,
        competition_name,
        result,
        opponent,
    ):
        self._execute(
            """
            INSERT INTO competition_records(
                team_name,
                sport_type,
                year,
                month,
                competition_name,
                result,
                opponent
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                team_name,
                sport_type,
                int(year),
                int(month),
                competition_name,
                result,
                opponent,
            ),
        )

    def list_competition_records(
        self,
        team_name=None,
        year=None,
        month=None,
        competition_name=None,
    ):
        conditions = []
        params = []

        if team_name:
            conditions.append("team_name = ?")
            params.append(team_name)
        if year is not None:
            conditions.append("year = ?")
            params.append(int(year))
        if month is not None:
            conditions.append("month = ?")
            params.append(int(month))
        if competition_name:
            conditions.append("competition_name LIKE ?")
            params.append(f"%{competition_name}%")

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT *
            FROM competition_records
            {where_clause}
            ORDER BY year DESC, month DESC, competition_name ASC, id ASC
        """
        return self._fetchall(query, tuple(params))

    def get_competition_record_by_id(self, record_id):
        return self._fetchone(
            "SELECT * FROM competition_records WHERE id = ?",
            (int(record_id),),
        )

    def delete_competition_record(self, record_id):
        self._execute(
            "DELETE FROM competition_records WHERE id = ?",
            (int(record_id),),
        )

    def get_team_win_loss_summary(self, team_name=None, year=None, month=None):
        conditions = []
        params = []

        if team_name:
            conditions.append("team_name = ?")
            params.append(team_name)
        if year is not None:
            conditions.append("year = ?")
            params.append(int(year))
        if month is not None:
            conditions.append("month = ?")
            params.append(int(month))

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT
                team_name,
                SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) AS wins,
                SUM(CASE WHEN result = 'loss' THEN 1 ELSE 0 END) AS losses,
                SUM(CASE WHEN result = 'draw' THEN 1 ELSE 0 END) AS draws,
                COUNT(*) AS total_matches
            FROM competition_records
            {where_clause}
            GROUP BY team_name
            ORDER BY team_name ASC
        """
        return self._fetchall(query, tuple(params))

    # dashboard part
    def list_table_columns(self, table_name):
        normalized_table = self._validate_dashboard_table(table_name)
        rows = self._fetchall(f"PRAGMA table_info({normalized_table})")
        return [row["name"] for row in rows]

    def list_table_rows(self, table_name):
        normalized_table = self._validate_dashboard_table(table_name)
        order_by = self.TABLE_SORT_KEY[normalized_table]
        query = f"SELECT * FROM {normalized_table} ORDER BY {order_by}"
        return self._fetchall(query)

    def get_dashboard_snapshot(self):
        snapshot = {}
        for table_name in self.DASHBOARD_TABLES:
            snapshot[table_name] = self.list_table_rows(table_name)
        return snapshot

    def count_rows(self, table_name):
        normalized_table = self._validate_dashboard_table(table_name)
        row = self._fetchone(f"SELECT COUNT(*) AS count FROM {normalized_table}")
        return int(row["count"])

    def get_table_counts(self, table_names):
        return {
            table_name: self.count_rows(table_name)
            for table_name in table_names
        }

    def _validate_dashboard_table(self, table_name):
        normalized_table = str(table_name).strip().lower()
        if normalized_table not in self.DASHBOARD_TABLES:
            raise ValueError(f"Unsupported table for dashboard: {table_name}")
        return normalized_table
