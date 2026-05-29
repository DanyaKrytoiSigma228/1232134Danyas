import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import json
import os
import time

DATA_FILE = 'auction_data.json'

DEFAULT_DATA = {
    "users": {},
    "items": []
}


class AuctionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("D-Coin Auction")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1f1f1f")

        self.data = self.load_data()

        self.current_user = None
        self.current_balance = 0
        self.is_admin = False

        self.login_window()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def login_window(self):
        self.login_frame = tk.Frame(self.root, bg="#1f1f1f")
        self.login_frame.pack(fill="both", expand=True)

        title = tk.Label(
            self.login_frame,
            text="D-COIN AUCTION",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="#1f1f1f"
        )
        title.pack(pady=50)

        tk.Label(
            self.login_frame,
            text="Введите имя",
            font=("Arial", 16),
            fg="white",
            bg="#1f1f1f"
        ).pack(pady=10)

        self.name_entry = tk.Entry(self.login_frame, font=("Arial", 16), width=25)
        self.name_entry.pack(pady=10)

        tk.Button(
            self.login_frame,
            text="Войти",
            font=("Arial", 14),
            bg="#00aa66",
            fg="white",
            command=self.login
        ).pack(pady=20)

    def login(self):
        name = self.name_entry.get().strip()

        if not name:
            messagebox.showerror("Ошибка", "Введите имя")
            return

        self.current_user = name

        if name not in self.data["users"]:
            self.data["users"][name] = {
                "balance": 1000
            }

        self.current_balance = self.data["users"][name]["balance"]

        if name.lower() == "даня":
            self.is_admin = True

        self.save_data()

        self.login_frame.destroy()
        self.main_window()

    def main_window(self):
        top_frame = tk.Frame(self.root, bg="#2b2b2b", height=60)
        top_frame.pack(fill="x")

        self.balance_label = tk.Label(
            top_frame,
            text=f"Пользователь: {self.current_user} | Баланс: {self.current_balance} D-Coin",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#2b2b2b"
        )
        self.balance_label.pack(side="left", padx=20)

        tk.Button(
            top_frame,
            text="Выставить товар",
            command=self.add_item_window,
            bg="#0066cc",
            fg="white",
            font=("Arial", 12)
        ).pack(side="right", padx=10, pady=10)

        if self.is_admin:
            tk.Button(
                top_frame,
                text="Админ панель",
                command=self.admin_panel,
                bg="#aa0000",
                fg="white",
                font=("Arial", 12)
            ).pack(side="right", padx=10)

        self.canvas = tk.Canvas(self.root, bg="#1f1f1f", highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.items_frame = tk.Frame(self.canvas, bg="#1f1f1f")
        self.canvas.create_window((0, 0), window=self.items_frame, anchor="nw")

        self.items_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.refresh_items()
        self.update_timers()

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0

        for item in self.data["items"]:
            frame = tk.Frame(self.items_frame, bg="#2d2d2d", bd=2, relief="ridge")
            frame.grid(row=row, column=col, padx=15, pady=15)

            image_label = tk.Label(frame, bg="#2d2d2d")
            image_label.pack(padx=10, pady=10)

            try:
                if os.path.exists(item["image"]):
                    img = Image.open(item["image"])
                    img = img.resize((180, 180))
                    photo = ImageTk.PhotoImage(img)
                    image_label.configure(image=photo)
                    image_label.image = photo
                else:
                    image_label.configure(text="Нет картинки", fg="white")
            except:
                image_label.configure(text="Ошибка изображения", fg="white")

            tk.Label(
                frame,
                text=item["title"],
                font=("Arial", 14, "bold"),
                fg="white",
                bg="#2d2d2d"
            ).pack()

            tk.Label(
                frame,
                text=f"Текущая ставка: {item['price']} D",
                font=("Arial", 12),
                fg="#00ff99",
                bg="#2d2d2d"
            ).pack(pady=5)

            remaining = self.get_remaining_time(item["end_time"])

            timer_label = tk.Label(
                frame,
                text=remaining,
                font=("Arial", 11),
                fg="#ffaa00",
                bg="#2d2d2d"
            )
            timer_label.pack()

            item["timer_widget"] = timer_label

            tk.Button(
                frame,
                text="Открыть",
                command=lambda i=item: self.open_item(i),
                bg="#0088ff",
                fg="white"
            ).pack(pady=10)

            col += 1

            if col >= 4:
                col = 0
                row += 1

    def get_remaining_time(self, end_time):
        now = int(time.time())
        diff = end_time - now

        if diff <= 0:
            return "Аукцион завершён"

        hours = diff // 3600
        minutes = (diff % 3600) // 60
        seconds = diff % 60

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def update_timers(self):
        changed = False

        for item in self.data["items"]:
            remaining = self.get_remaining_time(item["end_time"])

            if "timer_widget" in item:
                try:
                    item["timer_widget"].config(text=remaining)
                except:
                    pass

            if remaining == "Аукцион завершён" and not item.get("completed"):
                item["completed"] = True

                winner = item.get("highest_bidder")
                price = item["price"]

                if winner:
                    self.data["users"][winner]["balance"] -= price
                    changed = True

        if changed:
            self.save_data()
            self.update_balance_label()

        self.root.after(1000, self.update_timers)

    def update_balance_label(self):
        self.current_balance = self.data["users"][self.current_user]["balance"]

        self.balance_label.config(
            text=f"Пользователь: {self.current_user} | Баланс: {self.current_balance} D-Coin"
        )

    def open_item(self, item):
        window = tk.Toplevel(self.root)
        window.title(item["title"])
        window.geometry("500x700")
        window.configure(bg="#1f1f1f")

        info_text = f"""
Название: {item['title']}

Описание:
{item['description']}

Автор: {item['author']}

Контакт:
{item['contact']}

Адрес продавца:
{item['address']}

Текущая ставка: {item['price']} D

Последний покупатель:
{item.get('highest_bidder', 'Нет')}
        """

        tk.Label(
            window,
            text=info_text,
            justify="left",
            font=("Arial", 12),
            fg="white",
            bg="#1f1f1f"
        ).pack(padx=20, pady=10)

        tk.Button(
            window,
            text="Поставить ставку (+10 D)",
            bg="#00aa66",
            fg="white",
            command=lambda: self.place_bid(item, window)
        ).pack(pady=20)

    def place_bid(self, item, window):
        if item.get("completed"):
            messagebox.showerror("Ошибка", "Аукцион завершён")
            return

        if item.get("highest_bidder") == self.current_user:
            messagebox.showerror("Ошибка", "Нельзя перебивать самого себя")
            return

        next_bid = item["price"] + 10
        needed_balance = int(next_bid * 1.1)

        user_balance = self.data["users"][self.current_user]["balance"]

        if user_balance < needed_balance:
            messagebox.showerror(
                "Недостаточно средств",
                f"Для ставки нужно минимум {needed_balance} D"
            )
            return

        item["price"] = next_bid
        item["highest_bidder"] = self.current_user

        self.save_data()
        self.refresh_items()

        messagebox.showinfo(
            "Успешно",
            f"Ставка поставлена: {next_bid} D"
        )

        window.destroy()

    def add_item_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить товар")
        window.geometry("500x700")
        window.configure(bg="#1f1f1f")

        labels = [
            "Название",
            "Описание",
            "Контакт",
            "Адрес продавца",
            "Начальная цена",
            "Время работы (минуты)"
        ]

        entries = {}

        for text in labels:
            tk.Label(
                window,
                text=text,
                fg="white",
                bg="#1f1f1f"
            ).pack(pady=5)

            entry = tk.Entry(window, width=40)
            entry.pack(pady=5)
            entries[text] = entry

        image_path = tk.StringVar()

        def select_image():
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg")]
            )
            image_path.set(path)

        tk.Button(
            window,
            text="Выбрать картинку",
            command=select_image,
            bg="#4444aa",
            fg="white"
        ).pack(pady=10)

        def create_item():
            try:
                minutes = int(entries["Время работы (минуты)"].get())
                price = int(entries["Начальная цена"].get())
            except:
                messagebox.showerror("Ошибка", "Цена и время должны быть числами")
                return

            item = {
                "title": entries["Название"].get(),
                "description": entries["Описание"].get(),
                "contact": entries["Контакт"].get(),
                "address": entries["Адрес продавца"].get(),
                "price": price,
                "author": self.current_user,
                "image": image_path.get(),
                "highest_bidder": None,
                "end_time": int(time.time()) + (minutes * 60),
                "completed": False
            }

            self.data["items"].append(item)
            self.save_data()
            self.refresh_items()

            messagebox.showinfo("Успешно", "Товар добавлен")
            window.destroy()

        tk.Button(
            window,
            text="Создать товар",
            command=create_item,
            bg="#00aa66",
            fg="white"
        ).pack(pady=20)

    def admin_panel(self):
        window = tk.Toplevel(self.root)
        window.title("Админ панель")
        window.geometry("700x500")
        window.configure(bg="#1f1f1f")

        tk.Label(
            window,
            text="Админ панель",
            font=("Arial", 22, "bold"),
            fg="white",
            bg="#1f1f1f"
        ).pack(pady=20)

        users_frame = tk.Frame(window, bg="#1f1f1f")
        users_frame.pack(fill="both", expand=True)

        for user, data in self.data["users"].items():
            frame = tk.Frame(users_frame, bg="#2b2b2b")
            frame.pack(fill="x", padx=20, pady=5)

            tk.Label(
                frame,
                text=f"{user} - {data['balance']} D",
                fg="white",
                bg="#2b2b2b"
            ).pack(side="left", padx=10, pady=10)

            tk.Button(
                frame,
                text="+500 D",
                command=lambda u=user: self.give_money(u, 500),
                bg="#00aa66",
                fg="white"
            ).pack(side="right", padx=10)

    def give_money(self, user, amount):
        self.data["users"][user]["balance"] += amount
        self.save_data()
        self.update_balance_label()
        messagebox.showinfo("Успешно", f"{amount} D выдано пользователю {user}")


if __name__ == '__main__':
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()
