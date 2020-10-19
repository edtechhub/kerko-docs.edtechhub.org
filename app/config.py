import pathlib
import re

from environs import Env
from flask_babelex import gettext as _
from whoosh.fields import BOOLEAN, STORED

from kerko import codecs, extractors, transformers
from kerko.composer import Composer
from kerko.renderers import TemplateStringRenderer
from kerko.specs import BadgeSpec, CollectionFacetSpec, FieldSpec

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
    ABOUT_URL = 'https://edtechhub.org/about-edtech-hub/'
    ABOUT_TEAM_URL = 'https://edtechhub.org/about-edtech-hub/directors-team/'
    ABOUT_ADVISORS_URL = 'https://edtechhub.org/about-edtech-hub/advisors/'
    TOOLS_DATABASE_URL = 'https://database.edtechhub.org/'
    BLOG_URL = 'https://edtechhub.org/blog/'
    CONTACT_URL = 'https://edtechhub.org/contact-us/'

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
    KERKO_RELATIONS_INITIAL_LIMIT = 50

    KERKO_COMPOSER = Composer(
        whoosh_language=KERKO_WHOOSH_LANGUAGE,
        exclude_default_facets=['facet_tag', 'facet_link', 'facet_item_type', 'facet_year'],
        exclude_default_fields=['data'],
        default_child_include_re='^(_publish|publishPDF)$',
        default_child_exclude_re='',
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

    # Add extractors for the 'alternateId' field.
    KERKO_COMPOSER.fields['alternateId'].extractor.extractors.append(
        extractors.TransformerExtractor(
            extractor=extractors.ItemDataExtractor(key='extra'),
            transformers=[
                transformers.find(
                    regex=r'^\s*EdTechHub.ItemAlsoKnownAs\s*:\s*(.*)$',
                    flags=re.IGNORECASE | re.MULTILINE,
                    max_matches=1,
                ),
                transformers.split(sep=';'),
            ]
        )
    )

    # Learners type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_learners',
            filter_key='learners',
            title=_('Learners'),
            weight=10,
            collection_key='WZXRTV9N',
        )
    )

    # Educators type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_educators',
            filter_key='educators',
            title=_('Educators'),
            weight=20,
            collection_key='MS38G6YW',
        )
    )

    # Education systems type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_education_systems',
            filter_key='education_systems',
            title=_('Education systems'),
            weight=30,
            collection_key='ZN4PI2Z6',
        )
    )

    # Cost effectiveness type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_cost_effectiveness',
            filter_key='cost_effectiveness',
            title=_('Cost effectiveness'),
            weight=40,
            collection_key='SCMAR3ZW',
        )
    )

    # Hardware and modality type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_hardware_and_modality',
            filter_key='hardware_and_modality',
            title=_('Hardware and modality'),
            weight=50,
            collection_key='CE7P7GJX',
        )
    )

    # Educational level type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_educational_level',
            filter_key='educational_level',
            title=_('Educational level'),
            weight=60,
            collection_key='B2CQYHX8',
        )
    )

    # Within-country contexts type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_within_country_contexts',
            filter_key='within_country_contexts',
            title=_('Within-country contexts'),
            weight=70,
            collection_key='KY3HHD5I',
        )
    )

    # Language of publication type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_language_of_publication',
            filter_key='language_of_publication',
            title=_('Language of publication'),
            weight=80,
            collection_key='5WYC9ALL',
        )
    )

    # Country type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_country',
            filter_key='country',
            title=_('Country'),
            weight=90,
            collection_key='4UP8CZQE',
        )
    )

    # Research method type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_research_method',
            filter_key='research_method',
            title=_('Research method'),
            weight=110,
            collection_key='P4WEVZLQ',
        )
    )

    # COVID and reopening of schools type facet.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_covid_and_reopening_of_schools',
            filter_key='covid_and_reopening_of_schools',
            title=_('COVID and reopening of schools'),
            weight=120,
            collection_key='TIYLRP8N',
        )
    )

    # Featured publisher facet and badge.
    KERKO_COMPOSER.add_facet(
        CollectionFacetSpec(
            key='facet_featured',
            title=_('Featured publisher'),
            filter_key='featured',
            weight=100,
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
            weight=100,
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
