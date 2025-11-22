import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os

FILE_NAME = "studentMarks.txt"


# ===================== SAFE LOADER =====================
def load_students():
    if not os.path.exists(FILE_NAME):
        return []

    students = []

    with open(FILE_NAME, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # skip the first line (student count)
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) != 6:
            continue

        students.append({
            "code": parts[0],
            "name": parts[1],
            "c1": int(parts[2]),
            "c2": int(parts[3]),
            "c3": int(parts[4]),
            "exam": int(parts[5]),
        })

    return students


def save_students(students):
    with open(FILE_NAME, "w") as f:
        f.write(str(len(students)) + "\n")
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")


# ===================== CALCULATIONS =====================
def total_coursework(s):
    return s["c1"] + s["c2"] + s["c3"]

def percentage(s):
    return round(((total_coursework(s) + s["exam"]) / 160) * 100, 2)

def grade(p):
    if p >= 70: return "A"
    if p >= 60: return "B"
    if p >= 50: return "C"
    if p >= 40: return "D"
    return "F"


# ===================== MAIN CLASS =====================
class StudentApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager - Color Edition")
        self.root.geometry("950x550")
        self.root.configure(bg="#eef2f3")

        self.students = load_students()

        # ======= Sidebar =======
        sidebar = tk.Frame(root, bg="#3a6073", width=180)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Student Manager", fg="white",
                 bg="#3a6073", font=("Arial", 16, "bold")).pack(pady=20)

        buttons = [
            ("View All", self.view_all),
            ("View Individual", self.view_one),
            ("Highest Score", self.highest),
            ("Lowest Score", self.lowest),
            ("Sort Records", self.sort_records),
            ("Add Student", self.add_student),
            ("Delete Student", self.delete_student),
            ("Update Student", self.update_student)
        ]

        for text, cmd in buttons:
            tk.Button(sidebar, text=text, command=cmd,
                      bg="#4b79a1", fg="white", font=("Arial", 11),
                      activebackground="#35516a",
                      width=16, height=1).pack(pady=6)

        # ======= Table Frame =======
        frame = tk.Frame(root, bg="#eef2f3")
        frame.pack(side="right", fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview",
                        background="#ffffff",
                        rowheight=25,
                        fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.tree = ttk.Treeview(
            frame,
            columns=("name", "code", "cw", "exam", "percent", "grade"),
            show="headings"
        )

        headings = ["Name", "Code", "Coursework", "Exam", "Percent", "Grade"]
        for col, text in zip(self.tree["columns"], headings):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=130)

        self.tree.pack(fill="both", expand=True, padx=15, pady=15)

        self.view_all()

    # ===================== Helpers =====================
    def clear(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def insert(self, s):
        p = percentage(s)
        g = grade(p)
        self.tree.insert("", tk.END, values=(
            s["name"], s["code"], total_coursework(s), s["exam"], p, g
        ))

    # ===================== Menu Actions =====================
    def view_all(self):
        self.clear()
        for s in self.students:
            self.insert(s)

    def view_one(self):
        q = simpledialog.askstring("Search", "Enter student name or code:")
        if not q:
            return
        self.clear()
        matches = [s for s in self.students if q.lower() in s["name"].lower() or s["code"] == q]
        if matches:
            for s in matches:
                self.insert(s)
        else:
            messagebox.showwarning("Not Found", "Student not found.")

    def highest(self):
        s = max(self.students, key=lambda x: percentage(x))
        self.clear()
        self.insert(s)

    def lowest(self):
        s = min(self.students, key=lambda x: percentage(x))
        self.clear()
        self.insert(s)

    def sort_records(self):
        asc = messagebox.askyesno("Sort", "Sort ascending?")
        self.students.sort(key=lambda x: percentage(x), reverse=not asc)
        self.view_all()

    def add_student(self):
        try:
            code = simpledialog.askstring("Add", "Enter student code:")
            name = simpledialog.askstring("Add", "Enter name:")
            c1 = int(simpledialog.askstring("Add", "Coursework 1:"))
            c2 = int(simpledialog.askstring("Add", "Coursework 2:"))
            c3 = int(simpledialog.askstring("Add", "Coursework 3:"))
            exam = int(simpledialog.askstring("Add", "Exam mark:"))
        except:
            messagebox.showerror("Error", "Invalid input!")
            return

        self.students.append({
            "code": code, "name": name,
            "c1": c1, "c2": c2, "c3": c3, "exam": exam
        })
        save_students(self.students)
        self.view_all()
        messagebox.showinfo("Saved", "Student added successfully!")

    def delete_student(self):
        code = simpledialog.askstring("Delete", "Enter student code:")
        for s in self.students:
            if s["code"] == code:
                self.students.remove(s)
                save_students(self.students)
                self.view_all()
                messagebox.showinfo("Deleted", "Student removed.")
                return
        messagebox.showerror("Error", "Student not found.")

    def update_student(self):
        code = simpledialog.askstring("Update", "Enter student code:")

        for s in self.students:
            if s["code"] == code:
                field = simpledialog.askstring(
                    "Update",
                    "Field (name / c1 / c2 / c3 / exam):"
                )
                if field not in ("name", "c1", "c2", "c3", "exam"):
                    messagebox.showerror("Error", "Invalid field.")
                    return

                value = simpledialog.askstring("Update", "Enter new value:")
                if field in ("c1", "c2", "c3", "exam"):
                    value = int(value)

                s[field] = value
                save_students(self.students)
                self.view_all()
                messagebox.showinfo("Updated", "Record updated.")
                return

        messagebox.showerror("Error", "Student not found.")


# ===================== RUN =====================
root = tk.Tk()
app = StudentApp(root)
root.mainloop()
