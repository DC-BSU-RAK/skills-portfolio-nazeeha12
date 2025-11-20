import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# winsound is Windows-only — import safely
try:
    import winsound
    _HAS_WINSOUND = True
except Exception:
    _HAS_WINSOUND = False

# --------------------- Load Jokes (robust) --------------------- #
def load_jokes(filename="randomJokes.txt"):
    """
    Accepts lines like:
      Setup?Punchline
      Setup? Punchline
      Setup|Punchline
      Setup::Punchline
    Falls back to a small built-in list if file not found or malformed.
    """
    jokes = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line:
                    continue
                # Prefer splitting on the first question mark (common)
                if "?" in line:
                    parts = line.split("?", 1)
                    setup = parts[0].strip() + "?"
                    punch = parts[1].strip()
                    if punch:
                        jokes.append((setup, punch))
                        continue
                # try other separators
                for sep in ["|", "::", " - ", " — ", "\t"]:
                    if sep in line:
                        parts = line.split(sep, 1)
                        setup = parts[0].strip()
                        punch = parts[1].strip()
                        jokes.append((setup, punch))
                        break
                else:
                    # if no separator found, skip — it's malformed
                    continue
        if not jokes:
            raise ValueError("No valid jokes found in file.")
        return jokes
    except FileNotFoundError:
        messagebox.showwarning("Warning", f"{filename} not found — using built-in jokes.")
    except Exception as e:
        # show a quick warning and then continue with the built-in jokes
        messagebox.showwarning("Warning", f"Couldn't parse {filename}. Using built-in jokes.")
    # fallback jokes (always valid)
    return [
        ("Why don't scientists trust atoms?", "Because they make up everything."),
        ("Why did the scarecrow win an award?", "Because he was outstanding in his field."),
        ("What do you call fake spaghetti?", "An impasta."),
    ]


