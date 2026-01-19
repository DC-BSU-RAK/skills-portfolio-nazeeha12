import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
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
# Neon styles
# -----------------------------
NEON_COLORS = ["#ff39ff", "#00ffff"]  # pink, blue only
TEXT_FONT = ("Helvetica", 14, "bold")
TITLE_FONT = ("Helvetica", 20, "bold")

def neon_color(index):
    return NEON_COLORS[index % len(NEON_COLORS)]

# -----------------------------
# GUI Frames
# -----------------------------
class SetupFrame(tk.Frame):
    def __init__(self, master, start_quiz, bg_image):
        super().__init__(master, bg="black")
        self.start_quiz = start_quiz
        self.bg_image = bg_image
        self.create_widgets()

    def create_widgets(self):
        # Background image
        if self.bg_image:
            self.bg_label = tk.Label(self, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(self, text="TriviaLab", font=TITLE_FONT, fg=neon_color(0), bg="black").pack(pady=10)
        tk.Label(self, text="Number of questions:", font=TEXT_FONT, fg=neon_color(1), bg="black").pack()
        self.amount = tk.Entry(self, font=TEXT_FONT, bg="black", fg=neon_color(0), insertbackground=neon_color(0))
        self.amount.insert(0, "5")
        self.amount.pack()

        tk.Label(self, text="Difficulty:", font=TEXT_FONT, fg=neon_color(0), bg="black").pack()
        self.difficulty = tk.StringVar(value="easy")
        tk.OptionMenu(self, self.difficulty, "easy", "medium", "hard").config(bg="black", fg=neon_color(1), highlightbackground="black")
        tk.OptionMenu(self, self.difficulty, "easy", "medium", "hard").pack()

        tk.Label(self, text="Category (optional, ID 9-32):", font=TEXT_FONT, fg=neon_color(1), bg="black").pack()
        self.category = tk.Entry(self, font=TEXT_FONT, bg="black", fg=neon_color(0), insertbackground=neon_color(0))
        self.category.pack()

        tk.Button(self, text="Start Quiz", font=TEXT_FONT, bg="black", fg=neon_color(1),
                  command=self.begin, highlightbackground="black").pack(pady=10)

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
    def __init__(self, master, quiz_manager, finish, bg_image):
        super().__init__(master, bg="black")
        self.quiz = quiz_manager
        self.finish = finish
        self.answer = tk.StringVar()
        self.bg_image = bg_image
        self.load_question()

    def load_question(self):
        if not self.quiz.has_next():
            self.finish()
            return

        data = self.quiz.get_current_question()

        # Background image
        if self.bg_image:
            self.bg_label = tk.Label(self, image=self.bg_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(self, text=f"Question {self.quiz.index + 1}", font=TITLE_FONT,
                 fg=neon_color(0), bg="black").pack(pady=5)
        tk.Label(self, text=data["question"], wraplength=400, font=TEXT_FONT,
                 fg=neon_color(1), bg="black").pack(pady=10)

        for i, a in enumerate(data["answers"]):
            tk.Radiobutton(self, text=a, value=a, variable=self.answer, font=TEXT_FONT,
                           fg=neon_color(i), bg="black", selectcolor="black",
                           activebackground="black", activeforeground=neon_color(i)).pack(anchor="w")

        tk.Button(self, text="Submit", font=TEXT_FONT, bg="black", fg=neon_color(1),
                  command=self.submit, highlightbackground="black").pack(pady=10)

    def submit(self):
        if self.answer.get() == "":
            messagebox.showwarning("Warning", "Please select an answer")
            return
        self.quiz.submit_answer(self.answer.get())
        self.destroy()
        QuizFrame(self.master, self.quiz, self.finish, self.bg_image).pack()

# -----------------------------
# Main App
# -----------------------------
class TriviaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TriviaLab")
        self.geometry("500x500")
        self.configure(bg="black")
        self.api = TriviaAPI()
        self.current_frame = None

        # Load background image
        try:
            image = Image.open("background.png")  # Put your image in the same folder
            image = image.resize((500, 500))
            self.bg_image = ImageTk.PhotoImage(image)
        except Exception:
            self.bg_image = None  # Won’t crash if image is missing

        self.show_setup()

    def show_setup(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = SetupFrame(self, self.start_quiz, self.bg_image)
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
        self.current_frame = QuizFrame(self, self.quiz_manager, self.finish_quiz, self.bg_image)
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
