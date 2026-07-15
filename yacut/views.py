from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import MainPageForm, UploadForm
from .models import URLMap
from .utils import get_unique_short_id
from .yandex_disk import async_upload_files_to_disk


@app.route('/', methods=['GET', 'POST'])
def main_page_view():
    form = MainPageForm()
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        if custom_id:
            if custom_id == 'files' or URLMap.query.filter_by(
                short=custom_id
            ).first() is not None:
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('index.html', form=form)
            short = custom_id
        else:
            short = get_unique_short_id()
        url_map = URLMap(original=form.original_link.data, short=short)
        db.session.add(url_map)
        db.session.commit()
        short_link = url_for('redirect_view', short_id=short, _external=True)
        return render_template('index.html', form=form, short_link=short_link)
    return render_template('index.html', form=form)


@app.route('/<short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    response = redirect(url_map.original)
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = UploadForm()
    if form.validate_on_submit():
        files = form.files.data
        urls = await async_upload_files_to_disk(files)
        uploaded_files = []
        for file, original in zip(files, urls):
            short = get_unique_short_id()
            url_map = URLMap(original=original, short=short)
            db.session.add(url_map)
            short_link = url_for(
                'redirect_view', short_id=short, _external=True
            )
            uploaded_files.append((file.filename, short_link))
        db.session.commit()
        return render_template(
            'files.html', form=form, uploaded_files=uploaded_files
        )
    return render_template('files.html', form=form)
