import datetime


DB_NAME = "flashcards.db"


def get_today_str():
    """Возвращает сегодняшнюю дату в формате YYYY-MM-DD"""

    return datetime.date.today().isoformat()
