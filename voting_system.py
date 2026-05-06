import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os

parties = ["NOTA", "Party A", "Party B", "Party C", "Party D"]
db_path = "voting_system.db"

# SQLite Setup
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS votes")  # For testing purposes only
    cursor.execute("""
        CREATE TABLE votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_code TEXT UNIQUE,
            age INTEGER,
            party TEXT
        )
    """)
    conn.commit()
    conn.close()

def has_voted(user_code):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM votes WHERE user_code = ?", (user_code,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_vote(party, user_code, age):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO votes (user_code, age, party) VALUES (?, ?, ?)", (user_code, age, party))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def count_votes():
    votes = {party: 0 for party in parties}
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT party, COUNT(*) FROM votes GROUP BY party")
    for party, count in cursor.fetchall():
        if party in votes:
            votes[party] = count
    conn.close()
    return votes

# Voting logic
def cast_vote():
    code = code_entry.get().strip()
    age_str = age_entry.get().strip()
    selected = selected_party.get()

    if not code or not age_str:
        messagebox.showwarning("Error", "Please enter both code and age.")
        return

    try:
        age = int(age_str)
    except ValueError:
        messagebox.showwarning("Invalid Age", "Age must be a valid number.")
        return

    if age < 18:
        messagebox.showerror("Ineligible", "You must be at least 18 years old to vote.")
        return

    if not selected:
        messagebox.showwarning("Error", "Please select a party to vote for.")
        return

    if has_voted(code):
        messagebox.showerror("Duplicate", "You have already voted!")
        return

    if save_vote(selected, code, age):
        messagebox.showinfo("Success", f"Vote cast for {selected}")
        code_entry.delete(0, tk.END)
        age_entry.delete(0, tk.END)
        selected_party.set(None)
    else:
        messagebox.showerror("Error", "Failed to cast vote.")

def show_results():
    votes = count_votes()
    max_votes = max(votes.values())
    min_votes = min(votes.values())

    majority = [p for p in votes if votes[p] == max_votes]
    minority = [p for p in votes if votes[p] == min_votes]

    result = "Voting Results:\n"
    for party, count in votes.items():
        result += f"{party}: {count} vote{'s' if count != 1 else ''}\n"

    result += f"\nMajority Party: {', '.join(majority)} with {max_votes} vote(s)"
    result += f"\nMinority Party: {', '.join(minority)} with {min_votes} vote(s)"

    messagebox.showinfo("Results", result)

# GUI Setup
root = tk.Tk()
root.title("Voting System with SQLite")
root.geometry("700x500")

# Background image setup
try:
    bg_img = Image.open("voting_bg.png")
    bg_img_resized = bg_img.resize((700, 500), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_img_resized)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
except Exception as e:
    print("Background image not loaded:", e)

frame = tk.Frame(root, bg='white', bd=4)
frame.place(relx=0.5, rely=0.5, anchor='center')

tk.Label(frame, text="Enter your unique code:", bg="white", font=('Arial', 12)).pack(pady=5)
code_entry = tk.Entry(frame, font=('Arial', 12))
code_entry.pack(pady=5)

tk.Label(frame, text="Enter your age:", bg="white", font=('Arial', 12)).pack(pady=5)  # Age input
age_entry = tk.Entry(frame, font=('Arial', 12))
age_entry.pack(pady=5)

tk.Label(frame, text="Choose a party to vote for:", bg="white", font=('Arial', 12)).pack(pady=5)
selected_party = tk.StringVar()
for party in parties:
    tk.Radiobutton(frame, text=party, variable=selected_party, value=party, bg="white", font=('Arial', 11)).pack(anchor="w")

tk.Button(frame, text="Cast Vote", command=cast_vote, font=('Arial', 12)).pack(pady=10)
tk.Button(frame, text="Show Results", command=show_results, font=('Arial', 12)).pack(pady=5)

init_db()
root.mainloop()
