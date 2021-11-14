import pathlib
import re

from environs import Env
from flask_babel import gettext as _
from kerko import extractors, transformers
from kerko.composer import Composer
from kerko.renderers import TemplateRenderer
from kerko.specs import BadgeSpec, CollectionFacetSpec, FieldSpec, SortSpec
from whoosh.fields import BOOLEAN, STORED

from .extractors import InCollectionBoostExtractor
from .transformers import extra_field_cleaner

# pylint: disable=invalid-name

env = Env()
env.read_env()


class Config():

    def __init__(self):
        app_dir = pathlib.Path(env.str('FLASK_APP')).parent.absolute()

        # Get configuration values from the environment.
        self.SECRET_KEY = env.str('SECRET_KEY')
        self.KERKO_ZOTERO_API_KEY = env.str('KERKO_ZOTERO_API_KEY')
        self.KERKO_ZOTERO_LIBRARY_ID = env.str('KERKO_ZOTERO_LIBRARY_ID')
        self.KERKO_ZOTERO_LIBRARY_TYPE = env.str('KERKO_ZOTERO_LIBRARY_TYPE')
        self.KERKO_DATA_DIR = env.str('KERKO_DATA_DIR', str(app_dir / 'data' / 'kerko'))

        # Set other configuration variables.
        self.LOGGING_HANDLER = 'default'
        self.EXPLAIN_TEMPLATE_LOADING = False

        self.LIBSASS_INCLUDES = [
            str(pathlib.Path(__file__).parent.parent / 'static' / 'src' / 'vendor' / 'bootstrap' / 'scss'),
            str(pathlib.Path(__file__).parent.parent / 'static' / 'src' / 'vendor' / '@fortawesome' / 'fontawesome-free' / 'scss'),
        ]

        self.BABEL_DEFAULT_LOCALE = 'en_GB'
        self.KERKO_WHOOSH_LANGUAGE = 'en'
        self.KERKO_ZOTERO_LOCALE = 'en-GB'

        self.HOME_URL = 'https://edtechhub.org/'
        self.HOME_TITLE = _("The EdTech Hub")
        self.HOME_SUBTITLE = _("Research and Innovation to fulfil the potential of EdTech")
        self.ABOUT_URL = 'https://edtechhub.org/about-edtech-hub/'
        self.ABOUT_TEAM_URL = 'https://edtechhub.org/about-edtech-hub/directors-team/'
        self.ABOUT_ADVISORS_URL = 'https://edtechhub.org/about-edtech-hub/advisors/'
        self.TOOLS_DATABASE_URL = 'https://database.edtechhub.org/'
        self.BLOG_URL = 'https://edtechhub.org/blog/'
        self.CONTACT_URL = 'https://edtechhub.org/contact-us/'

        self.NAV_TITLE = _("Evidence Library")
        self.KERKO_TITLE = _("Evidence Library – The EdTech Hub")
        self.KERKO_PRINT_ITEM_LINK = True
        self.KERKO_PRINT_CITATIONS_LINK = True
        self.KERKO_RESULTS_FIELDS = ['id', 'attachments', 'bib', 'coins', 'data', 'preview', 'url']
        self.KERKO_RESULTS_ABSTRACTS = True
        self.KERKO_RESULTS_ABSTRACTS_MAX_LENGTH = 500
        self.KERKO_RESULTS_ABSTRACTS_MAX_LENGTH_LEEWAY = 40
        self.KERKO_TEMPLATE_LAYOUT = 'app/layout.html.jinja2'
        self.KERKO_TEMPLATE_SEARCH = 'app/search.html.jinja2'
        self.KERKO_TEMPLATE_SEARCH_ITEM = 'app/search-item.html.jinja2'
        self.KERKO_TEMPLATE_ITEM = 'app/item.html.jinja2'
        self.KERKO_DOWNLOAD_ATTACHMENT_NEW_WINDOW = True
        self.KERKO_RELATIONS_INITIAL_LIMIT = 50

        # CAUTION: The URL's query string must be changed after any edit to the CSL
        # style, otherwise zotero.org might still use a previously cached version of
        # the file.
        self.KERKO_CSL_STYLE = 'https://docs.edtechhub.org/static/dist/csl/eth_apa.xml?202012301815'

        self.KERKO_COMPOSER = Composer(
            whoosh_language=self.KERKO_WHOOSH_LANGUAGE,
            exclude_default_facets=['facet_tag', 'facet_link', 'facet_item_type'],
            exclude_default_fields=['data'],
            default_child_include_re='^(_publish|publishPDF)$',
            default_child_exclude_re='',
        )

        # Replace the default 'data' extractor to strip unwanted data from the Extra field.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='data',
                field_type=STORED,
                extractor=extractors.TransformerExtractor(
                    extractor=extractors.RawDataExtractor(),
                    transformers=[extra_field_cleaner]
                ),
            )
        )

        # Add field for storing the formatted item preview used on search result
        # pages. This relies on the CSL style's in-text citation formatting and only
        # makes sense using our custom CSL style!
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='preview',
                field_type=STORED,
                extractor=extractors.TransformerExtractor(
                    extractor=extractors.ItemExtractor(key='citation', format_='citation'),
                    # Zotero wraps the citation in a <span> element (most probably
                    # because it expects the 'citation' format to be used in-text),
                    # but that <span> has to be removed because our custom CSL style
                    # causes <div>s to be nested within. Let's replace that <span>
                    # with the same markup that the 'bib' format usually provides.
                    transformers=[
                        lambda value: re.sub(r'^<span>', '<div class="csl-entry">', value, count=1),
                        lambda value: re.sub(r'</span>$', '</div>', value, count=1),
                    ]
                )
            )
        )

        # Add extractors for the 'alternate_id' field.
        self.KERKO_COMPOSER.fields['alternate_id'].extractor.extractors.append(
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
        self.KERKO_COMPOSER.fields['alternate_id'].extractor.extractors.append(
            extractors.TransformerExtractor(
                extractor=extractors.ItemDataExtractor(key='extra'),
                transformers=[
                    transformers.find(
                        regex=r'^\s*KerkoCite.ItemAlsoKnownAs\s*:\s*(.*)$',
                        flags=re.IGNORECASE | re.MULTILINE,
                        max_matches=1,
                    ),
                    transformers.split(sep=' '),
                ]
            )
        )
        self.KERKO_COMPOSER.fields['alternate_id'].extractor.extractors.append(
            extractors.TransformerExtractor(
                extractor=extractors.ItemDataExtractor(key='extra'),
                transformers=[
                    transformers.find(
                        regex=r'^\s*shortDOI\s*:\s*(\S+)\s*$',
                        flags=re.IGNORECASE | re.MULTILINE,
                        max_matches=0,
                    ),
                ]
            )
        )

        # Learners type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_learners',
                filter_key='learners',
                title=_('Learners'),
                weight=10,
                collection_key='WZXRTV9N',
            )
        )

        # Educators type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_educators',
                filter_key='educators',
                title=_('Educators'),
                weight=20,
                collection_key='MS38G6YW',
            )
        )

        # Education systems type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_education_systems',
                filter_key='education_systems',
                title=_('Education systems'),
                weight=30,
                collection_key='ZN4PI2Z6',
            )
        )

        # Cost effectiveness type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_cost_effectiveness',
                filter_key='cost_effectiveness',
                title=_('Cost effectiveness'),
                weight=40,
                collection_key='SCMAR3ZW',
            )
        )

        # Hardware and modality type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_hardware_and_modality',
                filter_key='hardware_and_modality',
                title=_('Hardware and modality'),
                weight=50,
                collection_key='CE7P7GJX',
            )
        )

        # Educational level type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_educational_level',
                filter_key='educational_level',
                title=_('Educational level'),
                weight=60,
                collection_key='B2CQYHX8',
            )
        )

        # Within-country contexts type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_within_country_contexts',
                filter_key='within_country_contexts',
                title=_('Within-country contexts'),
                weight=70,
                collection_key='KY3HHD5I',
            )
        )

        # Language of publication type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_language_of_publication',
                filter_key='language_of_publication',
                title=_('Language of publication'),
                weight=80,
                collection_key='5WYC9ALL',
            )
        )

        # Country type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_country',
                filter_key='country',
                title=_('Geography'),
                weight=90,
                collection_key='4UP8CZQE',
            )
        )

        # Research method type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_research_method',
                filter_key='research_method',
                title=_('Research method'),
                weight=110,
                collection_key='P4WEVZLQ',
            )
        )

        # COVID and reopening of schools type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_covid_and_reopening_of_schools',
                filter_key='covid_and_reopening_of_schools',
                title=_('COVID and reopening of schools'),
                weight=120,
                collection_key='TIYLRP8N',
            )
        )

        # Hub Only facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_edtechhub_only',
                title=_('EdTech Hub Publications'),
                filter_key='hubonly',
                weight=1,
                collection_key='BFS3UXT4',
            )
        )

        # Featured publisher facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_featured',
                title=_('Other publishers'),
                filter_key='featured',
                weight=101,
                collection_key='SGAGGGLK',
            )
        )

        # EdTech Hub flag and badge.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='edtechhub',
                field_type=BOOLEAN(stored=True),
                extractor=extractors.InCollectionExtractor(collection_key='BFS3UXT4'),
            )
        )
        self.KERKO_COMPOSER.add_badge(
            BadgeSpec(
                key='edtechhub',
                field=self.KERKO_COMPOSER.fields['edtechhub'],
                activator=lambda field, item: bool(item.get(field.key)),
                renderer=TemplateRenderer(
                    'app/_hub-badge.html.jinja2', badge_title=_('Published by The EdTech Hub')
                ),
                weight=100,
            )
        )

        # Boost factor for every field of any EdTech Hub publication.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='_boost',  # Per whoosh.writing.IndexWriter.add_document() usage.
                field_type=None,  # Not to be added to the schema.
                extractor=InCollectionBoostExtractor(collection_key='BFS3UXT4', boost_factor=5.0),
            )
        )

        # Sort option based on the EdTech Hub flag.
        self.KERKO_COMPOSER.add_sort(
            SortSpec(
                key='hub_desc',
                label=_('EdTech Hub first'),
                weight=5,
                fields=[
                    self.KERKO_COMPOSER.fields['edtechhub'],
                    self.KERKO_COMPOSER.fields['sort_date'],
                    self.KERKO_COMPOSER.fields['sort_creator'],
                    self.KERKO_COMPOSER.fields['sort_title']
                ],
                reverse=[
                    False,
                    True,
                    False,
                    False,
                ],
            )
        )


class DevelopmentConfig(Config):

    def __init__(self):
        super().__init__()

        self.CONFIG = 'development'
        self.DEBUG = True
        self.ASSETS_DEBUG = env.bool('ASSETS_DEBUG', True)  # Don't bundle/minify static assets.
        self.KERKO_ZOTERO_START = env.int('KERKO_ZOTERO_START', 0)
        self.KERKO_ZOTERO_END = env.int('KERKO_ZOTERO_END', 0)
        self.LIBSASS_STYLE = 'expanded'
        self.LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'DEBUG')


class ProductionConfig(Config):

    def __init__(self):
        super().__init__()

        self.CONFIG = 'production'
        self.DEBUG = False
        self.ASSETS_DEBUG = env.bool('ASSETS_DEBUG', False)
        self.ASSETS_AUTO_BUILD = False
        self.LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'WARNING')
        self.GOOGLE_ANALYTICS_ID = 'UA-149862882-2'
        self.LIBSASS_STYLE = 'compressed'


CONFIGS = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
