import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# GUI check
# it stop early with clear message so users know how to install missing package.
try:
    import customtkinter as ctk
except ImportError as error:
    raise SystemExit("CustomTkinter is required. Install with: pip install customtkinter") from error

from logic import TeamManagementSystem
from repositories import TeamManagementRepository


# Application root 
# develop MSUTMSApp window
class MSUTMSApp(ctk.CTk):
    """Desktop GUI for MSUTMS."""

    def __init__(self):
        super().__init__()
        #service object handles all business logic and SQL operations.
        self.system = TeamManagementSystem()
        self.current_account = None

        self.title("MSUTMS - Multi-Sport University Team Management System")
        self.geometry("1360x860")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # container holds all pages. we create a simple page navigation at page
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=16, pady=16)

        self.frames = {}
        for frame_class in (LoginFrame, StaffDashboardFrame):
            # create all frames once and keep them in memory for fast switching
            frame = frame_class(parent=self.container, app=self)
            self.frames[frame_class.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame("LoginFrame")

    def show_frame(self, frame_name):
        # bring selected page to front
        self.frames[frame_name].tkraise()

    def logout(self):
        # clear current session and reset login form
        self.current_account = None
        self.frames["LoginFrame"].reset_form()
        self.show_frame("LoginFrame")


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        title = ctk.CTkLabel(self,text="MSUTMS Login",font=ctk.CTkFont(size=30, weight="bold"),)
        title.pack(pady=(80, 30))

        card = ctk.CTkFrame(self)
        card.pack(pady=12, padx=20)

        ctk.CTkLabel(card, text="Username").grid(row=0, column=0, padx=12, pady=10, sticky="w")
        self.username_entry = ctk.CTkEntry(card, width=280)
        self.username_entry.grid(row=0, column=1, padx=12, pady=10)

        ctk.CTkLabel(card, text="Password").grid(row=1, column=0, padx=12, pady=10, sticky="w")
        self.password_entry = ctk.CTkEntry(card, width=280, show="*")
        self.password_entry.grid(row=1, column=1, padx=12, pady=10)

        login_button = ctk.CTkButton(card, text="Login", command=self._login)
        login_button.grid(row=2, column=0, columnspan=2, pady=16)

        

    def _login(self):
        # read and normalize input from login form
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        try:
            # authentication is done in service layer
            account = self.app.system.authenticate(username, password)

            # staff-only policy: only teacher/coach can access management dashboard
            if not self.app.system.is_staff_role(account.role):
                raise ValueError("Only teacher/coach accounts can access management GUI.")

            self.app.current_account = account
            staff_frame = self.app.frames["StaffDashboardFrame"]
            staff_frame.set_account(account)
            self.app.show_frame("StaffDashboardFrame")

        except Exception as error:  
            messagebox.showerror("Login Failed", str(error))

    def reset_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)


class StaffDashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.header_label = ctk.CTkLabel(
            self,
            text="Staff Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.header_label.pack(pady=(10, 8))

        top_bar = ctk.CTkFrame(self)
        top_bar.pack(fill="x", padx=8, pady=(0, 8))
        ctk.CTkButton(top_bar, text="Logout", command=self.app.logout).pack(
            side="right", padx=8, pady=8
        )

        # the tab-base and layout
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_add = self.tabs.add("Add Data")
        self.tab_team = self.tabs.add("Team Operation")
        self.tab_update = self.tabs.add("Update")
        self.tab_competition = self.tabs.add("Competition Records")
        self.tab_reports = self.tabs.add("Reports")
        self.tab_sql = self.tabs.add("SQL Data")

        self._build_add_tab()
        self._build_team_tab()
        self._build_update_tab()
        self._build_competition_tab()
        self._build_reports_tab()
        self._build_sql_tab()

    def set_account(self, account):
        # show current role/user in header for quick context.
        self.header_label.configure(
            text=f"Staff Dashboard - {account.role.title()} ({account.username})"
        )
        self._refresh_all_views()

    #  Add tab 
    def _build_add_tab(self):
        # add tab provides create operations for three member types
        frame = self.tab_add
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        student_box = ctk.CTkFrame(frame)
        student_box.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(student_box, text="Add Student", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.stu_name = self._labeled_entry(student_box, "Name")
        self.stu_id = self._labeled_entry(student_box, "Member ID")
        self.stu_gpa = self._labeled_entry(student_box, "GPA (0-4)")
        self.stu_att = self._labeled_entry(student_box, "Attendance (0-100)")

        ctk.CTkButton(student_box, text="Add Student", command=self._add_student).pack(pady=8)

        coach_box = ctk.CTkFrame(frame)
        coach_box.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(coach_box, text="Add Coach", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.coach_name = self._labeled_entry(coach_box, "Name")
        self.coach_id = self._labeled_entry(coach_box, "Member ID")
        self.coach_spec = self._labeled_entry(coach_box, "Specialization")
        self.coach_user = self._labeled_entry(coach_box, "Username (required)")
        self.coach_pass = self._labeled_entry(coach_box, "Password (required)", show="*")

        ctk.CTkButton(coach_box, text="Add Coach", command=self._add_coach).pack(pady=8)

        teacher_box = ctk.CTkFrame(frame)
        teacher_box.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(teacher_box, text="Add Teacher", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.teacher_name = self._labeled_entry(teacher_box, "Name")
        self.teacher_id = self._labeled_entry(teacher_box, "Member ID")
        self.teacher_dept = self._labeled_entry(teacher_box, "Department")
        self.teacher_user = self._labeled_entry(teacher_box, "Username (required)")
        self.teacher_pass = self._labeled_entry(teacher_box, "Password (required)", show="*")

        ctk.CTkButton(teacher_box, text="Add Teacher", command=self._add_teacher).pack(pady=8)

        info_box = ctk.CTkFrame(frame)
        info_box.grid(row=0, column=3, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(info_box, text="Hint", font=ctk.CTkFont(weight="bold")).pack(pady=6)
        hint_text = (
            "- Student GPA >= 2.0 can join team\n"
            "- Student has no login account\n"
            "- Management login: teacher / coach only\n"
            "- Supported account roles: teacher, coach\n"
            "- Password at least 4 chars"
        )
        ctk.CTkLabel(info_box, text=hint_text, justify="left").pack(padx=8, pady=8)

    # Team tab 
    def _build_team_tab(self):
        # team tab handles team creation and student-team assignment
        frame = self.tab_team
        frame.grid_columnconfigure((0, 1), weight=1)

        create_box = ctk.CTkFrame(frame)
        create_box.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(create_box, text="Create Team", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.team_sport = self._labeled_entry(create_box, "Sport Type")
        self.team_name = self._labeled_entry(create_box, "Team Name")
        self.team_coach_id = self._labeled_entry(create_box, "Coach ID")
        self.team_metric = self._labeled_entry(create_box, "Metric Value")

        sport_hint = "football/basketball/badminton/swimming/track_and_field/handball"
        ctk.CTkLabel(create_box, text=sport_hint, text_color="gray").pack(pady=(0, 6))

        ctk.CTkButton(create_box, text="Create Team", command=self._create_team).pack(pady=8)

        assign_box = ctk.CTkFrame(frame)
        assign_box.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(assign_box, text="Assign Student to Team", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.assign_student_id = self._labeled_entry(assign_box, "Student ID")
        self.assign_team_name = self._labeled_entry(assign_box, "Team Name")

        ctk.CTkButton(assign_box, text="Assign", command=self._assign_student).pack(pady=8)

    # Update tab 
    def _build_update_tab(self):
        # update tab supports correction of existing records
        update_scroll = ctk.CTkScrollableFrame(self.tab_update)
        update_scroll.pack(fill="both", expand=True, padx=8, pady=8)
        frame = update_scroll
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        update_student_box = ctk.CTkFrame(frame)
        update_student_box.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(update_student_box, text="Update Student", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.up_stu_id = self._labeled_entry(update_student_box, "Member ID")
        self.up_stu_name = self._labeled_entry(update_student_box, "New Name (optional)")
        self.up_stu_gpa = self._labeled_entry(update_student_box, "New GPA (optional)")
        self.up_stu_att = self._labeled_entry(update_student_box, "New Attendance (optional)")
        ctk.CTkButton(update_student_box, text="Update Student", command=self._update_student).pack(pady=8)

        update_coach_box = ctk.CTkFrame(frame)
        update_coach_box.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(update_coach_box, text="Update Coach", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.up_coach_id = self._labeled_entry(update_coach_box, "Member ID")
        self.up_coach_name = self._labeled_entry(update_coach_box, "New Name (optional)")
        self.up_coach_spec = self._labeled_entry(update_coach_box, "New Specialization (optional)")
        self.up_coach_pass = self._labeled_entry(update_coach_box, "New Password (optional)", show="*")
        ctk.CTkButton(update_coach_box, text="Update Coach", command=self._update_coach).pack(pady=8)

        update_team_box = ctk.CTkFrame(frame)
        update_team_box.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(update_team_box, text="Update Team", font=ctk.CTkFont(weight="bold")).pack(pady=6)

        self.up_team_name = self._labeled_entry(update_team_box, "Team Name")
        self.up_team_coach = self._labeled_entry(update_team_box, "New Coach ID (optional)")
        self.up_team_metric = self._labeled_entry(update_team_box, "New Metric (optional)")
        ctk.CTkButton(update_team_box, text="Update Team", command=self._update_team).pack(pady=8)

        update_competition_box = ctk.CTkFrame(frame)
        update_competition_box.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            update_competition_box,
            text="Update Competition",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=6)
        self.up_comp_id = self._labeled_entry(update_competition_box, "Record ID")
        self.up_comp_year = self._labeled_entry(update_competition_box, "New Year (optional)")
        self.up_comp_month = self._labeled_entry(update_competition_box, "New Month (optional)")
        self.up_comp_name = self._labeled_entry(
            update_competition_box,
            "New Competition Name (optional)",
        )
        ctk.CTkLabel(update_competition_box, text="New Result (optional)").pack(
            anchor="w",
            padx=8,
            pady=(4, 0),
        )
        self.up_comp_result_var = tk.StringVar(value="(no change)")
        self.up_comp_result_menu = ctk.CTkOptionMenu(
            update_competition_box,
            values=["(no change)", "win", "loss", "draw"],
            variable=self.up_comp_result_var,
        )
        self.up_comp_result_menu.pack(fill="x", padx=8, pady=(2, 4))
        self.up_comp_opponent = self._labeled_entry(update_competition_box, "New Opponent (optional)")
        ctk.CTkLabel(
            update_competition_box,
            text="Record ID: Reports -> Competition History -> id",
            text_color="gray",
        ).pack(pady=(0, 4))
        ctk.CTkButton(
            update_competition_box,
            text="Update Competition",
            command=self._update_competition,
            fg_color="#1f6aa5",
            hover_color="#144870",
        ).pack(pady=8)

        delete_student_box = ctk.CTkFrame(frame)
        delete_student_box.grid(row=2, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            delete_student_box,
            text="Delete Student",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=6)
        self.del_stu_id = self._labeled_entry(delete_student_box, "Member ID")
        ctk.CTkButton(
            delete_student_box,
            text="Delete Student",
            command=self._delete_student,
            fg_color="#c0392b",
            hover_color="#922b21",
        ).pack(pady=8)

        delete_coach_box = ctk.CTkFrame(frame)
        delete_coach_box.grid(row=2, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            delete_coach_box,
            text="Delete Coach",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=6)
        self.del_coach_id = self._labeled_entry(delete_coach_box, "Member ID")
        ctk.CTkLabel(
            delete_coach_box,
            text="Coach with team cannot be deleted",
            text_color="gray",
        ).pack(pady=(0, 4))
        ctk.CTkButton(
            delete_coach_box,
            text="Delete Coach",
            command=self._delete_coach,
            fg_color="#c0392b",
            hover_color="#922b21",
        ).pack(pady=8)

        delete_teacher_box = ctk.CTkFrame(frame)
        delete_teacher_box.grid(row=2, column=2, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            delete_teacher_box,
            text="Delete Teacher",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=6)
        self.del_teacher_id = self._labeled_entry(delete_teacher_box, "Member ID")
        ctk.CTkButton(
            delete_teacher_box,
            text="Delete Teacher",
            command=self._delete_teacher,
            fg_color="#c0392b",
            hover_color="#922b21",
        ).pack(pady=8)

        delete_team_box = ctk.CTkFrame(frame)
        delete_team_box.grid(row=3, column=0, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            delete_team_box,
            text="Delete Team",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=6)
        self.del_team_name = self._labeled_entry(delete_team_box, "Team Name")
        ctk.CTkLabel(
            delete_team_box,
            text="Cascade delete: team members + competition records",
            text_color="gray",
        ).pack(pady=(0, 4))
        ctk.CTkButton(
            delete_team_box,
            text="Delete Team",
            command=self._delete_team,
            fg_color="#c0392b",
            hover_color="#922b21",
        ).pack(pady=8)

        delete_competition_box = ctk.CTkFrame(frame)
        delete_competition_box.grid(row=3, column=1, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(
            delete_competition_box,
            text="Delete Competition",
            font=ctk.CTkFont(weight="bold"),
        ).pack(pady=6)
        self.del_competition_id = self._labeled_entry(delete_competition_box, "Record ID")
        ctk.CTkLabel(
            delete_competition_box,
            text="Record ID: Reports -> Competition History -> id",
            text_color="gray",
        ).pack(pady=(0, 4))
        ctk.CTkButton(
            delete_competition_box,
            text="Delete Competition",
            command=self._delete_competition,
            fg_color="#c0392b",
            hover_color="#922b21",
        ).pack(pady=8)

    # Competition tab 
    def _build_competition_tab(self):
        # Competition tab is simplified to common W/L/D fields.
        frame = self.tab_competition

        step1 = ctk.CTkFrame(frame)
        step1.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(step1, text="Step 1 - Common Fields", font=ctk.CTkFont(weight="bold")).grid(
            row=0,
            column=0,
            columnspan=8,
            sticky="w",
            padx=8,
            pady=(8, 4),
        )

        ctk.CTkLabel(step1, text="Team").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.comp_team_var = tk.StringVar(value="")
        self.comp_team_menu = ctk.CTkOptionMenu(
            step1,
            values=[""],
            variable=self.comp_team_var,
            width=180,
        )
        self.comp_team_menu.grid(row=1, column=1, padx=6, pady=6)

        ctk.CTkLabel(step1, text="Year").grid(row=1, column=2, padx=6, pady=6, sticky="w")
        self.comp_year = ctk.CTkEntry(step1, width=90)
        self.comp_year.grid(row=1, column=3, padx=6, pady=6)

        ctk.CTkLabel(step1, text="Month").grid(row=1, column=4, padx=6, pady=6, sticky="w")
        self.comp_month = ctk.CTkEntry(step1, width=70)
        self.comp_month.grid(row=1, column=5, padx=6, pady=6)

        ctk.CTkLabel(step1, text="Result").grid(row=1, column=6, padx=6, pady=6, sticky="w")
        self.comp_result_var = tk.StringVar(value="win")
        self.comp_result_menu = ctk.CTkOptionMenu(
            step1,
            values=["win", "loss", "draw"],
            variable=self.comp_result_var,
            width=100,
        )
        self.comp_result_menu.grid(row=1, column=7, padx=6, pady=6)

        ctk.CTkLabel(step1, text="Competition Name").grid(row=2, column=0, padx=6, pady=6, sticky="w")
        self.comp_name = ctk.CTkEntry(step1, width=280)
        self.comp_name.grid(row=2, column=1, columnspan=3, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(step1, text="Opponent").grid(row=2, column=4, padx=6, pady=6, sticky="w")
        self.comp_opponent = ctk.CTkEntry(step1, width=220)
        self.comp_opponent.grid(row=2, column=5, columnspan=3, padx=6, pady=6, sticky="w")

        ctk.CTkButton(step1, text="Refresh Teams", command=self._refresh_competition_team_options).grid(
            row=3,
            column=0,
            padx=6,
            pady=(4, 8),
            sticky="w",
        )

        ctk.CTkButton(step1, text="Save Competition Record", command=self._add_competition_record).grid(
            row=3,
            column=7,
            padx=6,
            pady=(4, 8),
            sticky="e",
        )

        self._refresh_competition_team_options()

    # reports tab 
    def _build_reports_tab(self):
        # reports tab uses scrollable frame so that long content can still be viewed
        frame = self.tab_reports
        scroll = ctk.CTkScrollableFrame(frame)
        scroll.pack(fill="both", expand=True, padx=8, pady=8)

        toolbar = ctk.CTkFrame(scroll)
        toolbar.pack(fill="x", padx=8, pady=8)
        ctk.CTkButton(toolbar, text="Refresh All Reports", command=self._refresh_all_reports).pack(
            side="left", padx=8, pady=8
        )

        ctk.CTkLabel(scroll, text="Team Performance", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w",
            padx=12,
            pady=(4, 0),
        )
        self.team_report_tree = self._create_treeview(scroll, height=6, expand=False)

        ctk.CTkLabel(scroll, text="Ineligible Students (GPA < 2.0)", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w",
            padx=12,
            pady=(6, 0),
        )
        self.ineligible_tree = self._create_treeview(scroll, height=5, expand=False)

        filters = ctk.CTkFrame(scroll)
        filters.pack(fill="x", padx=8, pady=(6, 8))
        ctk.CTkLabel(filters, text="Team").grid(row=0, column=0, padx=6, pady=6)
        self.rep_team = ctk.CTkEntry(filters, width=140)
        self.rep_team.grid(row=0, column=1, padx=6, pady=6)
        ctk.CTkLabel(filters, text="Year").grid(row=0, column=2, padx=6, pady=6)
        self.rep_year = ctk.CTkEntry(filters, width=90)
        self.rep_year.grid(row=0, column=3, padx=6, pady=6)
        ctk.CTkLabel(filters, text="Month").grid(row=0, column=4, padx=6, pady=6)
        self.rep_month = ctk.CTkEntry(filters, width=70)
        self.rep_month.grid(row=0, column=5, padx=6, pady=6)
        ctk.CTkLabel(filters, text="Competition").grid(row=0, column=6, padx=6, pady=6)
        self.rep_comp_name = ctk.CTkEntry(filters, width=220)
        self.rep_comp_name.grid(row=0, column=7, padx=6, pady=6)
        ctk.CTkButton(filters, text="Apply Filters", command=self._refresh_competition_reports).grid(
            row=0,
            column=8,
            padx=6,
            pady=6,
        )

        ctk.CTkLabel(scroll, text="Win / Loss / Draw Summary", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w",
            padx=12,
            pady=(2, 0),
        )
        self.win_loss_tree = self._create_treeview(scroll, height=5, expand=False)

        ctk.CTkLabel(scroll, text="Competition History", font=ctk.CTkFont(weight="bold")).pack(
            anchor="w",
            padx=12,
            pady=(2, 0),
        )
        self.history_tree = self._create_treeview(scroll, height=7, expand=False)

    # SQL Data tab 
    def _build_sql_tab(self):
        # SQL tab is read-only,it is used to inspect database state in table form
        frame = self.tab_sql

        control_row = ctk.CTkFrame(frame)
        control_row.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(control_row, text="Table").pack(side="left", padx=8)
        self.sql_table_options = ["all_tables", *TeamManagementRepository.DASHBOARD_TABLES]
        self.sql_table_var = tk.StringVar(value="all_tables")
        self.sql_table_menu = ctk.CTkOptionMenu(
            control_row,
            values=self.sql_table_options,
            variable=self.sql_table_var,
            width=240,
        )
        self.sql_table_menu.pack(side="left", padx=8)

        ctk.CTkButton(control_row, text="Refresh SQL Data", command=self._refresh_sql_data).pack(
            side="left",
            padx=8,
        )

        hint = ctk.CTkLabel(
            frame,
            text="Select single table for full rows; all_tables shows summary.",
            text_color="gray",
        )
        hint.pack(anchor="w", padx=12, pady=(0, 8))

        self.sql_tree = self._create_treeview(frame, height=18)

    # UI helpers 
    @staticmethod
    def _labeled_entry(parent, label_text, show=None):
        # helper to reduce repeated label and entry code in forms.
        ctk.CTkLabel(parent, text=label_text).pack(anchor="w", padx=8, pady=(4, 0))
        entry = ctk.CTkEntry(parent, show=show)
        entry.pack(fill="x", padx=8, pady=(2, 4))
        return entry

    @staticmethod
    def _create_treeview(parent, height=10, expand=True):
        # treeview + vertical,horizontal scrollbars to simulate SQL or Excel grid
        container = ctk.CTkFrame(parent)
        if expand:
            container.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        else:
            container.pack(fill="x", expand=False, padx=8, pady=(0, 8))

        tree = ttk.Treeview(container, show="headings", height=height)
        v_scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        return tree

    @staticmethod
    def _render_tree(tree, columns, rows):
        # full refresh render: clear old rows, set new columns, insert current rows
        tree.delete(*tree.get_children())

        if not columns:
            columns = ["message"]
            rows = [{"message": "No data available"}]

        tree["columns"] = columns
        for column in columns:
            tree.heading(column, text=column)
            tree.column(column, anchor="w", width=140, stretch=True)

        for row in rows:
            values = [row.get(column, "") for column in columns]
            tree.insert("", "end", values=values)

    @staticmethod
    def _or_none(value):
        return value if value else None

    @staticmethod
    def _parse_optional_int(field_name, text, min_value=None, max_value=None):
        # shared parser for filter fields.
        # empty input means "no filter", otherwise must be valid integer range.
        if not text:
            return None
        try:
            parsed = int(text)
        except ValueError as error:
            raise ValueError(f"{field_name} must be an integer.") from error

        if min_value is not None and parsed < min_value:
            raise ValueError(f"{field_name} must be >= {min_value}.")
        if max_value is not None and parsed > max_value:
            raise ValueError(f"{field_name} must be <= {max_value}.")
        return parsed

    def _safe_call(self, func, success_message, on_success=None):
        # generic action wrapper:
        # run action
        # show status message
        # refresh all relevant views
        try:
            func()
            if on_success is not None:
                on_success()
            self._refresh_all_views()
            messagebox.showinfo("Success", success_message)
        except Exception as error:
            messagebox.showerror("Operation Failed", str(error))

    # competition helpers 
    def _refresh_competition_team_options(self):
        # refresh team dropdown so new teams are available immediately in form
        team_names = sorted(self.app.system.teams.keys())
        if not team_names:
            team_names = [""]
        self.comp_team_menu.configure(values=team_names)
        if self.comp_team_var.get() not in team_names:
            self.comp_team_var.set(team_names[0])

    # refresh methods 
    def _refresh_all_views(self):
        # central refresh chain for consistency across tabs
        self._refresh_competition_team_options()
        self._refresh_all_reports()
        self._refresh_sql_data()

    def _refresh_all_reports(self):
        # reports are split into three independent blocks
        self._show_team_performance()
        self._show_ineligible()
        self._refresh_competition_reports()

    def _refresh_competition_reports(self):
        # read current filter values from UI
        team_name = self._or_none(self.rep_team.get().strip())
        year_text = self.rep_year.get().strip()
        month_text = self.rep_month.get().strip()
        competition_name = self._or_none(self.rep_comp_name.get().strip())

        try:
            # validate numeric filters before querying service layer.
            year = self._parse_optional_int("Year", year_text, min_value=2000, max_value=2100)
            month = self._parse_optional_int("Month", month_text, min_value=1, max_value=12)
        except ValueError as error:
            messagebox.showerror("Invalid Filters", str(error))
            return

        # summary section: aggregated W/L/D numbers.
        summary_rows = self.app.system.list_win_loss_summary(
            team_name=team_name,
            year=year,
            month=month,
        )
        self._render_tree(
            self.win_loss_tree,
            ["team_name", "wins", "losses", "draws", "total_matches"],
            summary_rows,
        )

        # history section: competition-level detail rows
        records = self.app.system.list_team_records(
            team_name=team_name,
            year=year,
            month=month,
            competition_name=competition_name,
        )
        history_rows = []
        for record in records:
            history_rows.append(
                {
                    "id": record["id"],
                    "team_name": record["team_name"],
                    "sport_type": record["sport_type"],
                    "year": record["year"],
                    "month": record["month"],
                    "competition_name": record["competition_name"],
                    "result": record["result"],
                    "opponent": record["opponent"],
                }
            )
        self._render_tree(
            self.history_tree,
            [
                "id",
                "team_name",
                "sport_type",
                "year",
                "month",
                "competition_name",
                "result",
                "opponent",
            ],
            history_rows,
        )

    # actions: add 
    def _add_student(self):
        # collect form values and pass to service layer
        def action():
            self.app.system.add_student(
                name=self.stu_name.get().strip(),
                member_id=self.stu_id.get().strip(),
                gpa=float(self.stu_gpa.get().strip()),
                attendance_rate=float(self.stu_att.get().strip()),
            )

        self._safe_call(
            action,
            "Student added.",
            on_success=self._clear_all_add_forms,
        )

    def _add_coach(self):
        # similar to student add flow
        def action():
            self.app.system.add_coach(
                name=self.coach_name.get().strip(),
                member_id=self.coach_id.get().strip(),
                specialization=self.coach_spec.get().strip(),
                username=self.coach_user.get().strip(),
                password=self.coach_pass.get().strip(),
            )

        self._safe_call(
            action,
            "Coach added.",
            on_success=self._clear_all_add_forms,
        )

    def _add_teacher(self):
        # teacher creation always includes account credentials in this GUI design
        def action():
            username = self.teacher_user.get().strip()
            password = self.teacher_pass.get().strip()
            if not username:
                raise ValueError("Username cannot be empty.")
            if len(password) < 4:
                raise ValueError("Password must be at least 4 characters.")

            self.app.system.add_teacher(
                name=self.teacher_name.get().strip(),
                member_id=self.teacher_id.get().strip(),
                department=self.teacher_dept.get().strip(),
                username=username,
                password=password,
            )

        self._safe_call(
            action,
            "Teacher added.",
            on_success=self._clear_all_add_forms,
        )

    def _clear_student_add_form(self):
        # Clear all student inputs in Add Data tab.
        self.stu_name.delete(0, tk.END)
        self.stu_id.delete(0, tk.END)
        self.stu_gpa.delete(0, tk.END)
        self.stu_att.delete(0, tk.END)

    def _clear_coach_add_form(self):
        # Clear all coach inputs in Add Data tab.
        self.coach_name.delete(0, tk.END)
        self.coach_id.delete(0, tk.END)
        self.coach_spec.delete(0, tk.END)
        self.coach_user.delete(0, tk.END)
        self.coach_pass.delete(0, tk.END)

    def _clear_teacher_add_form(self):
        # Clear all teacher inputs in Add Data tab.
        self.teacher_name.delete(0, tk.END)
        self.teacher_id.delete(0, tk.END)
        self.teacher_dept.delete(0, tk.END)
        self.teacher_user.delete(0, tk.END)
        self.teacher_pass.delete(0, tk.END)

    def _clear_all_add_forms(self):
        # Clear all Add Data forms after successful add action.
        self._clear_student_add_form()
        self._clear_coach_add_form()
        self._clear_teacher_add_form()

    def _clear_create_team_form(self):
        # Clear Create Team inputs in Team Operation tab.
        self.team_sport.delete(0, tk.END)
        self.team_name.delete(0, tk.END)
        self.team_coach_id.delete(0, tk.END)
        self.team_metric.delete(0, tk.END)

    def _clear_assign_team_form(self):
        # Clear Assign Student inputs in Team Operation tab.
        self.assign_student_id.delete(0, tk.END)
        self.assign_team_name.delete(0, tk.END)

    def _clear_team_operation_form(self):
        # Clear all Team Operation inputs after successful team actions.
        self._clear_create_team_form()
        self._clear_assign_team_form()

    def _clear_competition_form(self):
        # Clear Competition tab inputs after successful save.
        # Keep selected team, reset result default, and clear text fields.
        self.comp_year.delete(0, tk.END)
        self.comp_month.delete(0, tk.END)
        self.comp_name.delete(0, tk.END)
        self.comp_opponent.delete(0, tk.END)
        self.comp_result_var.set("win")

    def _clear_update_student_form(self):
        # Clear Update Student inputs in Update tab.
        self.up_stu_id.delete(0, tk.END)
        self.up_stu_name.delete(0, tk.END)
        self.up_stu_gpa.delete(0, tk.END)
        self.up_stu_att.delete(0, tk.END)

    def _clear_update_coach_form(self):
        # Clear Update Coach inputs in Update tab.
        self.up_coach_id.delete(0, tk.END)
        self.up_coach_name.delete(0, tk.END)
        self.up_coach_spec.delete(0, tk.END)
        self.up_coach_pass.delete(0, tk.END)

    def _clear_update_team_form(self):
        # Clear Update Team inputs in Update tab.
        self.up_team_name.delete(0, tk.END)
        self.up_team_coach.delete(0, tk.END)
        self.up_team_metric.delete(0, tk.END)

    def _clear_update_competition_form(self):
        # Clear Update Competition inputs in Update tab.
        self.up_comp_id.delete(0, tk.END)
        self.up_comp_year.delete(0, tk.END)
        self.up_comp_month.delete(0, tk.END)
        self.up_comp_name.delete(0, tk.END)
        self.up_comp_opponent.delete(0, tk.END)
        self.up_comp_result_var.set("(no change)")

    # actions: team 
    def _create_team(self):
        # create sport team using typed metric value from form
        def action():
            self.app.system.create_team(
                sport_type=self.team_sport.get().strip(),
                team_name=self.team_name.get().strip(),
                coach_id=self.team_coach_id.get().strip(),
                metric_value=float(self.team_metric.get().strip()),
            )

        self._safe_call(
            action,
            "Team created.",
            on_success=self._clear_team_operation_form,
        )

    def _assign_student(self):
        # assignment may fail if student is ineligible. service layer will report error
        def action():
            self.app.system.assign_student_to_team(
                student_id=self.assign_student_id.get().strip(),
                team_name=self.assign_team_name.get().strip(),
            )

        self._safe_call(
            action,
            "Student assigned to team.",
            on_success=self._clear_team_operation_form,
        )

    # actions: update 
    def _update_student(self):
        # optional inputs: blank means keep current value
        def action():
            gpa_text = self.up_stu_gpa.get().strip()
            att_text = self.up_stu_att.get().strip()
            self.app.system.update_student_profile(
                member_id=self.up_stu_id.get().strip(),
                name=self._or_none(self.up_stu_name.get().strip()),
                gpa=float(gpa_text) if gpa_text else None,
                attendance_rate=float(att_text) if att_text else None,
            )

        self._safe_call(
            action,
            "Student updated.",
            on_success=self._clear_update_student_form,
        )

    def _update_coach(self):
        # update coach profile
        def action():
            self.app.system.update_coach_profile(
                member_id=self.up_coach_id.get().strip(),
                name=self._or_none(self.up_coach_name.get().strip()),
                specialization=self._or_none(self.up_coach_spec.get().strip()),
                new_password=self._or_none(self.up_coach_pass.get().strip()),
            )

        self._safe_call(
            action,
            "Coach updated.",
            on_success=self._clear_update_coach_form,
        )

    def _update_team(self):
        # team update supports coach replacement and metric update
        def action():
            metric_text = self.up_team_metric.get().strip()
            self.app.system.update_team(
                team_name=self.up_team_name.get().strip(),
                new_coach_id=self._or_none(self.up_team_coach.get().strip()),
                new_metric=float(metric_text) if metric_text else None,
            )

        self._safe_call(
            action,
            "Team updated.",
            on_success=self._clear_update_team_form,
        )

    def _update_competition(self):
        record_id_text = self.up_comp_id.get().strip()
        if not record_id_text:
            messagebox.showerror("Operation Failed", "Competition record ID cannot be empty.")
            return
        try:
            record_id = int(record_id_text)
        except ValueError:
            messagebox.showerror("Operation Failed", "Competition record ID must be an integer.")
            return

        year_text = self.up_comp_year.get().strip()
        month_text = self.up_comp_month.get().strip()
        competition_name = self._or_none(self.up_comp_name.get().strip())
        opponent = self._or_none(self.up_comp_opponent.get().strip())
        try:
            year = self._parse_optional_int("Year", year_text)
            month = self._parse_optional_int("Month", month_text)
        except ValueError as error:
            messagebox.showerror("Operation Failed", str(error))
            return

        result_choice = self.up_comp_result_var.get().strip().lower()
        new_result = None if result_choice == "(no change)" else result_choice

        def action():
            self.app.system.update_competition_record(
                record_id=record_id,
                year=year,
                month=month,
                competition_name=competition_name,
                result=new_result,
                opponent=opponent,
            )

        self._safe_call(
            action,
            "Competition record updated.",
            on_success=self._clear_update_competition_form,
        )

    def _delete_student(self):
        member_id = self.del_stu_id.get().strip()
        if not member_id:
            messagebox.showerror("Operation Failed", "Student ID cannot be empty.")
            return
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete student profile '{member_id}'?",
        ):
            return

        def action():
            self.app.system.delete_student(member_id)

        def on_success():
            self.del_stu_id.delete(0, tk.END)

        self._safe_call(action, "Student deleted.", on_success=on_success)

    def _delete_coach(self):
        member_id = self.del_coach_id.get().strip()
        if not member_id:
            messagebox.showerror("Operation Failed", "Coach ID cannot be empty.")
            return
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete coach '{member_id}' and the linked coach account?",
        ):
            return

        def action():
            self.app.system.delete_coach(member_id)

        def on_success():
            self.del_coach_id.delete(0, tk.END)

        self._safe_call(action, "Coach deleted.", on_success=on_success)

    def _delete_teacher(self):
        member_id = self.del_teacher_id.get().strip()
        if not member_id:
            messagebox.showerror("Operation Failed", "Teacher ID cannot be empty.")
            return
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete teacher '{member_id}' and the linked teacher account?",
        ):
            return

        def action():
            self.app.system.delete_teacher(member_id)

        def on_success():
            self.del_teacher_id.delete(0, tk.END)

        self._safe_call(action, "Teacher deleted.", on_success=on_success)

    def _delete_team(self):
        team_name = self.del_team_name.get().strip()
        if not team_name:
            messagebox.showerror("Operation Failed", "Team name cannot be empty.")
            return
        if not messagebox.askyesno(
            "Confirm Delete",
            (
                f"Delete team '{team_name}'?\n\n"
                "This will also delete related team members and competition records."
            ),
        ):
            return

        def action():
            self.app.system.delete_team(team_name)

        def on_success():
            self.del_team_name.delete(0, tk.END)

        self._safe_call(action, "Team deleted.", on_success=on_success)

    def _delete_competition(self):
        record_id_text = self.del_competition_id.get().strip()
        if not record_id_text:
            messagebox.showerror("Operation Failed", "Competition record ID cannot be empty.")
            return
        try:
            record_id = int(record_id_text)
        except ValueError:
            messagebox.showerror("Operation Failed", "Competition record ID must be an integer.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete competition record ID '{record_id}'?",
        ):
            return

        def action():
            self.app.system.delete_competition_record(record_id)

        def on_success():
            self.del_competition_id.delete(0, tk.END)

        self._safe_call(action, "Competition record deleted.", on_success=on_success)

    # actions: competition 
    def _add_competition_record(self):
        # save one competition result using W/L/D model
        def action():
            self.app.system.add_team_competition_record(
                team_name=self.comp_team_var.get().strip(),
                year=int(self.comp_year.get().strip()),
                month=int(self.comp_month.get().strip()),
                competition_name=self.comp_name.get().strip(),
                result=self.comp_result_var.get().strip(),
                opponent=self.comp_opponent.get().strip(),
            )

        self._safe_call(
            action,
            "Competition record saved.",
            on_success=self._clear_competition_form,
        )

    # actions: reports 
    def _show_team_performance(self):
        # Build team performance table rows for reports tab
        rows = []
        for team_name in sorted(self.app.system.teams):
            team = self.app.system.teams[team_name]
            rows.append(
                {
                    "team_name": team.team_name,
                    "coach_name": team.coach.name,
                    "performance": f"{team.calculate_performance():.2f}",
                    "unit": team.performance_unit(),
                    "members": len(team.members),
                }
            )

        self._render_tree(
            self.team_report_tree,
            ["team_name", "coach_name", "performance", "unit", "members"],
            rows,
        )

    def _show_ineligible(self):
        # Show students that fail eligibility rule (GPA < 2.0).
        students = self.app.system.get_ineligible_students()
        rows = [
            {
                "student_id": student.member_id,
                "student_name": student.name,
                "gpa": f"{student.gpa:.2f}",
                "attendance_rate": f"{student.attendance_rate:.1f}",
            }
            for student in students
        ]
        self._render_tree(
            self.ineligible_tree,
            ["student_id", "student_name", "gpa", "attendance_rate"],
            rows,
        )

    # actions: sql data 
    def _refresh_sql_data(self):
        # SQL snapshot is the single source for this tab
        snapshot = self.app.system.get_sql_snapshot()
        selected = self.sql_table_var.get().strip().lower()

        if selected == "all_tables":
            # all_tables mode shows summary only (row count + columns per table)
            summary_rows = []
            for table_name in TeamManagementRepository.DASHBOARD_TABLES:
                table_payload = snapshot[table_name]
                summary_rows.append(
                    {
                        "table_name": table_name,
                        "row_count": len(table_payload["rows"]),
                        "columns": ", ".join(table_payload["columns"]),
                    }
                )
            self._render_tree(
                self.sql_tree,
                ["table_name", "row_count", "columns"],
                summary_rows,
            )
            return

        if selected not in snapshot:
            raise ValueError(f"Unsupported table selection: {selected}")

        # Single-table mode renders full row data.
        payload = snapshot[selected]
        self._render_tree(self.sql_tree, payload["columns"], payload["rows"])


if __name__ == "__main__":
    app = MSUTMSApp()
    app.mainloop()
