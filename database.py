import sqlite3
from utils import DB_NAME, get_today_str


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

    def add_card(self, deck_id, question, answer, next_date):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cards (deck_id, question, answer, next_review_date)
            VALUES (?, ?, ?, ?)""", (deck_id, question, answer, next_date))
        self.conn.commit()

    def get_due_cards(self, deck_id):
        """
        Возвращает карточки к повторению
        :param deck_id:
        :return:
        """

        cursor = self.conn.cursor()
        today = get_today_str()
        cursor.execute("""
            SELECT id, question, answer, next_review_date
            FROM cards
            WHERE deck_id = ? AND next_review_date <= ?""",
                       (deck_id, today))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