# --------------------- Joke App --------------------- #
class JokeAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Joke Assistant 😂")
        self.root.geometry("700x500")
        self.root.configure(bg="#1e272e")

        self.jokes = load_jokes()
        self.current_joke = None
        self.dark_mode = True
        self._anim_after_id = None  # to cancel animation if needed

        # ---------------- UI Layout ---------------- #
        title = tk.Label(root, text="🤣 Joke Assistant 2.0 🤣",
                         font=("Arial", 24, "bold"),
                         bg="#1e272e", fg="white")
        title.pack(pady=10)

        # Main card
        self.card = tk.Frame(root, bg="#485460", relief="groove", bd=3)
        self.card.pack(pady=15, ipadx=20, ipady=20, fill="x", padx=30)

        # Setup Text
        self.setup_label = tk.Label(self.card, text="", font=("Arial", 18, "bold"),
                                    bg="#485460", fg="white", wraplength=650, justify="left")
        self.setup_label.pack(pady=10)

        # Punchline Text
        self.punchline_label = tk.Label(self.card, text="", font=("Arial", 16),
                                        bg="#485460", fg="#d2dae2", wraplength=650, justify="left")
        self.punchline_label.pack(pady=10)

        # Buttons Frame
        btn_frame = tk.Frame(root, bg="#1e272e")
        btn_frame.pack(pady=10)

        btn_style = {"font": ("Arial", 13), "width": 18, "relief": "ridge"}

        tk.Button(btn_frame, text="Alexa, Tell Me a Joke",
                  command=self.show_joke, bg="#0fbcf9", fg="black", **btn_style).grid(row=0, column=0, padx=5, pady=5)

        tk.Button(btn_frame, text="Show Punchline",
                  command=self.show_punchline, bg="#05c46b", fg="black", **btn_style).grid(row=0, column=1, padx=5, pady=5)

        tk.Button(btn_frame, text="Next Joke",
                  command=self.show_joke, bg="#ffa801", fg="black", **btn_style).grid(row=1, column=0, padx=5, pady=5)

        tk.Button(btn_frame, text="Laugh Sound",
                  command=self.play_laugh, bg="#ff5e57", fg="black", **btn_style).grid(row=1, column=1, padx=5, pady=5)

        tk.Button(btn_frame, text="Toggle Dark/Light Mode",
                  command=self.toggle_mode, bg="#d2dae2", fg="black", **btn_style).grid(row=2, column=0, padx=5, pady=5)

        tk.Button(btn_frame, text="Quit",
                  command=root.quit, bg="#ff3f34", fg="white", **btn_style).grid(row=2, column=1, padx=5, pady=5)

        # ---------------- Joke History Section ---------------- #
        history_frame = tk.LabelFrame(root, text="Joke History", font=("Arial", 14),
                                      bg="#1e272e", fg="white")
        history_frame.pack(fill="both", padx=20, pady=10, ipadx=10)

        self.history_list = tk.Listbox(history_frame, height=7, font=("Arial", 12),
                                       bg="#2f3542", fg="#dcdde1")
        self.history_list.pack(fill="both", padx=10, pady=10)

    # ------------------- Core Functions ------------------- #
    def show_joke(self):
        """Pick a random joke and animate the setup. Clear previous punchline."""
        if not self.jokes:
            messagebox.showinfo("Info", "No jokes available.")
            return

        # Cancel any running animation
        if self._anim_after_id:
            try:
                self.root.after_cancel(self._anim_after_id)
            except Exception:
                pass
            self._anim_after_id = None

        self.current_joke = random.choice(self.jokes)
        setup, _ = self.current_joke

        self.setup_label.config(text="")
        self.punchline_label.config(text="")

        # Start typewriter animation for setup
        self._typewriter(self.setup_label, setup, 0)

        # Put the setup into history right away (so user sees history even if they don't press punchline)
        self.history_list.insert(tk.END, setup)

    def show_punchline(self):
        """Reveal the current punchline with animation. If no joke chosen, prompt user."""
        if not self.current_joke:
            messagebox.showinfo("Info", "Ask for a joke first!")
            return

        _, punchline = self.current_joke

        # Cancel any running animation on punchline
        if self._anim_after_id:
            try:
                self.root.after_cancel(self._anim_after_id)
            except Exception:
                pass
            self._anim_after_id = None

        self._typewriter(self.punchline_label, punchline, 0)

    # ------------------- Animation (safe) ------------------- #
    def _typewriter(self, label, text, index, delay=30):
        """Update label one character at a time using after() (safe for Tkinter)."""
        # Convert delay to milliseconds if user passed seconds by mistake
        ms = delay if isinstance(delay, int) else int(delay * 1000)
        label.config(text=text[:index])
        if index < len(text):
            # Schedule next character
            self._anim_after_id = self.root.after(ms, lambda: self._typewriter(label, text, index + 1, delay))
        else:
            self._anim_after_id = None

    # ------------------- Extra Features ------------------- #
    def play_laugh(self):
        """Play laugh beep on Windows; otherwise show playful message."""
        if _HAS_WINSOUND:
            # quick beep sequence
            try:
                for _ in range(3):
                    winsound.Beep(900, 120)
                    winsound.Beep(1200, 120)
            except Exception:
                # if winsound fails for any reason, ignore
                pass
        else:
            messagebox.showinfo("Laugh", "😄 (Laugh sound only available on Windows)")

    def toggle_mode(self):
        """Switch between dark and light themes."""
        if self.dark_mode:
            self.root.configure(bg="white")
            self.card.configure(bg="#dfe4ea")
            self.setup_label.configure(bg="#dfe4ea", fg="black")
            self.punchline_label.configure(bg="#dfe4ea", fg="black")
            self.dark_mode = False
        else:
            self.root.configure(bg="#1e272e")
            self.card.configure(bg="#485460")
            self.setup_label.configure(bg="#485460", fg="white")
            self.punchline_label.configure(bg="#485460", fg="#d2dae2")
            self.dark_mode = True


# --------------------- Main --------------------- #
if __name__ == "__main__":
    root = tk.Tk()
    app = JokeAssistant(root)
    root.mainloop()
