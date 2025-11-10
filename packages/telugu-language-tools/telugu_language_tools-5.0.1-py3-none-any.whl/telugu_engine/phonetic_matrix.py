"""
Phonetic normalization rules for lightweight Telugu engine.

This module does NOT translate to Telugu script. It only normalizes
romanized inputs into a consistent, rule-based phonetic form before
tense building and transliteration.

Keep rules small and composable; avoid large tables.
"""

from __future__ import annotations

import re
from typing import Callable, Iterable, List, Tuple


Rule = Tuple[re.Pattern, str]


def _compile_rules() -> List[Rule]:
    rules: List[Rule] = []

    # Normalize common digraphs and clusters to a canonical form
    # Prioritize longer patterns first to avoid partial matches.
    patterns = [
        (r"ksh", "ksh"),
        (r"x", "ks"),
        (r"shh", "sh"),
        (r"sch", "sh"),
        (r"sha", "sha"),
        (r"shi", "shi"),
        (r"shu", "shu"),
        (r"sh", "sh"),
        (r"chh", "ch"),
        (r"cch", "ch"),
        (r"ph", "ph"),  # keep aspirates
        (r"th", "th"),
        (r"dh", "dh"),
        (r"kh", "kh"),
        (r"gh", "gh"),
        (r"bh", "bh"),
        (r"aa", "aa"),
        (r"ii|ee", "ii"),
        (r"uu|oo", "uu"),
    ]

    for pat, rep in patterns:
        rules.append((re.compile(pat), rep))

    # Example targeted rule from the spec
    rules.insert(0, (re.compile(r"kri"), "kri"))  # keep 'kri' together

    return rules


_RULES = _compile_rules()


def map_sound(text: str) -> str:
    """
    Normalize romanized input to a canonical phonetic form.

    This is a conservative pass meant to standardize inputs. It intentionally
    does only lightweight replacements. Transliteration to Telugu script is
    handled by `transliterator.eng_to_telugu`.
    """
    s = text.strip().lower()
    if not s:
        return s

    # apply simple replacements
    for pat, rep in _RULES:
        s = pat.sub(rep, s)

    # collapse excessive spaces
    s = re.sub(r"\s+", " ", s)

    return s


__all__ = ["map_sound"]

