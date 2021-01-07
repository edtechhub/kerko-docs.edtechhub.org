"""
Functions for extracting data from Zotero items.
"""

from kerko.extractors import InCollectionExtractor


class InCollectionBoostExtractor(InCollectionExtractor):
    """Extract a boosting factor based on the membership of an item into a collection."""

    def __init__(self, *, boost_factor, **kwargs):
        super().__init__(**kwargs)
        self.boost_factor = boost_factor

    def extract(self, item_context, library_context, spec):
        if super().extract(item_context, library_context, spec):
            return self.boost_factor
        return None
