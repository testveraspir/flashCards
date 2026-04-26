import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class DeckMenuView:
    """Экран меню выбранной колоды"""

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

        self.create_widgets()

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

        # Центральные кнопки действий
        actions_frame = ttk.Frame(self.parent)
        actions_frame.pack(expand=True)

        ttk.Button(actions_frame,
                   text="Добавить карточку",
                   width=20,
                   command=self.on_add_card,
                   bootstyle=SUCCESS+OUTLINE
                   ).pack(pady=15)
        ttk.Button(actions_frame,
                   text="Начать повторение",
                   width=20,
                   command=self.on_start_review,
                   bootstyle=PRIMARY+OUTLINE
                   ).pack(pady=8)
