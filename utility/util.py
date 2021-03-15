from datetime import datetime


DATE_FORMAT = '%d.%m.%Y %H:%M:%S'
DATE_FORMAT_1C = '%Y%m%d%H%M%S'
DATE_FORMAT_SQL = '%Y-%m-%d %H:%M:%S'


def return_date_str(date):
    if value_filled(date):
        return datetime.strftime(date, DATE_FORMAT)
    else:
        return ""

def date_setter(date):
    if isinstance(date, datetime):
        return date
    elif date is None:
        return None
    else:
        try:
            return datetime.strptime(date, DATE_FORMAT)
        except ValueError:
            try:
                return datetime.strptime(date, DATE_FORMAT_SQL)
            except:
                raise ValueError(
                    f'date_setter: неверный формат даты. Получена дата формата {date}, тогда как ожидается {DATE_FORMAT}')

def value_filled(val):
    if isinstance(val, datetime):
        return val != datetime(1, 1, 1, 0, 0, 0)
    elif isinstance(val, str):
        return val != ""
    elif isinstance(val, int) or isinstance(val, float):
        return val != 0
    else:
        False