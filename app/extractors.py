"""
Functions for extracting data from Zotero items.
"""

import re

from kerko.extractors import Extractor, InCollectionExtractor


class InCollectionBoostExtractor(InCollectionExtractor):
    """Extract a boosting factor based on the membership of an item into a collection."""

    def __init__(self, *, boost_factor, **kwargs):
        super().__init__(**kwargs)
        self.boost_factor = boost_factor

    def extract(self, item, library_context, spec):
        if super().extract(item, library_context, spec):
            return self.boost_factor
        return None


class MatchesTagExtractor(Extractor):
    """Extract a boolean indicating if the item has a tag matching a given regular expression."""

    def __init__(self, *, pattern='', **kwargs):
        super().__init__(**kwargs)
        self.re_pattern = re.compile(pattern) if pattern else None

    def extract(self, item, library_context, spec):
        for tag_data in item.get('data', {}).get('tags', []):
            tag = tag_data.get('tag', '').strip()
            if tag and self.re_pattern.match(tag):
                return True
        return False
