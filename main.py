import tkinter as tk
from tkinter import ttk
from database import DatabaseManager
from views.deck_list_view import DeckListView
from views.deck_menu_view import DeckMenuView
from views.review_view import ReviewView


class FlashcardsApp:
    def __init__(self, root):
        # Настраиваем окно
        self.root = root
        self.root.title("Интервальное повторение")
        self.root.geometry("600x500")
        self.root.minsize(400, 300)
        # Создаем объект DatabaseManager
        self.db = DatabaseManager()

        self.deck_list_view = None
        self.current_deck_name = None
        self.current_deck_id = None
        self.deck_menu_view = None
        self.review_view = None

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
        self.clear_frame()
        self.review_view = ReviewView(
            self.main_container,
            self.db,
            self.current_deck_id,
            on_finish=self.show_deck_menu
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardsApp(root)
    root.mainloop()
