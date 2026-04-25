import sqlite3
from utils import DB_NAME


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Таблица колод
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        # Таблица карточек
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                next_review_date TEXT,
                FOREIGN KEY(deck_id) REFERENCES decks(id)
                    ON DELETE CASCADE
            )
        ''')
        # Таблица истории повторений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER,
                review_date TEXT,
                FOREIGN KEY(card_id) REFERENCES cards(id)
                    ON DELETE CASCADE
                )
        ''')
        self.conn.commit()

    def add_deck(self, name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO decks (name) VALUES (?)", (name,))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Колода с таким именем уже существует

    def get_decks(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, name FROM decks")
        return cursor.fetchall()

    def delete_deck(self, deck_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
