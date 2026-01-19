import tkinter as tk
from tkinter import messagebox
import requests
import random
import html

# -----------------------------
# Trivia API class
# -----------------------------
class TriviaAPI:
    BASE_URL = "https://opentdb.com/api.php"

    def fetch_questions(self, amount, category, difficulty):
        params = {
            "amount": amount,
            "category": category,
            "difficulty": difficulty,
            "type": "multiple"
        }
        response = requests.get(self.BASE_URL, params=params)
        response.raise_for_status()
        return response.json()["results"]

# -----------------------------
# Quiz Manager class
# -----------------------------
class QuizManager:
    def __init__(self, questions):
        self.questions = questions
        self.score = 0
        self.index = 0

    def has_next(self):
        return self.index < len(self.questions)

    def get_current_question(self):
        q = self.questions[self.index]
        answers = q["incorrect_answers"] + [q["correct_answer"]]
        random.shuffle(answers)

        return {
            "question": html.unescape(q["question"]),
            "answers": [html.unescape(a) for a in answers],
            "correct": html.unescape(q["correct_answer"])
        }

    def submit_answer(self, answer):
        correct = html.unescape(self.questions[self.index]["correct_answer"])
        if answer == correct:
            self.score += 1
        self.index += 1

# -----------------------------
# GUI Frames
# -----------------------------
class SetupFrame(tk.Frame):
    def __init__(self, master, start_quiz):
        super().__init__(master)
        self.start_quiz = start_quiz

        tk.Label(self, text="TriviaLab", font=("Arial", 18)).pack(pady=10)

        tk.Label(self, text="Number of questions:").pack()
        self.amount = tk.Entry(self)
        self.amount.insert(0, "5")
        self.amount.pack()

        tk.Label(self, text="Difficulty:").pack()
        self.difficulty = tk.StringVar(value="easy")
        tk.OptionMenu(self, self.difficulty, "easy", "medium", "hard").pack()

        tk.Label(self, text="Category (optional, ID 9-32):").pack()
        self.category = tk.Entry(self)
        self.category.pack()

        tk.Button(self, text="Start Quiz", command=self.begin).pack(pady=10)

    def begin(self):
        try:
            amount = int(self.amount.get())
            diff = self.difficulty.get()
            cat_text = self.category.get()
            category = int(cat_text) if cat_text.isdigit() else None
            self.start_quiz(amount, diff, category)
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number of questions and category")

class QuizFrame(tk.Frame):
    def __init__(self, master, quiz_manager, finish):
        super().__init__(master)
        self.quiz = quiz_manager
        self.finish = finish
        self.answer = tk.StringVar()
        self.load_question()

    def load_question(self):
        if not self.quiz.has_next():
            self.finish()
            return

        data = self.quiz.get_current_question()

        tk.Label(self, text=f"Question {self.quiz.index + 1}", font=("Arial", 14)).pack(pady=5)
        tk.Label(self, text=data["question"], wraplength=400, font=("Arial", 12)).pack(pady=10)
        for a in data["answers"]:
            tk.Radiobutton(self, text=a, value=a, variable=self.answer, font=("Arial", 10)).pack(anchor="w")

        tk.Button(self, text="Submit", command=self.submit).pack(pady=10)

    def submit(self):
        if self.answer.get() == "":
            messagebox.showwarning("Warning", "Please select an answer")
            return
        self.quiz.submit_answer(self.answer.get())
        self.destroy()
        QuizFrame(self.master, self.quiz, self.finish).pack()

# -----------------------------
# Main App
# -----------------------------
class TriviaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TriviaLab")
        self.geometry("500x500")
        self.api = TriviaAPI()
        self.current_frame = None
        self.show_setup()

    def show_setup(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = SetupFrame(self, self.start_quiz)
        self.current_frame.pack(fill="both", expand=True)

    def start_quiz(self, amount, difficulty, category):
        try:
            questions = self.api.fetch_questions(amount, category, difficulty)
        except requests.RequestException:
            messagebox.showerror("Error", "Failed to fetch questions. Check your internet connection.")
            return

        if not questions:
            messagebox.showinfo("Info", "No questions returned with these settings")
            return

        self.quiz_manager = QuizManager(questions)
        self.current_frame.destroy()
        self.current_frame = QuizFrame(self, self.quiz_manager, self.finish_quiz)
        self.current_frame.pack(fill="both", expand=True)

    def finish_quiz(self):
        score = self.quiz_manager.score
        total = len(self.quiz_manager.questions)
        messagebox.showinfo("Quiz Finished", f"You scored {score}/{total}")
        self.show_setup()

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    app = TriviaApp()
    app.mainloop()

