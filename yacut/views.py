from flask import flash, redirect, render_template, url_for

from . import app, db
from .forms import MainPageForm
from .models import URLMap
from .utils import get_unique_short_id


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
    return redirect(url_map.original)
