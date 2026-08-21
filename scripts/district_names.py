"""Canonical matching key for Malaysian administrative district names.

Four DOSM products spell districts four ways, e.g. Perak's Larut/Matang appears
as 'Larut & Matang' (DTS 2025 sheet 8B), 'Larut dan Matang' (GDP-by-district),
'Larut Dan Matang' (population_district) and 'Larut dan Matang' (amenities).
Rather than maintain pairwise alias maps, everything is reduced to one key.
"""
import re
import unicodedata

_SUBS = [
    (r"\s*&\s*", " dan "),          # 'Larut & Matang'
    (r"\band\b", "dan"),
    (r"\bsp\b", "seberang perai"),  # 'Sp Tengah' -> 'Seberang Perai Tengah'
    (r"\bhulu\b", "ulu"),           # 'Hulu Langat' / 'Ulu Langat'
    (r"\bhighlands\b", "highland"), # 'Cameron Highlands' / 'Cameron Highland'
    (r"\bw\.?\s*p\.?\b", "wp"),
]


def dkey(name):
    """Lower-cased, punctuation- and variant-normalised district key."""
    s = unicodedata.normalize("NFKC", str(name)).replace("\xa0", " ").strip().lower()
    s = s.replace("’", "'")
    for pat, rep in _SUBS:
        s = re.sub(pat, rep, s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def skey(state):
    """Same idea for state names ('W.P. Kuala Lumpur' vs 'WP Kuala Lumpur')."""
    return dkey(state)


def keypair(state, district):
    return (skey(state), dkey(district))
