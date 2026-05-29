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
        self.root.geometry("1250x720")
        self.root.configure(bg="#1f1f1f")

        self.data = self.load_data()

        self.current_user = None
        self.is_admin = False

        self.login_window()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_DATA, f, ensure_ascii=False, indent=4)

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_data(self):
        clean_data = {
            "users": self.data["users"],
            "items": []
        }

        for item in self.data["items"]:
            new_item = dict(item)

            if "timer_widget" in new_item:
                del new_item["timer_widget"]

            clean_data["items"].append(new_item)

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=4)

    def login_window(self):
        self.login_frame = tk.Frame(self.root, bg="#1f1f1f")
        self.login_frame.pack(fill="both", expand=True)

        tk.Label(
            self.login_frame,
            text="D-COIN AUCTION",
            font=("Arial", 30, "bold"),
            fg="white",
            bg="#1f1f1f"
        ).pack(pady=50)

        tk.Label(
            self.login_frame,
            text="Введите имя",
            font=("Arial", 16),
            fg="white",
            bg="#1f1f1f"
        ).pack(pady=10)

        self.name_entry = tk.Entry(self.login_frame, font=("Arial", 16), width=30)
        self.name_entry.pack(pady=10)

        tk.Button(
            self.login_frame,
            text="Войти",
            command=self.login,
            bg="#00aa66",
            fg="white",
            font=("Arial", 14)
        ).pack(pady=20)

    def login(self):
        name = self.name_entry.get().strip()

        if not name:
            return

        self.current_user = name

        if name not in self.data["users"]:
            self.data["users"][name] = {
                "balance": 1000,
                "inventory": [],
                "last_item_time": 0
            }

        user = self.data["users"][name]

        if "inventory" not in user:
            user["inventory"] = []

        if "last_item_time" not in user:
            user["last_item_time"] = 0

        self.is_admin = name.lower() == "даня"

        self.save_data()

        self.login_frame.destroy()
        self.main_window()

    def main_window(self):
        top = tk.Frame(self.root, bg="#2b2b2b")
        top.pack(fill="x")

        self.balance_label = tk.Label(
            top,
            text="",
            fg="white",
            bg="#2b2b2b",
            font=("Arial", 14, "bold")
        )
        self.balance_label.pack(side="left", padx=20)

        self.update_balance_label()

        tk.Button(
            top,
            text="Получить 100 D",
            command=self.claim_money,
            bg="#ffaa00",
            fg="black",
            font=("Arial", 11, "bold")
        ).pack(side="right", padx=10, pady=10)

        tk.Button(
            top,
            text="Инвентарь",
            command=self.open_inventory,
            bg="#7a00cc",
            fg="white",
            font=("Arial", 11)
        ).pack(side="right", padx=10)

        tk.Button(
            top,
            text="Выставить товар",
            command=self.add_item_window,
            bg="#0066cc",
            fg="white",
            font=("Arial", 11)
        ).pack(side="right", padx=10)

        if self.is_admin:
            tk.Button(
                top,
                text="Админ панель",
                command=self.admin_panel,
                bg="#aa0000",
                fg="white"
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

    def update_balance_label(self):
        balance = self.data["users"][self.current_user]["balance"]

        self.balance_label.config(
            text=f"Пользователь: {self.current_user} | Баланс: {balance} D-Coin"
        )

    def claim_money(self):
        self.data["users"][self.current_user]["balance"] += 100
        self.save_data()
        self.update_balance_label()

        messagebox.showinfo("Успешно", "Вы получили 100 D-Coin")

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
                image_label.configure(text="Ошибка картинки", fg="white")

            tk.Label(
                frame,
                text=item["title"],
                font=("Arial", 14, "bold"),
                fg="white",
                bg="#2d2d2d"
            ).pack()

            tk.Label(
                frame,
                text=f"Цена: {item['price']} D",
                fg="#00ff99",
                bg="#2d2d2d",
                font=("Arial", 12)
            ).pack()

            timer = tk.Label(
                frame,
                text=self.get_remaining_time(item["end_time"]),
                fg="#ffaa00",
                bg="#2d2d2d"
            )
            timer.pack()

            item["timer_widget"] = timer

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
        diff = end_time - int(time.time())

        if diff <= 0:
            return "Аукцион завершён"

        h = diff // 3600
        m = (diff % 3600) // 60
        s = diff % 60

        return f"{h:02}:{m:02}:{s:02}"

    def update_timers(self):
        changed = False

        for item in self.data["items"]:
            text = self.get_remaining_time(item["end_time"])

            if "timer_widget" in item:
                try:
                    item["timer_widget"].config(text=text)
                except:
                    pass

            if text == "Аукцион завершён" and not item.get("completed"):
                item["completed"] = True

                winner = item.get("highest_bidder")

                if winner:
                    price = item["price"]

                    self.data["users"][winner]["balance"] -= price
                    self.data["users"][winner]["inventory"].append(item["title"])

                    changed = True

        if changed:
            self.save_data()
            self.update_balance_label()

        self.root.after(1000, self.update_timers)

    def open_item(self, item):
        window = tk.Toplevel(self.root)
        window.geometry("500x700")
        window.configure(bg="#1f1f1f")

        try:
            if os.path.exists(item["image"]):
                img = Image.open(item["image"])
                img = img.resize((300, 300))
                photo = ImageTk.PhotoImage(img)

                lbl = tk.Label(window, image=photo, bg="#1f1f1f")
                lbl.image = photo
                lbl.pack(pady=10)
        except:
            pass

        text = f"""
Название: {item['title']}

Описание:
{item['description']}

Автор: {item['author']}

Контакт:
{item['contact']}

Адрес:
{item['address']}

Цена:
{item['price']} D

Лидер:
{item.get('highest_bidder', 'Нет')}
"""

        tk.Label(
            window,
            text=text,
            justify="left",
            fg="white",
            bg="#1f1f1f",
            font=("Arial", 12)
        ).pack(padx=20, pady=10)

        tk.Button(
            window,
            text="Поставить ставку +10 D",
            command=lambda: self.place_bid(item, window),
            bg="#00aa66",
            fg="white"
        ).pack(pady=20)

    def place_bid(self, item, window):
        if item.get("completed"):
            messagebox.showerror("Ошибка", "Аукцион завершён")
            return

        if item.get("highest_bidder") == self.current_user:
            messagebox.showerror("Ошибка", "Нельзя перебивать самого себя")
            return

        new_price = item["price"] + 10
        need_balance = int(new_price * 1.1)

        balance = self.data["users"][self.current_user]["balance"]

        if balance < need_balance:
            messagebox.showerror(
                "Ошибка",
                f"Нужно минимум {need_balance} D"
            )
            return

        item["price"] = new_price
        item["highest_bidder"] = self.current_user

        self.save_data()
        self.refresh_items()

        messagebox.showinfo("Успешно", "Ставка поставлена")
        window.destroy()

    def add_item_window(self):
        user = self.data["users"][self.current_user]

        if not self.is_admin:
            last = user["last_item_time"]
            now = int(time.time())

            if now - last < 86400:
                remain = 86400 - (now - last)
                hours = remain // 3600

                messagebox.showerror(
                    "Лимит",
                    f"Вы уже выставляли товар.\nЖдите {hours} ч."
                )
                return

        window = tk.Toplevel(self.root)
        window.geometry("500x700")
        window.configure(bg="#1f1f1f")

        labels = [
            "Название",
            "Описание",
            "Контакт",
            "Адрес",
            "Цена",
            "Время (минуты)"
        ]

        entries = {}

        for label in labels:
            tk.Label(
                window,
                text=label,
                fg="white",
                bg="#1f1f1f"
            ).pack(pady=5)

            e = tk.Entry(window, width=40)
            e.pack(pady=5)

            entries[label] = e

        image_path = tk.StringVar()

        def choose_image():
            path = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.jpg *.jpeg")]
            )

            image_path.set(path)

        tk.Button(
            window,
            text="Выбрать картинку",
            command=choose_image,
            bg="#4444aa",
            fg="white"
        ).pack(pady=10)

        def create_item():
            try:
                price = int(entries["Цена"].get())
                minutes = int(entries["Время (минуты)"].get())
            except:
                messagebox.showerror("Ошибка", "Цена и время должны быть числами")
                return

            item = {
                "title": entries["Название"].get(),
                "description": entries["Описание"].get(),
                "contact": entries["Контакт"].get(),
                "address": entries["Адрес"].get(),
                "price": price,
                "author": self.current_user,
                "image": image_path.get(),
                "highest_bidder": None,
                "end_time": int(time.time()) + (minutes * 60),
                "completed": False
            }

            self.data["items"].append(item)

            self.data["users"][self.current_user]["last_item_time"] = int(time.time())

            self.save_data()
            self.refresh_items()

            messagebox.showinfo("Успешно", "Товар создан")
            window.destroy()

        tk.Button(
            window,
            text="Создать",
            command=create_item,
            bg="#00aa66",
            fg="white"
        ).pack(pady=20)

    def open_inventory(self):
        window = tk.Toplevel(self.root)
        window.geometry("400x500")
        window.configure(bg="#1f1f1f")

        tk.Label(
            window,
            text="Инвентарь",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#1f1f1f"
        ).pack(pady=20)

        inventory = self.data["users"][self.current_user]["inventory"]

        if not inventory:
            tk.Label(
                window,
                text="Инвентарь пуст",
                fg="white",
                bg="#1f1f1f"
            ).pack()
        else:
            for item in inventory:
                tk.Label(
                    window,
                    text=f"• {item}",
                    fg="white",
                    bg="#1f1f1f",
                    font=("Arial", 12)
                ).pack(anchor="w", padx=30, pady=5)

    def admin_panel(self):
        window = tk.Toplevel(self.root)
        window.geometry("700x500")
        window.configure(bg="#1f1f1f")

        tk.Label(
            window,
            text="Админ панель",
            fg="white",
            bg="#1f1f1f",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        for user, data in self.data["users"].items():
            frame = tk.Frame(window, bg="#2b2b2b")
            frame.pack(fill="x", padx=20, pady=5)

            tk.Label(
                frame,
                text=f"{user} | Баланс: {data['balance']} D",
                fg="white",
                bg="#2b2b2b"
            ).pack(side="left", padx=10, pady=10)

            tk.Button(
                frame,
                text="+500 D",
                command=lambda u=user: self.give_money(u),
                bg="#00aa66",
                fg="white"
            ).pack(side="right", padx=10)

    def give_money(self, user):
        self.data["users"][user]["balance"] += 500

        self.save_data()
        self.update_balance_label()

        messagebox.showinfo("Успешно", f"500 D выдано {user}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AuctionApp(root)
    root.mainloop()
