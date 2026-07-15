from http import HTTPStatus
import re

from flask import jsonify, request, url_for

from . import app, db
from .constants import CUSTOM_ID_MAX_LENGTH
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .utils import get_unique_short_id

CUSTOM_ID_PATTERN = re.compile(r'^[A-Za-z0-9]*$')


def validate_custom_id(custom_id):
    if (
        len(custom_id) > CUSTOM_ID_MAX_LENGTH
        or not CUSTOM_ID_PATTERN.fullmatch(custom_id)
    ):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )


@app.route('/api/id/', methods=['POST'])
def create_id_view():
    data = request.get_json()
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    custom_id = data.get('custom_id')
    if custom_id:
        validate_custom_id(custom_id)
        if custom_id == 'files' or URLMap.query.filter_by(
            short=custom_id
        ).first() is not None:
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        short = custom_id
    else:
        short = get_unique_short_id()
    url_map = URLMap(original=data['url'], short=short)
    db.session.add(url_map)
    db.session.commit()
    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_view', short_id=short, _external=True
        )
    }), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
