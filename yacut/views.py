from flask import flash, redirect, render_template, url_for

from . import app
from .forms import MainPageForm, UploadForm
from .models import ShortIdValidationError, URLMap
from .yandex_disk import async_upload_files_to_disk


@app.route('/', methods=['GET', 'POST'])
def main_page_view():
    form = MainPageForm()
    if form.validate_on_submit():
        try:
            url_map = URLMap.create(
                original=form.original_link.data,
                custom_id=form.custom_id.data,
            )
        except ShortIdValidationError as error:
            flash(str(error))
            return render_template('index.html', form=form)
        short_link = url_for(
            'redirect_view', short_id=url_map.short, _external=True
        )
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
            url_map = URLMap.create(original=original)
            short_link = url_for(
                'redirect_view', short_id=url_map.short, _external=True
            )
            uploaded_files.append((file.filename, short_link))
        return render_template(
            'files.html', form=form, uploaded_files=uploaded_files
        )
    return render_template('files.html', form=form)
