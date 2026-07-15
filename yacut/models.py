from datetime import datetime

from . import db
from .constants import SHORT_LINK_LENGTH


class URLMap(db.Model):
    """Соответствие короткого идентификатора оригинальной длинной ссылке."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.Text, nullable=False)
    short = db.Column(
        db.String(SHORT_LINK_LENGTH), nullable=False, unique=True
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
