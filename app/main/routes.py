from functools import wraps

from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm


def requires_session(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('name') or not session.get('team'):
            return redirect(url_for('.index') + '?must_log_in')
        return f(*args, **kwargs)

    return wrapped


@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()

    if form.validate_on_submit():
        session['name'] = form.name.data.capitalize()
        session['team'] = form.team.data
        return redirect(url_for('.game'))

    print(form.errors)
    return render_template('index.html', form=form)


@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main.route('/chat')
@requires_session
def game():
    return render_template('game.html')
