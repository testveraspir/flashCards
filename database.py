import sqlite3
import datetime
from utils import DB_NAME, get_today_str


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.execute("PRAGMA foreign_keys = ON")
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
                last_review_date TEXT,
                added_date TEXT,
                FOREIGN KEY(deck_id) REFERENCES decks(id)
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
        today = get_today_str()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO cards (deck_id, question, answer,
             next_review_date, last_review_date, added_date)
            VALUES (?, ?, ?, ?, ?, ?)""", (deck_id, question, answer,
                                           next_date, today, today))
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

    def get_card_history(self, card_id):
        """
        Возвращает последние 4 даты повторения для карточки
        :param card_id:
        :return:
        """

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT review_date FROM review_history
            WHERE card_id = ?
            ORDER BY review_date DESC LIMIT 4
        """, (card_id,))
        return [row[0] for row in cursor.fetchall()]

    def update_review(self, card_id, interval_days):
        cursor = self.conn.cursor()
        today = datetime.date.today()
        # Вычисляем дату следующего повторения
        if interval_days == 0:
            next_date = today
        else:
            next_date = today + datetime.timedelta(days=interval_days)

        next_date_str = next_date.isoformat()
        today_str = today.isoformat()
        # Обновляем карточку
        cursor.execute("""
            UPDATE cards 
            SET next_review_date = ?, last_review_date = ?
            WHERE id = ?
        """, (next_date_str, today_str, card_id)
        )
        self.conn.commit()

    def get_all_cards_count(self, deck_id):
        """Возвращает общее количество карточек в колоде"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards WHERE deck_id = ?", (deck_id,))
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()
