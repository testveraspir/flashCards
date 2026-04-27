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

    def get_all_cards_count(self, deck_id):
        """Возвращает общее количество карточек в колоде"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cards WHERE deck_id = ?", (deck_id,))
        return cursor.fetchone()[0]

    def get_current_interval(self, card_id):
        """Возвращает текущий интервал карточки в днях"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT last_review_date, next_review_date 
            FROM cards WHERE id = ?
        """, (card_id,))
        row = cursor.fetchone()

        if not row or not row[0] or not row[1]:
            return 0  # новая карточка

        # Если дата слишком далёкая — считаем карточку выученной
        next_date_str = row[1]
        if next_date_str >= "2999-01-01":
            return 7  # последний интервал, дальше не увеличиваем

        last_date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
        next_date = datetime.datetime.strptime(row[1], "%Y-%m-%d").date()

        return (next_date - last_date).days

    def update_review_auto(self, card_id):
        """Автоматически обновляет интервал: 0→1→3→7→выучена"""
        cursor = self.conn.cursor()
        today = datetime.date.today()
        today_str = today.isoformat()

        # Получаем текущий интервал
        current_interval = self.get_current_interval(card_id)

        # Определяем следующий интервал
        if current_interval == 0:
            new_interval = 1
        elif current_interval == 1:
            new_interval = 3
        elif current_interval == 3:
            new_interval = 7
        else:
            new_interval = None  # выучена

        if new_interval:
            next_date = today + datetime.timedelta(days=new_interval)
            next_date_str = next_date.isoformat()
        else:
            # Выучена - ставим дату далеко в будущее
            next_date_str = "2999-12-31"

        # Обновляем карточку
        cursor.execute("""
            UPDATE cards 
            SET next_review_date = ?, last_review_date = ? 
            WHERE id = ?
        """, (next_date_str, today_str, card_id))

        self.conn.commit()
        return new_interval is not None  # True если не выучена

    def close(self):
        self.conn.close()
