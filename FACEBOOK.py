import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import random
import re

# ===== STYLE GRUP =====

AUDIENCE_STYLES = {
    "normiki":    "prosty ale odważny język, trochę oceny, coś z obecnego życia, nie lubię chamstwa",
    "boomers":    "narzekanie, nostalgia, kiedyś było lepiej, humor ale mocna krytyka, nie nawidzę zdrajców",
    "młodzi":     "memy, krytyka, szybkie punchline'y, chaos, małe doświadczenie życiowe",
    "pracownicy": "frustracja, robota, obawy o utratę pracy, wątek patriotyczny, nie lubię prostactwa",
    "hejterzy":   "ostry ton, ironia, krytyka, prawdziwi patrioci, więcej z historii,wiecej chamstwa,nie lubię prostactwa",
}

# ===== SZABLONY POSTÓW =====

TEMPLATES = {
    "normiki": [
        "Serio ktoś to pochwalił? {topic} to już przesada.",
        "Nie wiem co gorsze – {topic} czy ludzie, którzy to lajkują.",
        "Codziennie nowy {topic}, codziennie mniej wiary w ludzi. Co dalej?",
        "{topic} i wszyscy udają, że jest normalnie. Serio?",
    ],
    "boomers": [
        "Kiedyś to było normalne, dziś {topic} to norma. Dokąd zmierzamy?",
        "Za moich czasów {topic} nie przechodziło. I dobrze było.",
        "{topic}? Nostalgia wraca, ale rozsądek gdzieś zniknął. Prawda?",
        "Patrzę na {topic} i myślę: kiedyś było lepiej. Kto jeszcze tak ma?",
    ],
    "młodzi": [
        "{topic} XD ale czemu to jest aż tak zabawne?",
        "Nie no, {topic} to hit. Kto jeszcze to widział?",
        "{topic} i cała ta drama – serio? XD",
        "{topic} to mem sam w sobie. Kto to wymyślił?",
    ],
    "pracownicy": [
        "Po robocie widzę {topic} i zastanawiam się, po co to komu.",
        "{topic} zamiast konkretów. Tak wygląda dzisiejsza rzeczywistość?",
        "Robota, dom, a tu jeszcze {topic}. Kiedy normalność?",
        "Człowiek haruje, a tu {topic}. Serio nikt tego nie widzi?",
    ],
    "hejterzy": [
        "{topic} – kolejny dowód, że ktoś tu nie myśli. Serio?",
        "I znowu {topic}. Krytyka oczywista, ale ktoś to kupi?",
        "{topic}? Internet nie przestaje zaskakiwać. Kto za to odpowiada?",
        "{topic} i cała ta farsa. Prawdziwi patrioci to widzą. Kto jeszcze?",
    ],
}

TOPICS = [
    "ten widok", "ta sytuacja", "ta decyzja", "ten trend",
    "ta moda", "ten pomysł", "to zachowanie", "ten obrazek",
    "ta sprawa", "ten temat",
]

# ===== SCORING =====

TRIGGERS = ["serio", "dramat", "hit", "xd", "kto", "dlaczego", "co dalej", "prawda", "kiedyś", "norma"]

AUDIENCE_WORDS = {
    "normiki":    ["serio", "przesada", "lajk", "normalnie"],
    "boomers":    ["kiedyś", "norma", "rozsądek", "lepiej"],
    "młodzi":     ["xd", "hit", "drama", "mem"],
    "pracownicy": ["robota", "konkret", "rzeczywistość", "haruje"],
    "hejterzy":   ["krytyka", "internet", "odpowiada", "patrioci", "farsa","rzeczywistość"],
}

def score_post(text, audience):
    text_low = text.lower()
    words = re.findall(r"\w+", text_low)

    # 1. Długość w optymalnym przedziale (40–160 znaków = najlepszy zasięg)
    n = len(text)
    if 40 <= n <= 160:
        len_score = 10
    elif n < 40:
        len_score = 5
    else:
        len_score = 6

    # 2. Pytanie na końcu = większy engagement
    question_bonus = 3 if "?" in text else 0

    # 3. Trigger words (max 3)
    trigger_score = min(sum(1 for t in TRIGGERS if t in text_low), 3) * 2

    # 4. Zgodność z targetem (słowa kluczowe grupy)
    audience_words = AUDIENCE_WORDS.get(audience, [])
    match_score = sum(2 for w in audience_words if w in text_low)

    # 5. Kara za powtórzenia (te same słowa 3+ razy)
    repetition_penalty = 0
    for w in set(words):
        if words.count(w) >= 3:
            repetition_penalty -= 2

    total = len_score + question_bonus + trigger_score + match_score + repetition_penalty
    return max(0, min(20, total))

