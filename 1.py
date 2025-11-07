import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import time
import threading
import winsound
from datetime import date

# ------------------------------
# Configuration
# ------------------------------
SAVINGS_GOAL = 5000          # Set your savings goal here
DATA_FILE = "savings.json"   # File to store savings progress

# ------------------------------
# Data handling
# ------------------------------
def load_data():
    """Load savings data from file or initialize new data."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {"savings": 0.0, "last_date": str(date.today())}

    # Reset savings if a new day has started
    if data.get("last_date") != str(date.today()):
        data["savings"] = 0.0
        data["last_date"] = str(date.today())

    return data


def save_data():
    """Save current savings data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


data = load_data()

# ------------------------------
# GUI Setup
# ------------------------------
root = tk.Tk()
root.title("🐷 Money Saving Box")
root.geometry("420x450")
root.configure(bg="#2e3b4e")

# Fonts
FONT_LARGE = ("Arial", 16, "bold")
FONT_MEDIUM = ("Arial", 14)
FONT_SMALL = ("Arial", 12)

# ------------------------------
# UI Components
# ------------------------------
goal_label = tk.Label(
    root,
    text=f"🎯 Goal: Rp {SAVINGS_GOAL}",
    font=FONT_LARGE,
    fg="white",
    bg="#2e3b4e"
)
goal_label.pack(pady=20)

bar_canvas = tk.Canvas(
    root,
    width=350,
    height=40,
    bg="#3e4a61",
    bd=0,
    highlightthickness=0
)
bar_canvas.pack(pady=20)

savings_label = tk.Label(
    root,
    text="",
    font=FONT_MEDIUM,
    fg="white",
    bg="#2e3b4e"
)
savings_label.pack(pady=10)

# ------------------------------
# Functions
# ------------------------------
def round_rect(x1, y1, x2, y2, r=25, **kwargs):
    """Draw a rounded rectangle on the canvas."""
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1,
        x2, y1 + r, x2, y2 - r, x2, y2,
        x2 - r, y2, x1 + r, y2, x1, y2,
        x1, y2 - r, x1, y1 + r, x1, y1
    ]
    return bar_canvas.create_polygon(points, smooth=True, **kwargs)


def update_bar_animated():
    """Smoothly animate the progress bar when savings update."""
    target_ratio = min(data["savings"] / SAVINGS_GOAL, 1.0)
    current_ratio = getattr(update_bar_animated, "last_ratio", 0)
    steps = 50

    for i in range(steps + 1):
        ratio = current_ratio + (target_ratio - current_ratio) * (i / steps)
        width = int(350 * ratio)
        bar_canvas.delete("all")
        round_rect(5, 5, width - 5, 35, r=15, fill="#4caf50")

        savings_label.config(text=f"💰 Savings: Rp {data['savings']:.2f}")
        root.update()
        time.sleep(0.01)

    update_bar_animated.last_ratio = target_ratio


def threaded_update():
    """Run the bar update in a separate thread."""
    threading.Thread(target=update_bar_animated, daemon=True).start()


def add_money():
    """Prompt user to add money and update savings."""
    amount = simpledialog.askfloat(
        "📝 Add Money",
        "How much money do you want to add (Rp)?",
        minvalue=0
    )
    if amount is not None and amount > 0:
        winsound.PlaySound("2.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
        data["savings"] += amount
        save_data()
        threaded_update()

        if data["savings"] >= SAVINGS_GOAL:
            messagebox.showinfo("🎉 Congratulations!", "You've reached your savings goal!")
    else:
        messagebox.showwarning("⚠️ Invalid Input", "Please enter a valid amount.")


def reset_savings():
    """Reset the savings back to zero."""
    data["savings"] = 0.0
    save_data()
    threaded_update()

# ------------------------------
# Button Hover Effects
# ------------------------------
def on_enter(event):
    event.widget.configure(bg="#388E3C")

def on_leave(event):
    event.widget.configure(bg="#4CAF50")

# ------------------------------
# Buttons
# ------------------------------
add_btn = tk.Button(
    root,
    text="➕ Add Money",
    font=FONT_MEDIUM,
    bg="#4CAF50",
    fg="white",
    width=20,
    height=2,
    relief="flat",
    command=add_money
)
add_btn.pack(pady=15)
add_btn.bind("<Enter>", on_enter)
add_btn.bind("<Leave>", on_leave)

reset_btn = tk.Button(
    root,
    text="🔄 Reset Savings",
    font=FONT_SMALL,
    bg="#F44336",
    fg="white",
    width=20,
    relief="flat",
    command=reset_savings
)
reset_btn.pack(pady=10)

# ------------------------------
# Run App
# ------------------------------
threaded_update()
root.mainloop()
