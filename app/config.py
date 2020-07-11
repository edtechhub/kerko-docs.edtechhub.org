import pathlib
import re

from environs import Env
from flask_babelex import gettext as _
from whoosh.fields import BOOLEAN, ID, STORED

from kerko import codecs, extractors
from kerko.composer import Composer
from kerko.renderers import TemplateStringRenderer
from kerko.specs import BadgeSpec, CollectionFacetSpec, FieldSpec
from kerko.transformers import make_regex_find_transformer, make_split_transformer

from .transformers import extra_field_cleaner

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
    ABOUT_URL = 'https://edtechhub.org/about-the-edtech-hub/'
    BLOG_URL = 'https://edtechhub.org/blog/'
    CONTACT_URL = 'https://edtechhub.org/jobs/'

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
    KERKO_DOWNLOAD_ATTACHMENT_NEW_WINDOW = True

    KERKO_COMPOSER = Composer(
        whoosh_language=KERKO_WHOOSH_LANGUAGE,
        exclude_default_facets=['facet_tag', 'facet_link', 'facet_item_type'],
        exclude_default_fields=['data'],
        default_child_whitelist_re='^(_publish|publishPDF)$',
        default_child_blacklist_re='',
    )

    # Replace the default 'data' extractor to strip unwanted data from the Extra field.
    KERKO_COMPOSER.add_field(
        FieldSpec(
            key='data',
            field_type=STORED,
            extractor=extractors.TransformerExtractor(
                extractor=extractors.RawDataExtractor(),
                transformers=[extra_field_cleaner]
            ),
            codec=codecs.JSONFieldCodec()
        )
    )

    # Alternate ID, for the `kerko.item_redirect` view.
    KERKO_COMPOSER.add_field(
        FieldSpec(
            key='alternateId',
            field_type=ID,
            extractor=extractors.TransformerExtractor(
                extractor=extractors.ItemDataExtractor(key='extra'),
                transformers=[
                    make_regex_find_transformer(
                        regex=r'^\s*EdTechHub.ItemAlsoKnownAs\s*:\s*(.*)$',
                        flags=re.IGNORECASE | re.MULTILINE,
                        max_matches=1,
                    ),
                    make_split_transformer(sep=';'),
                ]
            )
        )
    )

    # Featured publisher facet and badge.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_featured',
            title=_('Featured publisher'),
            filter_key='featured',
            weight=10,
            collection_key='SGAGGGLK',
        )
    )
    KERKO_COMPOSER.add_field(
        FieldSpec(
            key='edtechhub',
            field_type=BOOLEAN(stored=True),
            extractor=extractors.InCollectionExtractor(collection_key='BFS3UXT4'),
        )
    )
    KERKO_COMPOSER.add_badge(
        BadgeSpec(
            key='edtechhub',
            field=KERKO_COMPOSER.fields['edtechhub'],
            activator=lambda field, item: bool(item.get(field.key)),
            renderer=TemplateStringRenderer(
                '<span class="fas fa-star" title="{title}"'
                ' aria-hidden="true"></span>'.format(title=_('Published by The EdTech Hub'))
            ),
            weight=0,
        )
    )

    # Publication type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_pubtype',
            filter_key='pubtype',
            title=_('Publication type'),
            weight=20,
            collection_key='WIWEWXZ8',
        )
    )

    # TODO: Audience facet.
    # KERKO_COMPOSER.add_facet(
    #     CollectionFacetSpec(
    #         key='facet_audience',
    #         filter_key='audience',
    #         title=_('Audience'),
    #         weight=30,
    #         collection_key='WJZFJQ5D',
    #     )
    # )

    # Themes facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_themes',
            filter_key='theme',
            title=_('Theme'),
            weight=40,
            collection_key='23WS6R2T',
        )
    )

    # Location facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_location',
            filter_key='location',
            title=_('Location'),
            weight=50,
            collection_key='PFCKJVIL',
        )
    )

    # Other facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_references',
            filter_key='ref',
            title=_('Other'),
            weight=60,
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
    LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'DEBUG')


class ProductionConfig(Config):
    CONFIG = 'production'
    DEBUG = False
    ASSETS_DEBUG = env.bool('ASSETS_DEBUG', False)
    ASSETS_AUTO_BUILD = False
    LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'WARNING')
    GOOGLE_ANALYTICS_ID = 'UA-149862882-2'
    LIBSASS_STYLE = 'compressed'


CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
