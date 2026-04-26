import tkinter as tk
from tkinter import ttk, messagebox
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
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.deck_listbox.yview)
        self.deck_listbox.configure(yscrollcommand=scrollbar.set)

        self.deck_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


if __name__ == "__main__":
    root = tk.Tk()
    app = FlashcardsApp(root)
    root.mainloop()




