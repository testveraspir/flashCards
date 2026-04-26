import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
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
        self.q_text = None
        self.a_text = None
        self.cards_queue = []
        self.card_frame = None
        self.progress_label = None
        self.answer_label = None
        self.answer_container = None
        self.btn_flip = None
        self.question_label = None
        self.history_label = None
        self.current_card_id = None

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
                               f'Удалить колоду "{deck_name}"?'
                               f'\nВсе карточки будут потеряны.'):
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
        dialog = tk.Toplevel(self.root)
        dialog.title("Новая карточка")
        dialog.geometry("500x400")

        # Метка и поле для Вопроса
        ttk.Label(dialog, text="Вопрос:").pack(anchor="w", padx=10, pady=(10, 0))
        self.q_text = scrolledtext.ScrolledText(dialog, width=50, height=8)
        self.q_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Метка и поле для Ответа
        ttk.Label(dialog, text="Ответ:").pack(anchor="w", padx=10)
        self.a_text = scrolledtext.ScrolledText(dialog, width=50, height=8)
        self.a_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Кнопка сохранения
        def save_card():
            q = self.q_text.get("1.0", tk.END).strip()
            a = self.a_text.get("1.0", tk.END).strip()
            if not q or not a:
                messagebox.showerror("Ошибка",
                                     "Заполните оба поля: вопрос и ответ")
                return

            # Импорт get_today_str из utils
            from utils import get_today_str
            next_date = get_today_str()

            self.db.add_card(self.current_deck_id, q, a, next_date)
            messagebox.showinfo("Успех", "Карточка добавлена")
            dialog.destroy()

        ttk.Button(dialog, text="Сохранить", command=save_card).pack(pady=10)

    def start_review_session(self):
        """Начинает сессию повторения"""
        due_cards = self.db.get_due_cards(self.current_deck_id)

        if not due_cards:
            messagebox.showinfo("Информация", "На сегодня все карточки изучены!")
            return

        self.cards_queue = list(due_cards)
        self.clear_frame()
        self.setup_review_ui()
        self.show_next_card()

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

    def setup_review_ui(self):
        """Создаёт интерфейс для режима повторения"""
        # Верхняя панель (кнопка "Прервать")
        top_frame = ttk.Frame(self.main_container)
        top_frame.pack(fill=tk.X, pady=5)
        ttk.Button(top_frame,
                   text="Прервать",
                   command=self.show_deck_list
                   ).pack(side=tk.LEFT)

        # Основная область карточки
        self.card_frame = ttk.Frame(self.main_container,
                                    borderwidth=2,
                                    relief="groove",
                                    padding=20)
        self.card_frame.pack(fill=tk.BOTH,
                             expand=True, padx=20, pady=10)

        # История повторений
        self.history_label = ttk.Label(self.card_frame,
                                       text="",
                                       foreground="gray",
                                       font=("Helvetica", 9))
        self.history_label.pack(anchor="w", pady=(0, 10))

        # Вопрос
        ttk.Label(self.card_frame, text="Вопрос:",
                  font=("Helvetica", 10, "bold")
                  ).pack(anchor="w")
        self.question_label = ttk.Label(self.card_frame,
                                        text="",
                                        wraplength=500,
                                        font=("Helvetica", 12))
        self.question_label.pack(anchor="w", pady=5)

        # Кнопка "Показать ответ"
        self.btn_flip = ttk.Button(self.card_frame,
                                   text="Показать ответ",
                                   command=self.flip_card)
        self.btn_flip.pack(pady=20)

        # Контейнер для ответа и кнопок (изначально скрыт)
        self.answer_container = ttk.Frame(self.card_frame)

        ttk.Label(self.answer_container,
                  text="Ответ:",
                  font=("Helvetica", 10, "bold")
                  ).pack(anchor="w")
        self.answer_label = ttk.Label(self.answer_container,
                                      text="",
                                      wraplength=500,
                                      font=("Helvetica", 12))
        self.answer_label.pack(anchor="w", pady=5)

        ttk.Separator(self.answer_container,
                      orient='horizontal'
                      ).pack(fill='x', pady=15)

        # Кнопки выбора интервала
        btn_grid = ttk.Frame(self.answer_container)
        btn_grid.pack()

        ttk.Button(btn_grid, text="Сегодня (0 дн)",
                   command=lambda: self.rate_card(0)
                   ).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(btn_grid, text="Через 1 день",
                   command=lambda: self.rate_card(1)
                   ).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(btn_grid, text="Через 3 дня",
                   command=lambda: self.rate_card(3)
                   ).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(btn_grid, text="Через 7 дней",
                   command=lambda: self.rate_card(7)
                   ).grid(row=1, column=1, padx=5, pady=5)

        # Прогресс
        self.progress_label = ttk.Label(self.main_container, text="")
        self.progress_label.pack(pady=5)

    def flip_card(self):
        """Переворачивает карточку (показывает ответ)"""
        # отключаем кнопку "Показать ответ"
        self.btn_flip.config(state="disabled")
        # показываем контейнер с ответом и кнопками
        self.answer_container.pack(fill=tk.BOTH, expand=True, pady=10)

    def rate_card(self, interval):
        """Обрабатывает выбор интервала повторения"""
        # Сохраняем результат повторения в БД
        self.db.update_review(self.current_card_id, interval)

        # Удаляем текущую карточку из очереди
        self.cards_queue.pop(0)

        # Показываем следующую карточку (если есть)
        self.show_next_card()

    def show_next_card(self):
        """Отображает следующую карточку из очереди"""
        if not self.cards_queue:
            messagebox.showinfo("Сессия окончена",
                                "Вы повторили все карточки на сегодня!")
            self.show_deck_list()
            return

        # Берём первую карточку из очереди
        card = self.cards_queue[0]
        self.current_card_id = card[0]
        question_text = card[1]
        answer_text = card[2]

        # Обновляем виджеты
        self.question_label.config(text=question_text)
        self.answer_label.config(text=answer_text)
        self.progress_label.config(text=f"Осталось: {len(self.cards_queue)}")

        # Загружаем и отображаем историю повторений
        history = self.db.get_card_history(self.current_card_id)
        if history:
            from utils import format_relative_date
            history_lines = [format_relative_date(d) for d in history]
            history_text = "Последние повторения:\n" + "\n".join(history_lines)
            self.history_label.config(text=history_text)
        else:
            self.history_label.config(text="История повторений:\n(Нет данных)")

        # Сбрасываем состояние: скрываем контейнер с ответом, активируем кнопку переворота
        self.answer_container.pack_forget()
        self.btn_flip.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardsApp(root)
    root.mainloop()
