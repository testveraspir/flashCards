import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database import DatabaseManager


class FlashcardsApp:
    def __init__(self, root):
        # Настраиваем окно
        self.root = root
        self.root.title("Интервальное повторение")
        self.root.geometry("600x500")
        self.root.minsize(400, 300)
        # Создаем объект DatabaseManager
        self.db = DatabaseManager()
        # Для хранения, выбранной колоды
        self.current_deck_id = None
        self.deck_listbox = None
        self.deck_ids = []
        self.current_deck_name = None

        # Основной контейнер
        self.main_container = ttk.Frame(root, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Показываем экран списка колод
        self.show_deck_list()

        # Закрытие окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.db.close()
        self.root.destroy()

    def clear_frame(self):
        """Очищает все виджеты в main_container"""
        # Это нужно, чтобы при переходе между экранами,
        # могли полностью заменить содержимое
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_deck_list(self):
        """Отображает список колод (только заголовок и пустой список)"""
        # Очищает контейнер
        self.clear_frame()
        # Заголовок
        ttk.Label(self.main_container,
                  text="Мои колоды",
                  font=("Helvetica", 14, "bold")
                  ).pack(pady=10)
        # Рамка для списка
        list_frame = ttk.Frame(self.main_container)
        list_frame.pack(fill=tk.BOTH,
                        expand=True,
                        pady=5)
        # Список колод
        self.deck_listbox = tk.Listbox(list_frame,
                                       font=("Helvetica", 12))
        scrollbar = ttk.Scrollbar(list_frame,
                                  orient="vertical",
                                  command=self.deck_listbox.yview)
        self.deck_listbox.configure(yscrollcommand=scrollbar.set)

        self.deck_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки
        btn_frame = ttk.Frame(self.main_container)
        btn_frame.pack(pady=10, fill=tk.X)

        ttk.Button(btn_frame,
                   text="Создать колоду",
                   command=self.create_deck_dialog
                   ).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame,
                   text="Выбрать колоду",
                   command=self.select_deck
                   ).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame,
                   text="Удалить колоду",
                   command=self.delete_deck
                   ).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame,
                   text="Выход",
                   command=self.on_closing
                   ).pack(fill=tk.X, pady=2)
        # Загружаем список колод
        self.refresh_deck_list()

    def refresh_deck_list(self):
        """Обновляет список колод из базы данных"""
        self.deck_listbox.delete(0, tk.END)
        decks = self.db.get_decks()
        for deck_id, name in decks:
            self.deck_listbox.insert(tk.END, name)
        # Сохраним id колод, чтобы потом по имени найти id
        self.deck_ids = [deck_id for deck_id, name in decks]

    def delete_deck(self):
        """Удаляет выбранную колоду"""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите колоду для удаления")
            return
        index = selection[0]
        deck_id = self.deck_ids[index]
        deck_name = self.deck_listbox.get(index)
        if messagebox.askyesno("Подтверждение",
                               f'Удалить колоду "{deck_name}"?\nВсе карточки будут потеряны.'):
            self.db.delete_deck(deck_id)
            self.refresh_deck_list()
            messagebox.showinfo("Успех", "Колода удалена")

    def select_deck(self):
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите колоду из списка")
            return
        index = selection[0]
        self.current_deck_id = self.deck_ids[index]
        self.current_deck_name = self.deck_listbox.get(index)
        self.show_deck_menu()

    def show_deck_menu(self):
        """Отображает меню выбранной колоды"""
        self.clear_frame()

        # Верхняя панель: название колоды и кнопка "Назад"
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame,
                  text=f"Колода: {self.current_deck_name}",
                  font=("Helvetica", 14, "bold")).pack(
            side=tk.LEFT)
        ttk.Button(header_frame,
                   text="< Назад",
                   command=self.show_deck_list
                   ).pack(side=tk.RIGHT)

        # Центральные кнопки действий
        actions_frame = ttk.Frame(self.main_container)
        actions_frame.pack(pady=40)

        ttk.Button(actions_frame,
                   text="Добавить карточку",
                   width=20,
                   command=self.add_card_dialog
                   ).pack(pady=5)
        ttk.Button(actions_frame,
                   text="Начать повторение",
                   width=20,
                   command=self.start_review_session
                   ).pack(pady=5)

    def add_card_dialog(self):
        """Временная заглушка для добавления карточки"""
        messagebox.showinfo("В разработке", "Окно добавления карточки будет здесь")

    def start_review_session(self):
        """Временная заглушка для начала повторения"""
        messagebox.showinfo("В разработке", "Режим повторения будет здесь")

    def create_deck_dialog(self):
        """Открывает диалог создания новой колоды"""
        name = simpledialog.askstring("Новая колода",
                                      "Введите название колоды (не более 50 символов):")
        if name:
            if len(name) > 50:
                messagebox.showerror("Ошибка",
                                     "Название не должно превышать 50 символов")
                return
            if self.db.add_deck(name):
                messagebox.showinfo("Успех",
                                    "Колода создана")
                self.refresh_deck_list()
            else:
                messagebox.showerror("Ошибка",
                                     "Колода с таким названием уже существует")


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardsApp(root)
    root.mainloop()
