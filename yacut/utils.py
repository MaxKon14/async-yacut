import random
import string

from yacut.constants import AUTO_SHORT_ID_LENGTH
from yacut.models import URLMap

ALPHABET = string.ascii_letters + string.digits


def get_unique_short_id():
    """Сгенерировать случайный короткий ID, которого ещё нет в базе."""
    while True:
        short_id = ''.join(
            random.choices(ALPHABET, k=AUTO_SHORT_ID_LENGTH)
        )
        if URLMap.query.filter_by(short=short_id).first() is None:
            return short_id
