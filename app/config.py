import pathlib
import re

from environs import Env
from flask_babel import gettext as _
from kerko import extractors, transformers
from kerko.composer import Composer
from kerko.renderers import TemplateRenderer
from kerko.specs import BadgeSpec, CollectionFacetSpec, FieldSpec, SortSpec
from whoosh.fields import BOOLEAN, STORED

from .extractors import InCollectionBoostExtractor, MatchesTagExtractor
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
        self.SANDBOXES_URL = 'https://edtechhub.org/sandboxes/'
        self.BLOG_URL = 'https://edtechhub.org/blog/'
        self.CONTACT_URL = 'https://edtechhub.org/contact-us/'

        self.NAV_TITLE = _("Evidence Library")
        self.KERKO_TITLE = _("Evidence Library – The EdTech Hub")
        self.KERKO_PRINT_ITEM_LINK = True
        self.KERKO_PRINT_CITATIONS_LINK = True
        self.KERKO_RESULTS_FIELDS = ['id', 'attachments', 'bib', 'data', 'preview', 'url']
        self.KERKO_RESULTS_ABSTRACTS = True
        self.KERKO_RESULTS_ABSTRACTS_MAX_LENGTH = 500
        self.KERKO_RESULTS_ABSTRACTS_MAX_LENGTH_LEEWAY = 40
        self.KERKO_TEMPLATE_LAYOUT = 'app/layout.html.jinja2'
        self.KERKO_TEMPLATE_SEARCH = 'app/search.html.jinja2'
        self.KERKO_TEMPLATE_SEARCH_ITEM = 'app/search-item.html.jinja2'
        self.KERKO_TEMPLATE_ITEM = 'app/item.html.jinja2'
        self.KERKO_DOWNLOAD_ATTACHMENT_NEW_WINDOW = True
        self.KERKO_RELATIONS_INITIAL_LIMIT = 50
        self.KERKO_FEEDS = ['atom']
        self.KERKO_FEEDS_MAX_DAYS = 0

        # CAUTION: The URL's query string must be changed after any edit to the CSL
        # style, otherwise zotero.org might still use a previously cached version of
        # the file.
        self.KERKO_CSL_STYLE = 'https://docs.edtechhub.org/static/dist/csl/eth_apa.xml?202012301815'

        self.KERKO_COMPOSER = Composer(
            whoosh_language=self.KERKO_WHOOSH_LANGUAGE,
            exclude_default_facets=['facet_tag', 'facet_link', 'facet_item_type'],
            exclude_default_fields=['data'],
            default_item_exclude_re=r'^_exclude$',
            default_child_include_re=r'^(_publish|publishPDF)$',
            default_child_exclude_re=r'',
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

        # Learners facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_learners',
                title=_('Learners'),
                filter_key='learners',
                weight=1,
                collection_key='X6MP49KP',
            )
        )

        # Educators type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_educators',
                filter_key='educators',
                title=_('Educators'),
                weight=2,
                collection_key='HCTKHFNN',
            )
        )

        # Education systems type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_education_systems',
                filter_key='education_systems',
                title=_('Education systems'),
                weight=3,
                collection_key='X3DPTXLG',
            )
        )

        # Cost effectiveness type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_cost_effectiveness',
                filter_key='cost_effectiveness',
                title=_('Cost effectiveness'),
                weight=4,
                collection_key='3TN4ME9B',
            )
        )

        # Hardware and modality type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_hardware_and_modality',
                filter_key='hardware_and_modality',
                title=_('Hardware and modality'),
                weight=5,
                collection_key='C965YJYB',
            )
        )

        # Educational level type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_educational_level',
                filter_key='educational_level',
                title=_('Educational level'),
                weight=6,
                collection_key='B42SBYGD',
            )
        )

        # Within-country contexts type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_within_country_contexts',
                filter_key='within_country_contexts',
                title=_('Within-country contexts'),
                weight=7,
                collection_key='P3Q22NYF',
            )
        )

        # Language of publication type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_language_of_publication',
                filter_key='language_of_publication',
                title=_('Language of publication'),
                weight=8,
                collection_key='ZNNITHFH',
            )
        )

        # Publisher and type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_publisher_type',
                filter_key='publisher_type',
                title=_('Publisher and type'),
                weight=9,
                collection_key='N6HGZU24',
            )
        )

        # Research method type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_research_method',
                filter_key='research_method',
                title=_('Research method'),
                weight=10,
                collection_key='9WEL59XM',
            )
        )

        # COVID and reopening of schools type facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_covid_and_reopening_of_schools',
                filter_key='covid_and_reopening_of_schools',
                title=_('COVID and reopening of schools'),
                weight=11,
                collection_key='NRS95TC8',
            )
        )

        # Topic Area facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_topic_area',
                title=_('Topic Area'),
                filter_key='topic_area',
                weight=12,
                collection_key='W6YXX3J6',
            )
        )

        # Focus Countries facet.
        self.KERKO_COMPOSER.add_facet(
            CollectionFacetSpec(
                key='facet_focus_countries',
                title=_('Focus Countries'),
                filter_key='focus_countries',
                weight=13,
                collection_key='F29UQFBX',
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
        # "Internal document" flag and badge.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='internal',
                field_type=BOOLEAN(stored=True),
                extractor=MatchesTagExtractor(pattern=r'^_internal$'),
            )
        )
        self.KERKO_COMPOSER.add_badge(
            BadgeSpec(
                key='internal',
                field=self.KERKO_COMPOSER.fields['internal'],
                activator=lambda field, item: item.get(field.key, False),
                renderer=TemplateRenderer(
                    'app/_text-badge.html.jinja2', text=_('Internal<br />document')
                ),
                weight=10,
            )
        )
        # "Coming soon" flag and badge.
        self.KERKO_COMPOSER.add_field(
            FieldSpec(
                key='comingsoon',
                field_type=BOOLEAN(stored=True),
                extractor=MatchesTagExtractor(pattern=r'^_comingsoon$'),
            )
        )
        self.KERKO_COMPOSER.add_badge(
            BadgeSpec(
                key='comingsoon',
                field=self.KERKO_COMPOSER.fields['comingsoon'],
                activator=lambda field, item: item.get(field.key, False),
                renderer=TemplateRenderer(
                    'app/_text-badge.html.jinja2', text=_('Coming<br >soon')
                ),
                weight=20,
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
        self.LIBSASS_STYLE = 'expanded'
        self.LOGGING_LEVEL = env.str('LOGGING_LEVEL', 'DEBUG')
        # self.EXPLAIN_TEMPLATE_LOADING = True


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
