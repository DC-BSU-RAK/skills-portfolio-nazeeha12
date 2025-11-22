import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os


# ===================== FILE HANDLING ========================

FILE_NAME = "studentMarks.txt"

def load_students():
    students = []
    if not os.path.exists(FILE_NAME):
        return students

    with open(FILE_NAME, "r") as f:
        lines = f.read().strip().split("\n")

        n = int(lines[0])
        for line in lines[1:n+1]:
            parts = line.split(",")

            code = parts[0]
            name = parts[1]
            c1, c2, c3 = map(int, parts[2:5])
            exam = int(parts[5])

            students.append({
                "code": code,
                "name": name,
                "c1": c1,
                "c2": c2,
                "c3": c3,
                "exam": exam
            })
    return students


def save_students(students):
    with open(FILE_NAME, "w") as f:
        f.write(str(len(students)) + "\n")
        for s in students:
            f.write(f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n")


# ===================== UTILITY FUNCTIONS ========================

def compute_total(s):
    return s["c1"] + s["c2"] + s["c3"]

def compute_percentage(s):
    total = compute_total(s) + s["exam"]
    return round((total / 160) * 100, 2)

def compute_grade(p):
    if p >= 70: return "A"
    if p >= 60: return "B"
    if p >= 50: return "C"
    if p >= 40: return "D"
    return "F"


def student_display(s):
    total_course = compute_total(s)
    percentage = compute_percentage(s)
    grade = compute_grade(percentage)

    return (f"Name: {s['name']}\n"
            f"Student Number: {s['code']}\n"
            f"Total Coursework: {total_course}/60\n"
            f"Exam Mark: {s['exam']}/100\n"
            f"Percentage: {percentage}%\n"
            f"Grade: {grade}\n"
            f"{'-'*35}\n")


# ===================== GUI APP ========================

class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Manager")

        self.students = load_students()

        self.text = tk.Text(root, width=70, height=25, font=("Arial", 11))
        self.text.pack()

        self.menu()

    def menu(self):
        menu_frame = tk.Frame(self.root)
        menu_frame.pack()

        options = [
            ("View All Students", self.view_all),
            ("View Individual Student", self.view_one),
            ("Show Highest Score", self.highest_score),
            ("Show Lowest Score", self.lowest_score),
            ("Sort Records", self.sort_records),
            ("Add Student", self.add_student),
            ("Delete Student", self.delete_student),
            ("Update Student", self.update_student),
        ]

        for text, cmd in options:
            ttk.Button(menu_frame, text=text, width=30, command=cmd).pack(pady=2)

    # -------------------- MENU FUNCTIONS ----------------------

    def view_all(self):
        self.text.delete("1.0", tk.END)

        total_percent = 0

        for s in self.students:
            p = compute_percentage(s)
            total_percent += p
            self.text.insert(tk.END, student_display(s))

        avg = round(total_percent / len(self.students), 2)

        self.text.insert(tk.END, f"\nTotal Students: {len(self.students)}")
        self.text.insert(tk.END, f"\nAverage Percentage: {avg}%\n")

    def view_one(self):
        code = simpledialog.askstring("Search", "Enter student number or name:")
        if not code:
            return

        self.text.delete("1.0", tk.END)

        for s in self.students:
            if s["code"] == code or code.lower() in s["name"].lower():
                self.text.insert(tk.END, student_display(s))
                return

        messagebox.showwarning("Not Found", "Student not found.")

    def highest_score(self):
        best = max(self.students, key=lambda s: compute_percentage(s))
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, student_display(best))

    def lowest_score(self):
        worst = min(self.students, key=lambda s: compute_percentage(s))
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, student_display(worst))

    def sort_records(self):
        choice = messagebox.askyesno("Sort", "Sort ascending? (No = descending)")
        self.students.sort(key=lambda s: compute_percentage(s), reverse=not choice)
        self.view_all()

    def add_student(self):
        code = simpledialog.askstring("Add", "Student Number:")
        name = simpledialog.askstring("Add", "Student Name:")
        c1 = int(simpledialog.askstring("Add", "Coursework 1:"))
        c2 = int(simpledialog.askstring("Add", "Coursework 2:"))
        c3 = int(simpledialog.askstring("Add", "Coursework 3:"))
        exam = int(simpledialog.askstring("Add", "Exam Mark:"))

        self.students.append({
            "code": code,
            "name": name,
            "c1": c1, "c2": c2, "c3": c3,
            "exam": exam
        })

        save_students(self.students)
        messagebox.showinfo("Saved", "Student added successfully.")

    def delete_student(self):
        code = simpledialog.askstring("Delete", "Enter student code to delete:")
        if not code: return

        for s in self.students:
            if s["code"] == code:
                self.students.remove(s)
                save_students(self.students)
                messagebox.showinfo("Deleted", "Record removed.")
                return

        messagebox.showwarning("Not Found", "Student not found.")

    def update_student(self):
        code = simpledialog.askstring("Update", "Enter student code to update:")
        if not code: return

        for s in self.students:
            if s["code"] == code:
                field = simpledialog.askstring("Field", "What to update? (name/c1/c2/c3/exam)")
                if field not in ["name","c1","c2","c3","exam"]:
                    return

                new_value = simpledialog.askstring("Update", f"Enter new value for {field}:")
                if field in ["c1","c2","c3","exam"]:
                    new_value = int(new_value)

                s[field] = new_value
                save_students(self.students)
                messagebox.showinfo("Updated", "Record updated successfully.")
                return

        messagebox.showwarning("Not Found", "Student not found.")


# ===================== RUN APP ========================

root = tk.Tk()
app = StudentApp(root)
root.mainloop()
