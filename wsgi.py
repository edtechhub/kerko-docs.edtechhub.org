from environs import Env
from flask import redirect, url_for

from app import create_app

env = Env()
env.read_env()

application = create_app(env.str('FLASK_ENV'))


@application.route('/')
def home():
    return redirect(url_for('kerko.search'))


@application.shell_context_processor
def make_shell_context():
    """Return context dict for a shell session, giving access to variables."""
    return dict(application=application)
