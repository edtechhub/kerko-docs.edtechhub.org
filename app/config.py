import logging
import pathlib

from environs import Env
from flask_babelex import gettext as _
from whoosh.fields import BOOLEAN
from whoosh.query import Term

from kerko.codecs import BooleanFacetCodec
from kerko.composer import Composer
from kerko.extractors import InCollectionExtractor
from kerko.renderers import TemplateStringRenderer
from kerko.specs import BadgeSpec, CollectionFacetSpec, FieldSpec, FlatFacetSpec

env = Env()  # pylint: disable=invalid-name
env.read_env()


class Config():
    app_dir = pathlib.Path(env.str('FLASK_APP')).parent.absolute()

    # Get configuration values from the environment.
    SECRET_KEY = env.str('SECRET_KEY')
    KERKO_ZOTERO_API_KEY = env.str('KERKO_ZOTERO_API_KEY')
    KERKO_ZOTERO_LIBRARY_ID = env.str('KERKO_ZOTERO_LIBRARY_ID')
    KERKO_ZOTERO_LIBRARY_TYPE = env.str('KERKO_ZOTERO_LIBRARY_TYPE')
    KERKO_DATA_DIR = env.str('KERKO_DATA_DIR', str(app_dir / 'data' / 'kerko'))

    # Set other configuration variables.
    LOGGING_HANDLER = 'default'
    EXPLAIN_TEMPLATE_LOADING = False

    LIBSASS_INCLUDES = [
        str(pathlib.Path(__file__).parent.parent / 'static' / 'src' / 'vendor' / 'bootstrap' / 'scss'),
        str(pathlib.Path(__file__).parent.parent / 'static' / 'src' / 'vendor' / '@fortawesome' / 'fontawesome-free' / 'scss'),
    ]

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
        exclude_default_facets=['facet_tag', 'facet_link'],
        default_child_whitelist_re='^publishPDF$',
        default_child_blacklist_re='',
    )

    # Themes facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_themes',
            filter_key='theme',
            title=_('Theme'),
            weight=10,
            collection_key='23WS6R2T',
        )
    )

    # Our publications facet and badge.f
    KERKO_COMPOSER.add_facet(
        FlatFacetSpec(
            key='facet_ours',
            title=_('Our publications') + ' <span class="fas fa-star" aria-hidden="true"></span>',
            filter_key='ours',
            weight=1,
            field_type=BOOLEAN,
            extractor=InCollectionExtractor('SGAGGGLK'),
            codec=BooleanFacetCodec(true_label=_('Yes'), false_value='', false_label=''),
            missing_label=None,
            sort_key=['label'],
            sort_reverse=False,
            item_view=False,
            allow_overlap=False,
            query_class=Term,
        )
    )
    KERKO_COMPOSER.add_field(
        FieldSpec(
            key='ours',
            field_type=BOOLEAN(stored=True),
            extractor=InCollectionExtractor('SGAGGGLK'),
        )
    )
    KERKO_COMPOSER.add_badge(
        BadgeSpec(
            key='ours',
            field=KERKO_COMPOSER.fields['ours'],
            activator=lambda field, item: bool(item.get(field.key)),
            renderer=TemplateStringRenderer(
                '<span class="fas fa-star" title="{title}"'
                ' aria-hidden="true"></span>'.format(title=_('Our publications'))
            ),
            weight=0,
        )
    )

    # References facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_references',
            filter_key='ref',
            title=_('References'),
            weight=20,
            collection_key='GQH9J3MJ',
        )
    )


class DevelopmentConfig(Config):
    CONFIG = 'development'
    DEBUG = True
    ASSETS_DEBUG = env.bool('ASSETS_DEBUG', True)  # Don't bundle/minify static assets.
    KERKO_ZOTERO_START = env.int('KERKO_ZOTERO_START', 0)
    KERKO_ZOTERO_END = env.int('KERKO_ZOTERO_END', 0)
    LIBSASS_STYLE = 'expanded'


class ProductionConfig(Config):
    CONFIG = 'production'
    DEBUG = False
    ASSETS_DEBUG = env.bool('ASSETS_DEBUG', False)
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
