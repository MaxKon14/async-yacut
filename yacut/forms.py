from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from .constants import CUSTOM_ID_MAX_LENGTH


class MainPageForm(FlaskForm):
    """Форма главной страницы: длинная ссылка и опциональный короткий ID."""

    original_link = URLField(
        'Введите длинную ссылку',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Введите вариант короткой ссылки',
        validators=[
            Optional(),
            Length(max=CUSTOM_ID_MAX_LENGTH,
                   message='Указано недопустимо большое количество символов'),
            Regexp(r'^[A-Za-z0-9]*$',
                   message='Допустимы только латинские буквы и цифры')
        ]
    )
    submit = SubmitField('Добавить')


class UploadForm(FlaskForm):
    """Форма страницы /files: загрузка нескольких файлов на Яндекс Диск."""

    files = MultipleFileField(
        'Выберите файлы для загрузки',
        validators=[FileRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Загрузить')
