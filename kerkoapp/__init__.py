"""
An application inspired by KerkoApp.
"""

import os
import pathlib

import kerko
from flask import Flask, current_app, g, redirect, render_template, request
from flask_babel import get_locale
from kerko import blueprint as kerko_blueprint
from kerko.config_helpers import (ConfigModel, KerkoModel, config_update,
                                  load_toml, parse_config)

from . import logging
from .assets import assets
from .config import DevelopmentConfig, ProductionConfig, update_composer
from .config_helpers import KerkoAppModel, load_config_files
from .extensions import babel, bootstrap


def create_app() -> Flask:
    """
    Application factory.

    Explained here: http://flask.pocoo.org/docs/patterns/appfactories/
    """
    try:
        app = Flask(
            __name__,
            instance_path=os.environ.get('KERKOAPP_INSTANCE_PATH'),
            static_folder='../static',
        )
    except ValueError as e:
        raise RuntimeError(f"Unable to initialize the application. {e}") from e

    # Initialize app configuration with Kerko's defaults.
    config_update(app.config, kerko.DEFAULTS)

    # Update app configuration from TOML configuration file(s).
    load_config_files(app, os.environ.get('KERKOAPP_CONFIG_FILES'))

    # Update app configuration from environment variables.
    app.config.from_prefixed_env(prefix='KERKOAPP')

    # Update app configuration from objects.
    if app.config['DEBUG']:
        app.config.from_object(DevelopmentConfig())
    else:
        app.config.from_object(ProductionConfig())

    # Validate configuration and save its parsed version.
    parse_config(app.config)

    # Validate extra configuration model and save its parsed version.
    if app.config.get('kerkoapp'):
        parse_config(app.config, 'kerkoapp', KerkoAppModel)

    # Initialize the Composer object.
    app.config['kerko_composer'] = kerko.composer.Composer(app.config)

    # Update the Composer object.
    update_composer(app.config['kerko_composer'])

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)

    return app


def register_extensions(app):
    # Configure Babel to use both Kerko's translations and the app's.
    translation_directories = ';'.join(kerko.TRANSLATION_DIRECTORIES + ['translations'])
    babel.init_app(
        app,
        default_domain=kerko.TRANSLATION_DOMAIN,
        default_translation_directories=translation_directories,
    )

    assets.init_app(app)
    logging.init_app(app)
    bootstrap.init_app(app)


def register_blueprints(app):
    # Setting `url_prefix` is required to distinguish the blueprint's static
    # folder route URL from the app's.
    app.register_blueprint(kerko_blueprint, url_prefix='/lib')


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500.
        error_code = getattr(error, 'code', 500)
        context = {
            'locale': get_locale(),
        }
        return render_template(f'kerkoapp/{error_code}.html.jinja2', **context), error_code

    for errcode in [400, 403, 404, 500, 503]:
        app.errorhandler(errcode)(render_error)
