import re
from datetime import datetime

from . import db
from .constants import (
    CUSTOM_ID_MAX_LENGTH, CUSTOM_ID_PATTERN, SHORT_LINK_LENGTH
)

CUSTOM_ID_RE = re.compile(CUSTOM_ID_PATTERN)


class ShortIdValidationError(Exception):
    """Предложенный вариант короткой ссылки нельзя использовать."""


class URLMap(db.Model):
    """Соответствие короткого идентификатора оригинальной длинной ссылке."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(
        db.String(SHORT_LINK_LENGTH), nullable=False, unique=True
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @staticmethod
    def create(original, custom_id=None):
        """Провалидировать/сгенерировать short, сохранить и вернуть объект."""
        from .utils import get_unique_short_id

        if custom_id:
            if (
                len(custom_id) > CUSTOM_ID_MAX_LENGTH
                or not CUSTOM_ID_RE.fullmatch(custom_id)
            ):
                raise ShortIdValidationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
            if custom_id == 'files' or URLMap.query.filter_by(
                short=custom_id
            ).first() is not None:
                raise ShortIdValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            short = custom_id
        else:
            short = get_unique_short_id()
        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()
        return url_map