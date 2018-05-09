from functools import wraps

from flask import session, redirect, url_for, render_template, request, jsonify

from app.main.state import CONNECTED_CLIENTS, CHATS
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

    valid = form.validate_on_submit()
    name = valid and form.name.data.strip().capitalize()
    already_registered = valid and name in CONNECTED_CLIENTS

    if valid and not already_registered:
        session['name'] = name
        session['team'] = form.team.data
        return redirect(url_for('.game'))

    return render_template('index.html', form=form, already_registered=already_registered)


@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@main.route('/history')
def history():
    return jsonify(CHATS)


@main.route('/chat')
@requires_session
def game():
    return render_template('game.html')
