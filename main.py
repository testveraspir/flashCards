import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from database import DatabaseManager
from views.deck_list_view import DeckListView
from views.deck_menu_view import DeckMenuView


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
        self.cards_queue = []
        self.card_frame = None
        self.progress_label = None
        self.answer_label = None
        self.answer_container = None
        self.btn_flip = None
        self.question_label = None
        self.history_label = None
        self.current_card_id = None
        self.deck_list_view = None
        self.current_deck_name = None
        self.current_deck_id = None
        self.deck_menu_view = None

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
        """Отображает экран списка колод"""
        self.clear_frame()
        # Создаём экран, передаём callback для выбора колоды
        self.deck_list_view = DeckListView(
            self.main_container,
            self.db,
            self.on_deck_selected
        )

    def on_deck_selected(self, deck_id, deck_name):
        """Обработчик выбора колоды из списка"""
        self.current_deck_id = deck_id
        self.current_deck_name = deck_name
        self.show_deck_menu()

    def show_deck_menu(self):
        """Отображает экран меню колоды"""
        self.clear_frame()
        self.deck_menu_view = DeckMenuView(
            self.main_container,
            self.current_deck_id,
            self.current_deck_name,
            self.db,
            on_back=self.show_deck_list,
            on_add_card=self.add_card_dialog,
            on_start_review=self.start_review_session
        )

    def add_card_dialog(self):
        from dialogs.add_card_dialog import show_add_card_dialog
        show_add_card_dialog(self.root, self.db, self.current_deck_id)

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
