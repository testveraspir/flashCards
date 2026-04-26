import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class DeckListView:
    """"Экран со списком всех колод"""

    def __init__(self, parent, db, on_deck_selected):
        """
        :param parent: контейнер, в котором размещается экран (Frame)
        :param db: объект DatabaseManager
        :param on_deck_selected: callback,
        вызываемый при выборе колоды (принимает deck_id, deck_name)
        """

        self.parent = parent
        self.db = db
        self.on_deck_selected = on_deck_selected
        self.deck_listbox = None
        self.deck_ids = []

        self.create_widgets()
        self.refresh_deck_list()

    def create_widgets(self):
        """Отображает список колод"""
        # Заголовок
        ttk.Label(self.parent,
                  text="Мои колоды",
                  font=("Helvetica", 14, "bold")
                  ).pack(pady=10)
        # Рамка для списка
        list_frame = ttk.Frame(self.parent)
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
        btn_frame = ttk.Frame(self.parent)
        btn_frame.pack(pady=10, fill=tk.X)

        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        ttk.Button(btn_frame,
                   text="Создать колоду",
                   command=self.create_deck_dialog
                   ).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_frame,
                   text="Удалить колоду",
                   command=self.delete_deck
                   ).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        ttk.Button(btn_frame,
                   text="Выбрать колоду",
                   command=self.select_deck
                   ).grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        ttk.Button(btn_frame,
                   text="Выход",
                   command=self.on_exit
                   ).grid(row=1, column=1, padx=2, pady=2, sticky="ew")

    def refresh_deck_list(self):
        """Обновляет список колод из базы данных"""
        self.deck_listbox.delete(0, tk.END)
        decks = self.db.get_decks()
        for deck_id, name in decks:
            self.deck_listbox.insert(tk.END, name)
            self.deck_ids.append(deck_id)

    def create_deck_dialog(self):
        """Диалог создания новой колоды"""
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

    def delete_deck(self):
        """Удаляет выбранную колоду"""
        selection = self.deck_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание",
                                   "Выберите колоду для удаления")
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
        deck_id = self.deck_ids[index]
        deck_name = self.deck_listbox.get(index)
        self.on_deck_selected(deck_id, deck_name)

    def on_exit(self):
        """Выход из приложения"""
        if messagebox.askyesno("Выход",
                               "Вы уверены, что хотите выйти?"):
            self.parent.winfo_toplevel().destroy()
