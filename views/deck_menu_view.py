import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import datetime


class DeckMenuView:
    """Экран со списком всех карточек колоды и их статусами"""

    def __init__(self, parent, deck_id, deck_name,
                 db, on_back, on_add_card, on_start_review):
        """
        :param parent: контейнер, в котором размещается экран (Frame)
        :param deck_id: ID выбранной колоды
        :param deck_name: название колоды
        :param db: объект DatabaseManager
        :param on_back: callback для возврата к списку колод
        :param on_add_card: callback для открытия
         диалога добавления карточки
        :param on_start_review: callback для начала повторения
        """

        self.parent = parent
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.db = db
        self.on_back = on_back
        self.on_add_card = on_add_card
        self.on_start_review = on_start_review
        self.tree = None

        self.create_widgets()
        self.refresh_card_list()

    def create_widgets(self):
        """Отображает меню выбранной колоды"""
        # Верхняя панель: название колоды и кнопка "Назад"
        header_frame = ttk.Frame(self.parent)
        header_frame.pack(fill=tk.X, pady=5)
        ttk.Label(header_frame,
                  text=f"Колода: {self.deck_name}",
                  font=("Helvetica", 14, "bold")).pack(
            side=tk.LEFT)
        ttk.Button(header_frame,
                   text="Назад",
                   bootstyle=PRIMARY + OUTLINE,
                   command=self.on_back,
                   ).pack(side=tk.RIGHT)

        # Рамка для списка карточек
        list_frame = ttk.Frame(self.parent)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Таблица с колонками
        columns = ("question", "next_review")
        self.tree = ttk.Treeview(list_frame,
                                 columns=columns,
                                 show="headings",
                                 height=15)
        self.tree.heading("question", text="Вопрос")
        self.tree.heading("next_review", text="Дата повтора")
        self.tree.column("question", width=350, anchor="w", minwidth=200)
        self.tree.column("next_review", width=120, anchor="center", minwidth=100)

        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки внизу
        actions_frame = ttk.Frame(self.parent)
        actions_frame.pack(pady=10, fill=tk.X)
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)

        ttk.Button(actions_frame,
                   text="Добавить карточку",
                   width=20,
                   command=self.on_add_card,
                   bootstyle=SUCCESS+OUTLINE
                   ).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame,
                   text="Начать повторение",
                   width=20,
                   command=self.on_start_review,
                   bootstyle=PRIMARY+OUTLINE
                   ).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame,
                   text="В повтор (для выбранной)",
                   command=self.add_selected_to_review,
                   bootstyle=WARNING+OUTLINE
                   ).pack(side=tk.LEFT, padx=5)

    def get_card_status(self, next_review_date):
        """Возвращает дату следующего повторения в формате ДД.ММ.ГГ"""
        if not next_review_date:
            return "сегодня"

        # Если карточка выучена
        if next_review_date >= "2999-01-01":
            return "выучена"

        # Преобразуем дату в формат ДД.ММ.ГГ
        date_obj = datetime.datetime.strptime(next_review_date, "%Y-%m-%d").date()
        return date_obj.strftime("%d.%m.%y")

    def refresh_card_list(self):
        """Обновляет список карточек из базы данных"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        cards = self.db.get_all_cards(self.deck_id)

        for i, card in enumerate(cards):
            card_id, question, next_review_date = card
            status = self.get_card_status(next_review_date)
            # Вставляем строку
            self.tree.insert("", tk.END, values=(question, status),
                             iid=str(card_id))


    def add_selected_to_review(self):
        """Добавляет выбранную карточку в повтор"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите карточку")
            return

        card_id = int(selected[0])

        # Проверяем, выучена ли карточка
        cards = self.db.get_all_cards(self.deck_id)
        for card in cards:
            if card[0] == card_id and card[2] >= "2999-01-01":
                self.db.reset_card(card_id)
                self.refresh_card_list()
                messagebox.showinfo("Успех", "Карточка добавлена в повтор")
                return

        messagebox.showinfo("Инфо",
                            "Можно добавлять в повтор только выученные карточки")
