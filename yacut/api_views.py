from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app
from .error_handlers import InvalidAPIUsage
from .models import ShortIdValidationError, URLMap


@app.route('/api/id/', methods=['POST'])
def create_id_view():
    data = request.get_json()
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    try:
        url_map = URLMap.create(
            original=data['url'], custom_id=data.get('custom_id')
        )
    except ShortIdValidationError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_view', short_id=url_map.short, _external=True
        )
    }), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_url_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
