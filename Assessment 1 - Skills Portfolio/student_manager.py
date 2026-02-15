import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import os

FILE = "studentMarks.txt"

# ---------------------------------------------------------
#   FILE HANDLING & UTILITIES
# ---------------------------------------------------------

def load_students():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            f.write("0\n")
        return []

    with open(FILE, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 1:
        return []

    try:
        student_count = int(lines[0])
    except:
        messagebox.showerror("Error", "Invalid studentMarks.txt format.")
        return []

    students = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != 6:  
            continue
        code = int(parts[0])
        name = parts[1]
        c1, c2, c3 = map(int, parts[2:5])
        exam = int(parts[5])

        students.append({
            "code": code,
            "name": name,
            "c1": c1,
            "c2": c2,
            "c3": c3,
            "coursework": c1 + c2 + c3,
            "exam": exam
        })

    return students


def save_students(students):
    with open(FILE, "w") as f:
        f.write(str(len(students)) + "\n")
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")


def percentage(s):
    return round((s["coursework"] + s["exam"]) / 160 * 100, 2)


def grade(p):
    if p >= 70: return "A"
    if p >= 60: return "B"
    if p >= 50: return "C"
    if p >= 40: return "D"
    return "F"


# ---------------------------------------------------------
#   PROFESSIONAL CAR-DASHBOARD GUI
# ---------------------------------------------------------

class StudentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager – Automotive Edition")
        self.root.geometry("950x600")

        # Automotive dashboard palette
        BG = "#1A1D21"         # carbon dark
        PANEL = "#101214"      # deeper carbon
        ACCENT = "#21C3D1"     # teal dashboard glow
        TEXT_LIGHT = "#DDE2E6"
        BUTTON_BG = "#2B2F33"  # graphite steel

        self.root.configure(bg=BG)
        self.students = load_students()

        # Title
        tk.Label(
            root,
            text="STUDENT MANAGER",
            font=("Segoe UI Semibold", 26),
            fg=ACCENT,
            bg=BG
        ).pack(pady=20)

        # Output Panel
        self.output = tk.Text(
            root,
            width=110,
            height=22,
            bg=PANEL,
            fg=TEXT_LIGHT,
            font=("Consolas", 12),
            insertbackground=ACCENT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#333"
        )
        self.output.pack(pady=10)

        # Tkinter button styling
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dashboard.TButton",
                        background=BUTTON_BG,
                        foreground=TEXT_LIGHT,
                        padding=8,
                        font=("Segoe UI", 11),
                        borderwidth=0)

        style.map("Dashboard.TButton",
                  background=[("active", ACCENT)],
                  foreground=[("active", "black")])

        # Button Frame
        frame = tk.Frame(root, bg=BG)
        frame.pack(pady=10)

        buttons = [
            ("View All Records", self.view_all),
            ("View Student", self.view_one),
            ("Highest Score", self.highest),
            ("Lowest Score", self.lowest),
            ("Sort Records", self.sort_records),
            ("Add Student", self.add_student),
            ("Delete Student", self.delete_student),
            ("Update Student", self.update_student)
        ]

        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(frame, text=text, command=cmd, width=20,
                       style="Dashboard.TButton").grid(
                row=i // 2, column=i % 2, padx=12, pady=6
            )

    # ---------------------------------------------------------
    #   Display Helper
    # ---------------------------------------------------------

    def show(self, content):
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, content)

    # ---------------------------------------------------------
    #   Core Functions
    # ---------------------------------------------------------

    def view_all(self):
        if not self.students:
            return self.show("No student records found.")

        out = ""
        percentages_list = []

        for s in self.students:
            p = percentage(s)
            percentages_list.append(p)

            out += (
                f"Name: {s['name']}\n"
                f"Code: {s['code']}\n"
                f"Coursework Total: {s['coursework']} / 60\n"
                f"Exam: {s['exam']} / 100\n"
                f"Percentage: {p}%\n"
                f"Grade: {grade(p)}\n"
                f"{'-' * 45}\n"
            )

        avg = round(sum(percentages_list) / len(percentages_list), 2)
        out += f"\nTotal Students: {len(self.students)}"
        out += f"\nAverage Percentage: {avg}%"

        self.show(out)

    def view_one(self):
        code = simpledialog.askinteger("Search Student", "Enter student code:")
        if code is None:
            return

        for s in self.students:
            if s["code"] == code:
                p = percentage(s)
                return self.show(
                    f"Name: {s['name']}\n"
                    f"Code: {s['code']}\n"
                    f"Coursework: {s['coursework']}\n"
                    f"Exam: {s['exam']}\n"
                    f"Percentage: {p}%\n"
                    f"Grade: {grade(p)}"
                )

        messagebox.showinfo("Not Found", "Student not found.")

    def highest(self):
        s = max(self.students, key=lambda x: percentage(x))
        p = percentage(s)
        self.show(
            f"TOP PERFORMER\n\n"
            f"Name: {s['name']}\nCode: {s['code']}\n"
            f"Coursework: {s['coursework']}\nExam: {s['exam']}\n"
            f"Percentage: {p}%\nGrade: {grade(p)}"
        )

    def lowest(self):
        s = min(self.students, key=lambda x: percentage(x))
        p = percentage(s)
        self.show(
            f"LOWEST PERFORMER\n\n"
            f"Name: {s['name']}\nCode: {s['code']}\n"
            f"Coursework: {s['coursework']}\nExam: {s['exam']}\n"
            f"Percentage: {p}%\nGrade: {grade(p)}"
        )

    def sort_records(self):
        order = simpledialog.askstring("Sort", "Enter 'asc' or 'desc':")
        if order not in ("asc", "desc"):
            return

        self.students.sort(key=lambda x: percentage(x), reverse=(order == "desc"))
        self.view_all()

    def add_student(self):
        code = simpledialog.askinteger("Add", "Student Code:")
        name = simpledialog.askstring("Add", "Student Name:")
        c1 = simpledialog.askinteger("Add", "Coursework 1 (0–20):")
        c2 = simpledialog.askinteger("Add", "Coursework 2 (0–20):")
        c3 = simpledialog.askinteger("Add", "Coursework 3 (0–20):")
        exam = simpledialog.askinteger("Add", "Exam Mark (0–100):")

        if None in (code, name, c1, c2, c3, exam):
            return

        self.students.append({
            "code": code,
            "name": name,
            "c1": c1,
            "c2": c2,
            "c3": c3,
            "coursework": c1 + c2 + c3,
            "exam": exam
        })

        save_students(self.students)
        self.view_all()

    def delete_student(self):
        code = simpledialog.askinteger("Delete", "Enter student code:")
        if code is None:
            return

        self.students = [s for s in self.students if s["code"] != code]
        save_students(self.students)
        self.view_all()

    def update_student(self):
        code = simpledialog.askinteger("Update", "Enter student code to update:")
        if code is None:
            return

        for s in self.students:
            if s["code"] == code:
                new_exam = simpledialog.askinteger("Update", "New exam mark:")
                new_c = simpledialog.askinteger("Update", "New coursework total (0–60):")

                if new_exam is not None:
                    s["exam"] = new_exam

                if new_c is not None:
                    p = new_c // 3
                    s["c1"] = s["c2"] = s["c3"] = p
                    s["coursework"] = new_c

                save_students(self.students)
                self.view_all()
                return

        messagebox.showinfo("Not Found", "Student not found.")


# ---------------------------------------------------------
#   RUN APPLICATION
# ---------------------------------------------------------
root = tk.Tk()
StudentGUI(root)
root.mainloop()



