import tkinter as tk
from tkinter import messagebox
import random

# -----------------------
# Function Definitions
# -----------------------

def displayMenu():
    """Display difficulty level menu."""
    clear_window()
    tk.Label(root, text="SELECT DIFFICULTY LEVEL", font=("Arial", 16, "bold")).pack(pady=10)
    
    tk.Button(root, text="1. Easy", width=20, command=lambda: start_quiz("Easy")).pack(pady=5)
    tk.Button(root, text="2. Moderate", width=20, command=lambda: start_quiz("Moderate")).pack(pady=5)
    tk.Button(root, text="3. Advanced", width=20, command=lambda: start_quiz("Advanced")).pack(pady=5)

def randomInt(level):
    """Return a random integer based on difficulty."""
    if level == "Easy":
        return random.randint(1, 9)
    elif level == "Moderate":
        return random.randint(10, 99)
    else:  # Advanced
        return random.randint(1000, 9999)

def decideOperation():
    """Randomly decide between + or -"""
    return random.choice(['+', '-'])

def displayProblem():
    """Display the current arithmetic problem."""
    clear_window()
    global current_question, attempts
    
    if current_question < 10:
        num1 = randomInt(level)
        num2 = randomInt(level)
        operation = decideOperation()
        
        # Avoid negative results in subtraction for simplicity
        if operation == '-' and num2 > num1:
            num1, num2 = num2, num1
        
        problems.append((num1, num2, operation))
        question_text.set(f"Question {current_question + 1}: {num1} {operation} {num2} = ")
        
        tk.Label(root, textvariable=question_text, font=("Arial", 14)).pack(pady=10)
        entry_answer.delete(0, tk.END)
        entry_answer.pack(pady=5)
        
        tk.Button(root, text="Submit", command=check_answer).pack(pady=10)
    else:
        displayResults()

def isCorrect(num1, num2, op, answer):
    """Check if user's answer is correct."""
    correct = num1 + num2 if op == '+' else num1 - num2
    return answer == correct

def check_answer():
    """Check user's answer and update score."""
    global score, current_question, attempts
    
    num1, num2, op = problems[current_question]
    
    try:
        user_ans = int(entry_answer.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")
        return
    
    if isCorrect(num1, num2, op, user_ans):
        if attempts == 1:
            score += 10
            messagebox.showinfo("Correct!", "Perfect! +10 points")
        else:
            score += 5
            messagebox.showinfo("Correct!", "Correct on second try! +5 points")
        current_question += 1
        attempts = 1
        displayProblem()
    else:
        if attempts == 1:
            attempts += 1
            messagebox.showwarning("Try Again", "Incorrect. Try once more!")
        else:
            messagebox.showinfo("Incorrect", f"Wrong again! The correct answer was {num1 + num2 if op == '+' else num1 - num2}")
            current_question += 1
            attempts = 1
            displayProblem()

def displayResults():
    """Display final score and grade."""
    clear_window()
    grade = ""
    if score >= 90:
        grade = "A+"
    elif score >= 80:
        grade = "A"
    elif score >= 70:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "F"
    
    tk.Label(root, text=f"Final Score: {score}/100", font=("Arial", 16)).pack(pady=10)
    tk.Label(root, text=f"Your Grade: {grade}", font=("Arial", 14, "bold")).pack(pady=5)
    
    tk.Button(root, text="Play Again", command=displayMenu).pack(pady=10)
    tk.Button(root, text="Exit", command=root.destroy).pack(pady=5)

def start_quiz(selected_level):
    """Initialize quiz state."""
    global level, score, current_question, attempts, problems
    level = selected_level
    score = 0
    current_question = 0
    attempts = 1
    problems = []
    displayProblem()

def clear_window():
    """Clear all widgets in window."""
    for widget in root.winfo_children():
        widget.pack_forget()

# -----------------------
# Tkinter GUI Setup
# -----------------------
root = tk.Tk()
root.title("Arithmetic Quiz Game")
root.geometry("400x300")

question_text = tk.StringVar()
entry_answer = tk.Entry(root, font=("Arial", 12))

displayMenu()

root.mainloop()
