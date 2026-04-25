import datetime


def get_today_str():
    """Возвращает сегодняшнюю дату в формате YYYY-MM-DD"""

    return datetime.date.today().isoformat()


def format_relative_date(date_str):
    """
    Преобразует дату строки YYYY-MM-DD
    в относительный формат 'дней назад'
    :param date_str:
    :return:
    """

    if not date_str:
        return ""

    try:
        review_date = datetime.datetime.strptime(
            date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        delta = today - review_date
        days = delta.days

        if days == 0:
            return "сегодня"
        elif days == 1:
            return "вчера"
        elif days < 7:
            return f"{days} дн. назад"
        elif days < 14:
            return "1 нед. назад"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} нед. назад"
        elif days < 365:
            months = days // 30
            return f"{months} мес. назад"
        else:
            years = days // 365
            return f"{years} г. назад"
    except ValueError:
        return date_str
