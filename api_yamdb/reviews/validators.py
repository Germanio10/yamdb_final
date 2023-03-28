import datetime as dt

from django.core import exceptions


def validate_year(value):
    now_year = dt.datetime.now().year
    if value > now_year:
        raise exceptions.ValidationError(
            f'Значение года ({value})'
            f' не может быть больше текущего ({now_year})'
        )
    return value