# ===== GENERATOR =====

def generuj_posty(audience):
    templates = TEMPLATES.get(audience, TEMPLATES["normiki"])
    chosen = random.sample(templates, k=min(3, len(templates)))
    posts = []
    for tpl in chosen:
        topic = random.choice(TOPICS)
        posts.append(tpl.format(topic=topic))
    return posts

# ===== APP =====

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("💣 VIRAL MACHINE (offline)")
        self.root.geometry("700x650")
        self.image = None
        self.build()

    def build(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", pady=10)

        tk.Button(
            top, text="📸 Wybierz zdjęcie", command=self.pick,
            bg="#4CAF50", fg="white", font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.img_label = tk.Label(
            top, text="", fg="green", font=("Arial", 10, "bold")
        )
        self.img_label.pack(pady=5)

        tk.Label(
            top, text="(tryb offline – zdjęcie nie jest analizowane)",
            fg="gray", font=("Arial", 8)
        ).pack()

        self.audience_var = tk.StringVar(value="normiki")
        tk.OptionMenu(
            top, self.audience_var, *AUDIENCE_STYLES.keys()
        ).pack(pady=5)

        self.generate_btn = tk.Button(
            top, text="🚀 GENERUJ", command=self.generate,
            bg="#2196F3", fg="white", font=("Arial", 11, "bold")
        )
        self.generate_btn.pack(pady=10)

        middle = tk.Frame(self.root)
        middle.pack(fill="both", expand=True)

        self.output = scrolledtext.ScrolledText(
            middle, font=("Arial", 11), wrap=tk.WORD
        )
        self.output.pack(fill="both", expand=True, padx=10, pady=5)

        bottom = tk.Frame(self.root)
        bottom.pack(fill="x", pady=10)

        tk.Button(
            bottom, text="📋 Kopiuj", command=self.copy,
            bg="#9C27B0", fg="white", width=15
        ).pack(side="left", padx=10)

        tk.Button(
            bottom, text="🧹 Wyczyść", command=self.clear,
            bg="#F44336", fg="white", width=15
        ).pack(side="left", padx=10)

    def pick(self):
        file = filedialog.askopenfilename(
            filetypes=[
                ("Obrazy", "*.jpg *.jpeg *.png *.webp"),
                ("Wszystkie pliki", "*.*"),
            ]
        )
        if file:
            self.image = file
            nazwa = os.path.basename(file)
            self.img_label.config(text=f"📁 Zaimportowano:\n{nazwa}")

    def generate(self):
        if not self.image:
            messagebox.showwarning("Błąd", "Dodaj zdjęcie")
            return

        audience = self.audience_var.get()
        posts = generuj_posty(audience)
        self.show_results(posts, audience)

    def show_results(self, posts, audience):
        if not posts:
            self.output.delete("1.0", tk.END)
            self.output.insert("1.0", "❌ Brak postów.")
            return

        scored = [(p, score_post(p, audience)) for p in posts]
        scored.sort(key=lambda x: x[1], reverse=True)

        out = ""
        for i, (post, score) in enumerate(scored, 1):
            if i == 1:
                out += "🏆 NAJLEPSZY POST\n\n"
            out += f"===== WERSJA {i} =====\n"
            out += f"SCORE: {score}/20\n\n"
            out += post + "\n\n"

        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", out)

    def copy(self):
        text = self.output.get("1.0", tk.END)
        if not text.strip():
            messagebox.showinfo("Info", "Nie ma tekstu.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("OK", "Skopiowano.")

    def clear(self):
        self.output.delete("1.0", tk.END)
        self.img_label.config(text="")
        self.image = None

# ===== START =====

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()