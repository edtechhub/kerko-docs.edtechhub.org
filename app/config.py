import logging
import pathlib

from environs import Env
from flask_babelex import lazy_gettext as _

from kerko.composer import Composer

env = Env()  # pylint: disable=invalid-name


class Config():
    app_dir = pathlib.Path(env.str('FLASK_APP')).parent.absolute()

    # Get secret configuration values from the environment.
    SECRET_KEY = env.str('SECRET_KEY')
    KERKO_ZOTERO_API_KEY = env.str('KERKO_ZOTERO_API_KEY')
    KERKO_ZOTERO_LIBRARY_ID = env.str('KERKO_ZOTERO_LIBRARY_ID')
    KERKO_ZOTERO_LIBRARY_TYPE = env.str('KERKO_ZOTERO_LIBRARY_TYPE')

    # Set other configuration variables.
    LOGGING_HANDLER = 'default'
    EXPLAIN_TEMPLATE_LOADING = False

    BABEL_DEFAULT_LOCALE = 'en'
    KERKO_WHOOSH_LANGUAGE = 'en'
    KERKO_ZOTERO_LOCALE = 'en-GB'

    HOME_URL = 'https://edtechhub.org/'
    HOME_TITLE = _("The EdTech Hub")
    HOME_SUBTITLE = _("Research and Innovation to fulfil the potential of EdTech")
    NAV_TITLE = _("Evidence Library")
    KERKO_TITLE = _("Evidence Library – The EdTech Hub")
    KERKO_CSL_STYLE = 'apa'
    KERKO_PRINT_ITEM_LINK = True
    KERKO_PRINT_CITATIONS_LINK = True
    KERKO_TEMPLATE_BASE = 'app/base.html.jinja2'
    KERKO_TEMPLATE_LAYOUT = 'app/layout.html.jinja2'
    KERKO_TEMPLATE_SEARCH = 'app/search.html.jinja2'
    KERKO_TEMPLATE_SEARCH_ITEM = 'app/search-item.html.jinja2'
    KERKO_TEMPLATE_ITEM = 'app/item.html.jinja2'

    KERKO_COMPOSER = Composer(
        whoosh_language=KERKO_WHOOSH_LANGUAGE,
    )

    LIBSASS_INCLUDES = [
        str(pathlib.Path(__file__).parent / 'static' / 'src' / 'vendor' / 'bootstrap' / 'scss'),
        str(pathlib.Path(__file__).parent / 'static' / 'src' / 'vendor' / '@fortawesome' / 'fontawesome-free' / 'scss'),
    ]


class DevelopmentConfig(Config):
    CONFIG = 'development'
    DEBUG = True
    ASSETS_DEBUG = env.bool('KERKO_ASSETS_DEBUG', True)  # Don't bundle/minify static assets.
    KERKO_ZOTERO_START = env.int('KERKO_ZOTERO_START', 0)
    KERKO_ZOTERO_END = env.int('KERKO_ZOTERO_END', 0)
    LIBSASS_STYLE = 'expanded'


class ProductionConfig(Config):
    CONFIG = 'production'
    DEBUG = False
    ASSETS_DEBUG = env.bool('KERKO_ASSETS_DEBUG', False)
    ASSETS_AUTO_BUILD = False
    LOGGING_HANDLER = 'syslog'
    LOGGING_ADDRESS = '/dev/log'
    LOGGING_LEVEL = logging.WARNING
    LOGGING_FORMAT = '%(name)s %(asctime)s %(levelname)s: %(message)s'
    GOOGLE_ANALYTICS_ID = 'UA-149862882-2'
    LIBSASS_STYLE = 'compressed'


CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
