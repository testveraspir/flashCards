import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext


class ReviewView:
    """Экран режима повторения"""

    def __init__(self, parent, db, deck_id, on_finish):
        """
        :param parent: контейнер, в котором размещается экран (Frame)
        :param db: объект DatabaseManager
        :param deck_id: ID выбранной колоды
        :param on_finish: callback для возврата в меню колоды
         после завершения сессии
        """

        self.parent = parent
        self.db = db
        self.deck_id = deck_id
        self.on_finish = on_finish

        self.cards_queue = []
        self.current_card_id = None

        # Виджеты
        self.card_frame = None
        self.question_label = None
        self.btn_flip = None
        self.answer_container = None
        self.answer_label = None
        self.progress_label = None

        self.create_widgets()
        self.start_session()

    def create_widgets(self):
        """Создаёт интерфейс для режима повторения"""
        # Верхняя панель (кнопка "Прервать")
        top_frame = ttk.Frame(self.parent)
        top_frame.pack(fill=tk.X, pady=5)
        ttk.Button(top_frame,
                   text="Прервать",
                   bootstyle=PRIMARY + OUTLINE,
                   command=self.interrupt
                   ).pack(side=tk.RIGHT)

        # Основная область карточки
        self.card_frame = ttk.Frame(self.parent,
                                    borderwidth=2,
                                    relief="groove",
                                    padding=20)
        self.card_frame.pack(fill=tk.BOTH,
                             expand=True, padx=20, pady=10)

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
                                   bootstyle=PRIMARY + OUTLINE,
                                   command=self.flip_card)
        self.btn_flip.pack(pady=20)

        # Контейнер для ответа и кнопок (изначально скрыт)
        self.answer_container = ttk.Frame(self.card_frame)

        ttk.Label(self.answer_container,
                  text="Ответ:",
                  font=("Helvetica", 10, "bold")
                  ).pack(anchor="w")
        self.answer_label = scrolledtext.ScrolledText(self.answer_container,
                                                      wrap=tk.WORD,
                                                      font=("Helvetica", 12),
                                                      height=5,
                                                      relief=tk.FLAT)
        self.answer_label.pack(fill=tk.BOTH, expand=True, pady=5)
        self.answer_label.config(state=tk.DISABLED)  # только для чтения

        ttk.Separator(self.answer_container,
                      orient='horizontal'
                      ).pack(fill='x', pady=15)

        # Кнопки выбора интервала
        btn_grid = ttk.Frame(self.answer_container)
        btn_grid.pack()

        ttk.Button(btn_grid, text="Сегодня", bootstyle=PRIMARY+OUTLINE,
                   command=lambda: self.rate_card(0)
                   ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_grid, text="Через 1 день", bootstyle=PRIMARY+OUTLINE,
                   command=lambda: self.rate_card(1)
                   ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_grid, text="Через 3 дня", bootstyle=PRIMARY+OUTLINE,
                   command=lambda: self.rate_card(3)
                   ).grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_grid, text="Через 7 дней", bootstyle=PRIMARY+OUTLINE,
                   command=lambda: self.rate_card(7)
                   ).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Прогресс
        self.progress_label = ttk.Label(self.parent, text="")
        self.progress_label.pack(pady=5)

    def start_session(self):
        """Начинает сессию повторения"""
        # Проверяем, есть ли вообще карточки в колоде
        all_cards = self.db.get_all_cards_count(self.deck_id)
        self.cards_queue = self.db.get_due_cards(self.deck_id)

        if all_cards == 0:
            messagebox.showinfo("Информация",
                                "В этой колоде ещё нет карточек."
                                "\nДобавьте карточки через меню колоды.")
            return

        if not self.cards_queue:
            messagebox.showinfo("Информация",
                                "На сегодня все карточки изучены!")
            return

        self.show_next_card()

    def show_next_card(self):
        """Отображает следующую карточку из очереди"""
        if not self.cards_queue:
            messagebox.showinfo("Сессия окончена",
                                "Вы повторили все карточки на сегодня!")
            self.on_finish()
            return

        # Берём первую карточку из очереди
        card = self.cards_queue[0]
        self.current_card_id = card[0]
        question_text = card[1]
        answer_text = card[2]

        # Обновляем виджеты
        self.question_label.config(text=question_text)
        self.answer_label.config(state=tk.NORMAL)
        self.answer_label.delete("1.0", tk.END)
        self.answer_label.insert("1.0", answer_text)
        self.answer_label.config(state=tk.DISABLED)
        self.progress_label.config(text=f"Осталось: {len(self.cards_queue)}")

        # Сбрасываем состояние: скрываем контейнер с ответом, активируем кнопку переворота
        self.answer_container.pack_forget()
        self.btn_flip.pack()

    def flip_card(self):
        """Переворачивает карточку (показывает ответ)"""
        # отключаем кнопку "Показать ответ"
        self.btn_flip.pack_forget()
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

    def interrupt(self):
        """Прерывает сессию повторения"""
        if messagebox.askyesno("Прервать",
                               "Вы уверены? Прогресс текущей карточки будет потерян."):
            self.on_finish()
