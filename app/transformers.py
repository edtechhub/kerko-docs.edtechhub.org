"""
Utilities for transforming data.
"""

import re
from copy import deepcopy


def extra_field_cleaner(value):
    if 'extra' in value:
        value = deepcopy(value)  # Preserve original data, might be used by other extractors.
        value['extra'] = re.sub(
            r'^(\s*(EdTechHub|KerkoCite)\..*)$',
            '',
            value['extra'],
            flags=re.IGNORECASE | re.MULTILINE
        ).strip()
    return value
