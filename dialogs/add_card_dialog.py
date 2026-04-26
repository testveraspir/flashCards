import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, scrolledtext


def show_add_card_dialog(parent, db, deck_id):
    """
    Показывает диалог добавления карточки.
    :param parent: Родительское окно (Tk или Toplevel)
    :param db: объект DatabaseManager
    :param deck_id: ID колоды, в которую добавляем карточку
    :return:
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Новая карточка")
    dialog.geometry("500x400")

    # Метка и поле для Вопроса
    ttk.Label(
        dialog,
        text="Вопрос:",
        font=("Helvetica", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 0))
    q_text = scrolledtext.ScrolledText(
        dialog,
        width=50,
        height=8,
        font=("Helvetic", 10)
    )
    q_text.pack(
        padx=10,
        pady=5,
        fill=tk.BOTH,
        expand=True
    )

    # Метка и поле для Ответа
    ttk.Label(
        dialog,
        text="Ответ:",
        font=("Helvetica", 10, "bold")
    ).pack(anchor="w", padx=10)
    a_text = scrolledtext.ScrolledText(
        dialog,
        width=50,
        height=8,
        font=("Helvetica", 10)
    )
    a_text.pack(
        padx=10,
        pady=5,
        fill=tk.BOTH,
        expand=True
    )

    # Кнопка сохранения
    def save_card():
        q = q_text.get("1.0", tk.END).strip()
        a = a_text.get("1.0", tk.END).strip()
        if not q or not a:
            messagebox.showerror("Ошибка",
                                 "Заполните оба поля: вопрос и ответ")
            return

        # Импорт get_today_str из utils
        from utils import get_today_str
        next_date = get_today_str()

        db.add_card(deck_id, q, a, next_date)
        messagebox.showinfo("Успех", "Карточка добавлена")
        dialog.destroy()

    ttk.Button(dialog,
               text="Сохранить",
               command=save_card,
               bootstyle=SUCCESS+OUTLINE
               ).pack(pady=10)
