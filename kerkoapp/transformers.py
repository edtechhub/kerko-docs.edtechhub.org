"""
Utilities for transforming data.
"""

import re
from copy import deepcopy


def extra_field_cleaner(value):
    if 'extra' in value:
        value = deepcopy(value)  # Preserve original data, might be used by other extractors.
        pattern = re.compile(r'^\s*(EdTechHub|KerkoCite)\..*', flags=re.IGNORECASE)
        value['extra'] = '\n'.join(
            filter(lambda line: not pattern.match(line), value['extra'].split('\n'))
        ).strip()
    return value
