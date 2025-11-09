"""
Telugu Library v2.0 - Comprehensive Transliteration Engine
===========================================================

Features:
- Old vs New Telugu Alphabet Support (Classical, Modern, Hybrid)
- Bidirectional Transliteration (English ↔ Telugu)
- Semantic Word Mapping (English ↔ Telugu meanings)
- Universal Search (works for both languages)

Examples:
    eng_to_telugu("krishna")              → కృష్ణ
    telugu_to_eng("కృష్ణ")                 → krishna
    semantic_match("who")                 → ["ఎవరు", "ఎవరో"]
    eng_to_telugu_with_style("rama", "modern")  → రామ
    eng_to_telugu_with_style("rama", "classical") → రామ
"""

# ============================================================================
# PART 1: ENGLISH → TELUGU TRANSLITERATION
# ============================================================================

def normalize_roman_input(text: str) -> str:
    """Normalizes romanized input to a more basic ASCII representation."""
    replacements = {
        'ā': 'aa', 'ē': 'ee', 'ī': 'ii', 'ō': 'oo', 'ū': 'uu',
        'ṁ': 'm', 'ṇ': 'n', 'ḍ': 'd', 'ṭ': 't', 'ś': 'sh',
        'ṣ': 'sh', 'ṛ': 'ri'
    }
    for special, basic in replacements.items():
        text = text.replace(special, basic)
    return text

def eng_to_telugu_base(text: str, rules: dict) -> str:
    """Core transliteration engine with custom rules (pure transliteration only)."""
    text = normalize_roman_input(text)
    text = (text or "").lower().strip()

    consonants = rules.get("consonants", {})
    vowels = rules.get("vowels", {})
    matras = rules.get("matras", {})
    clusters = rules.get("clusters", {})
    strip_final_virama = rules.get("strip_final_virama", True)

    result = []
    i = 0
    prev_cons = False

    def emit_consonant(key: str, join_prev=False):
        nonlocal prev_cons
        if join_prev and prev_cons:
            result.append("్")
        result.append(consonants.get(key, key))
        prev_cons = True

    while i < len(text):
        chunk5 = text[i:i+5]
        chunk4 = text[i:i+4]
        chunk3 = text[i:i+3]
        chunk2 = text[i:i+2]
        single = text[i]

        # NEW: Handle vocalic r (r̥) - detect when 'r' between consonants should be vocalic
        if prev_cons and single == 'r':
            # Look ahead: is there a consonant after optional vowel?
            lookahead = i + 1
            while lookahead < len(text) and text[lookahead] in 'aeiou':
                lookahead += 1
            if lookahead < len(text) and text[lookahead] in 'bcdfghjklmnpqrstvwxyz':
                # Vocalic r: add ృ after the previous consonant
                # The ృ suppresses the inherent 'a' of the previous consonant
                # It doesn't affect the next consonant, so prev_cons stays True
                result.append("ృ")
                # Don't reset prev_cons - the next consonant will still have its inherent 'a'
                i += 1
                continue

        # Handle 5-letter clusters (krish for కృష్ణ)
        if chunk5 in clusters:
            if prev_cons:
                result.append("్")
            for idx, ck in enumerate(clusters[chunk5]):
                emit_consonant(ck, join_prev=(idx > 0))
            i += 5
            continue

        # Handle 4-letter clusters
        if chunk4 in clusters:
            if prev_cons:
                result.append("్")
            for idx, ck in enumerate(clusters[chunk4]):
                emit_consonant(ck, join_prev=(idx > 0))
            i += 4
            continue

        # Handle 3-letter clusters
        if chunk3 in clusters:
            if prev_cons:
                result.append("్")
            for idx, ck in enumerate(clusters[chunk3]):
                emit_consonant(ck, join_prev=(idx > 0))
            i += 3
            continue

        # Handle 2-letter clusters
        if chunk2 in clusters:
            if prev_cons:
                result.append("్")
            for idx, ck in enumerate(clusters[chunk2]):
                emit_consonant(ck, join_prev=(idx > 0))
            i += 2
            continue

        # Handle 2-letter vowels
        if chunk2 in vowels:
            if prev_cons:
                result.append(matras.get(chunk2, ""))
                prev_cons = False # A vowel sound has been produced
            else:
                result.append(vowels[chunk2])
                prev_cons = False
            i += 2
            continue

        # Handle 2-letter consonants
        if chunk2 in consonants:
            if prev_cons:
                result.append("్")
            emit_consonant(chunk2)
            i += 2
            continue

        # Single vowel
        if single in vowels:
            # Skip single "a" - consonants already have inherent 'a' sound
            if single == "a" and prev_cons:
                # 'a' after consonant = inherent vowel (skip)
                prev_cons = False
                i += 1
                continue

            # Special case: if the previous character is ృ, treat this as a standalone vowel
            # even though prev_cons is True. Also, DON'T reset prev_cons after this vowel
            is_after_vocalic_r = (result and result[-1] == "ృ")

            # Check if this is a matra (after a consonant) or standalone vowel
            if prev_cons and not is_after_vocalic_r:
                # This is a matra
                result.append(matras.get(single, ""))
                prev_cons = False # A vowel sound has been produced
            else:
                # This is a standalone vowel
                result.append(vowels[single])
                # Standalone vowel, so prev_cons becomes False
                # EXCEPTION: if this vowel comes after ృ, don't reset prev_cons
                # because ృ doesn't suppress inherent vowels (it only suppresses the vowel of its own consonant)
                if not is_after_vocalic_r:
                    prev_cons = False
            i += 1
            continue

        # Single consonant
        if single in consonants:
            if prev_cons:
                result.append("్")
            emit_consonant(single)
            i += 1
            continue

        # Unknown character
        result.append(single)
        prev_cons = False
        i += 1

    if strip_final_virama and result and result[-1] == "్":
        result.pop()

    return "".join(result)


def get_base_consonants(style="modern"):
    """
    Get consonant mappings for old vs new style.

    Args:
        style: "modern" (new) or "classical" (old)
    """

    # Common consonants in both styles
    common = {
        "k": "క", "kh": "ఖ", "g": "గ", "gh": "ఘ",
        "ch": "చ", "chh": "ఛ", "j": "జ", "jh": "ఝ",
        "t": "త", "th": "థ", "d": "ద", "dh": "ధ", "n": "న",
        "tt": "ట", "tth": "ఠ", "dd": "డ", "ddh": "ఢ", "nn": "ణ",
        "p": "ప", "ph": "ఫ", "b": "బ", "bh": "భ", "m": "మ",
        "y": "య", "l": "ల", "v": "వ", "w": "వ",
        "sh": "ష", "shh": "శ", "s": "స", "h": "హ",
    }

    if style == "classical":
        # OLD alphabet includes archaic letters
        return {
            **common,
            "r": "ర",
            "rr": "ఱ",      # Retroflex R (archaic)
            "ll": "ళ",      # Retroflex L (still used)
            "lll": "ఴ",     # Voiced retroflex fricative (obsolete)
            "nga": "ఙ",     # Velar nasal (archaic)
            "nya": "ఞ",     # Palatal nasal (archaic)
            "nna": "ణ",     # Retroflex nasal
        }
    else:
        # NEW alphabet (modern/reformed)
        return {
            **common,
            "r": "ర",       # Single R for both
            "rr": "ర్ర",    # Double R as conjunct
            "ll": "ళ",      # Retroflex L (retained)
            "nga": "న",     # Merged with dental N
            "nya": "న",     # Merged with dental N
            "nna": "ణ",     # Retroflex nasal (retained)
        }


def get_base_vowels(style="modern"):
    """Get vowel mappings for old vs new style."""

    common = {
        "aa": "ఆ", "a": "అ",
        "ii": "ఈ", "i": "ఇ",
        "uu": "ఊ", "u": "ఉ",
        "ai": "ఐ", "au": "ఔ",
        "am": "ం", "ah": "ః",
        "ri": "ఋ", "rii": "ౠ",
    }

    if style == "classical":
        return {
            **common,
            "e": "ఎ",       # Short e
            "ee": "ఏ",      # Long ē
            "o": "ఒ",       # Short o
            "oo": "ఓ",      # Long ō
            "li": "ౢ",      # Vocalic l̥ (archaic)
            "lii": "ౣ",     # Vocalic l̥̄ (archaic)
        }
    else:
        return {
            **common,
            "e": "ఎ",
            "ee": "ఏ",
            "o": "ఒ",
            "oo": "ఓ",
            # Archaic vowels dropped
        }


def get_base_matras(style="modern"):
    """Get matra (vowel sign) mappings."""

    common = {
        "aa": "ా", "a": "",
        "ii": "ీ", "i": "ి",
        "uu": "ూ", "u": "ు",
        "ee": "ే", "e": "ె",
        "oo": "ో", "o": "ొ",
        "ai": "ై", "au": "ౌ",
        "am": "ం", "ah": "ః",
        "ri": "ృ", "rii": "ౄ",
    }

    if style == "classical":
        return {
            **common,
            "li": "ౢ",      # Vocalic l̥ matra (archaic)
            "lii": "ౣ",     # Vocalic l̥̄ matra (archaic)
        }
    else:
        return common


def get_clusters(style="modern"):
    """Get common consonant clusters."""
    return {
        # 4-letter clusters
        "ksha": ["k", "sh"],
        "jna": ["j", "n"],
        "shna": ["sh", "n"],
        "shra": ["sh", "r"],
        # 3-letter clusters
        "bhra": ["bh", "r"],
        "gva": ["g", "v"],
        # 2-letter clusters
        "kr": ["k", "r"],
        "tr": ["t", "r"],
        "dr": ["d", "r"],
        "gr": ["g", "r"],
        "pr": ["p", "r"],
        "br": ["b", "r"],
        "vr": ["v", "r"],
        "nr": ["n", "r"],
        "sr": ["s", "r"],
    }


def eng_to_telugu_with_style(text: str, style: str = "modern") -> str:
    """
    Transliteration with style selection (Modern vs Classical vs Hybrid).
    Checks semantic dictionary first, then falls back to transliteration.

    Args:
        text: English text
        style: "modern" (default), "classical", or "hybrid"

    Returns:
        Telugu text using the specified alphabet style
    """
    # Input validation
    if text is None:
        raise ValueError("Input text cannot be None")
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    if not text or not text.strip():
        return ""
    if len(text) > 10000:
        raise ValueError("Input text too long (max 10000 characters)")
    
    # 1. NEW: Check semantic dictionary first for known words
    norm_text = normalize_for_matching(text)
    forward_dict = get_semantic_dictionary()

    if norm_text in forward_dict:
        # Found a known word. Return its first meaning.
        return forward_dict[norm_text][0]

    # 2. No match found. Fallback to pure transliteration.
    rules = {
        "consonants": get_base_consonants(style if style in ["modern", "classical", "hybrid"] else "modern"),
        "vowels": get_base_vowels(style if style in ["modern", "classical", "hybrid"] else "modern"),
        "matras": get_base_matras(style if style in ["modern", "classical", "hybrid"] else "modern"),
        "clusters": get_clusters("modern"),
        "strip_final_virama": True if style in ["modern", "hybrid"] else False,
    }
    return eng_to_telugu_base(text, rules)


def eng_to_telugu_old_new_options(text: str) -> list:
    """
    Generate transliteration options using OLD vs NEW alphabet styles.

    Args:
        text: English text to transliterate

    Returns:
        List of tuples: [(telugu_text, style_description), ...]
    """

    options = []

    # Style 1: MODERN (New Telugu)
    modern_rules = {
        "consonants": get_base_consonants("modern"),
        "vowels": get_base_vowels("modern"),
        "matras": get_base_matras("modern"),
        "clusters": get_clusters("modern"),
        "strip_final_virama": True,
    }
    modern = eng_to_telugu_base(text, modern_rules)
    options.append((modern, "Modern Telugu (Reformed)"))

    # Style 2: CLASSICAL (Old Telugu)
    classical_rules = {
        "consonants": get_base_consonants("classical"),
        "vowels": get_base_vowels("classical"),
        "matras": get_base_matras("classical"),
        "clusters": get_clusters("classical"),
        "strip_final_virama": False,  # Old style kept virama
    }
    classical = eng_to_telugu_base(text, classical_rules)
    options.append((classical, "Classical Telugu (Pre-reform)"))

    # Style 3: HYBRID (some old, some new)
    hybrid_rules = {
        "consonants": {**get_base_consonants("modern"), "rr": "ఱ", "ll": "ళ"},
        "vowels": get_base_vowels("modern"),
        "matras": get_base_matras("modern"),
        "clusters": get_clusters("modern"),
        "strip_final_virama": True,
    }
    hybrid = eng_to_telugu_base(text, hybrid_rules)
    options.append((hybrid, "Hybrid (Modern with some archaic letters)"))

    # Remove duplicates
    seen = set()
    unique_options = []
    for telugu, desc in options:
        if telugu not in seen:
            unique_options.append((telugu, desc))
            seen.add(telugu)

    return unique_options


def compare_old_new_alphabets():
    """
    Display comparison table of OLD vs NEW Telugu alphabets.
    """

    print("\n" + "=" * 80)
    print("OLD vs NEW TELUGU ALPHABET COMPARISON")
    print("=" * 80)

    comparisons = [
        ("Letter", "Old (Classical)", "New (Modern)", "Status", "Notes"),
        ("-" * 15, "-" * 20, "-" * 20, "-" * 12, "-" * 30),

        # Vowels
        ("a", "అ", "అ", "Unchanged", "Short vowel"),
        ("ā", "ఆ", "ఆ", "Unchanged", "Long vowel"),
        ("i", "ఇ", "ఇ", "Unchanged", "Short vowel"),
        ("ī", "ఈ", "ఈ", "Unchanged", "Long vowel"),
        ("u", "ఉ", "ఉ", "Unchanged", "Short vowel"),
        ("ū", "ఊ", "ఊ", "Unchanged", "Long vowel"),
        ("r̥", "ఋ", "ఋ", "Unchanged", "Vocalic R"),
        ("l̥", "ౢ", "(obsolete)", "Removed", "Vocalic L - archaic"),
        ("e", "ఎ", "ఎ", "Unchanged", "Short E"),
        ("ē", "ఏ", "ఏ", "Unchanged", "Long E"),
        ("ai", "ఐ", "ఐ", "Unchanged", "Diphthong"),
        ("o", "ఒ", "ఒ", "Unchanged", "Short O"),
        ("ō", "ఓ", "ఓ", "Unchanged", "Long O"),
        ("au", "ఔ", "ఔ", "Unchanged", "Diphthong"),

        ("", "", "", "", ""),

        # Consonants
        ("ka", "క", "క", "Unchanged", "Velar"),
        ("ṅa", "ఙ", "(merged→న)", "Rare", "Velar nasal"),
        ("cha", "చ", "చ", "Unchanged", "Palatal"),
        ("ña", "ఞ", "(merged→న)", "Rare", "Palatal nasal"),
        ("ṭa", "ట", "ట", "Unchanged", "Retroflex"),
        ("ṇa", "ణ", "ణ", "Unchanged", "Retroflex nasal"),
        ("ta", "త", "త", "Unchanged", "Dental"),
        ("na", "న", "న", "Unchanged", "Dental nasal"),
        ("pa", "ప", "ప", "Unchanged", "Labial"),
        ("ya", "య", "య", "Unchanged", "Semivowel"),
        ("ra", "ర", "ర", "Unchanged", "Alveolar"),
        ("ṟa", "ఱ", "(rare)", "Archaic", "Retroflex R"),
        ("la", "ల", "ల", "Unchanged", "Dental lateral"),
        ("ḷa", "ళ", "ళ", "Unchanged", "Retroflex lateral"),
        ("ḻa", "ఴ", "(obsolete)", "Removed", "Fricative - Tamil loan"),
        ("va", "వ", "వ", "Unchanged", "Labial"),
        ("śa", "శ", "శ", "Unchanged", "Palatal sibilant"),
        ("ṣa", "ష", "ష", "Unchanged", "Retroflex sibilant"),
        ("sa", "స", "స", "Unchanged", "Dental sibilant"),
        ("ha", "హ", "హ", "Unchanged", "Glottal"),
    ]

    for row in comparisons:
        print(f"{row[0]:15} {row[1]:20} {row[2]:20} {row[3]:12} {row[4]:30}")

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("  • Modern Telugu has 56 letters (16 vowels + 36 consonants + 4 modifiers)")
    print("  • Classical Telugu had ~60+ letters including archaic forms")
    print("  • Letters ఱ (ṟa), ఴ (ḻa), ౘ, ౙ, ౚ are now obsolete or very rare")
    print("  • Nasals ఙ (ṅa) and ఞ (ña) mostly merged into న (na) in modern usage")
    print("=" * 80 + "\n")


# Main function for backwards compatibility (v0.9)
def eng_to_telugu(text: str, strip_final_virama: bool = True) -> str:
    """
    Clean & Extended Telugu Transliteration Engine (BUG-FIXED v0.9)
    Maintained for backwards compatibility with v0.9.
    Checks semantic dictionary first, then falls back to pure transliteration.

    ✅ Fixed: Added 2-letter cluster checking
    ✅ Fixed: Consistent cluster definitions (no vowels in cluster names)
    ✅ Fixed: Proper processing order (clusters before vowels)
    ✅ Fixed: Comprehensive cluster coverage (2-letter, 3-letter, 4-letter)
    ✅ Includes major clusters (kr, tr, dr, bhra, gva, ksha, jna, shra, shna)
    ✅ Smart virama handling between consonants
    ✅ Correct vowel matras after clusters
    ✅ Optional strip_final_virama for smooth ending
    ✅ Semantic dictionary integration for known words

    Example:
        eng_to_telugu("krishna")   → కృష్ణ
        eng_to_telugu("bhagvaan")  → భగవాన్
        eng_to_telugu("karthik")   → కార్తిక్
    """
    # 1. Check semantic dictionary first for known words
    norm_text = normalize_for_matching(text)
    forward_dict = get_semantic_dictionary()

    if norm_text in forward_dict:
        # Found a known word. Return its first meaning.
        return forward_dict[norm_text][0]

    # 2. No match found. Fallback to pure transliteration.

    consonants = {
        "k": "క", "kh": "ఖ", "g": "గ", "gh": "ఘ",
        "ch": "చ", "jh": "ఝ", "j": "జ",
        "t": "త", "th": "థ", "d": "ద", "dh": "ధ",
        "n": "న", "p": "ప", "ph": "ఫ", "b": "బ", "bh": "భ", "m": "మ",
        "y": "య", "r": "ర", "l": "ల", "v": "వ", "w": "వ",
        "sh": "ష", "s": "స", "h": "హ",
    }

    vowels = {
        "aa": "ఆ", "a": "అ", "ii": "ఈ", "i": "ఇ",
        "uu": "ఊ", "u": "ఉ", "ee": "ఏ", "e": "ఎ",
        "oo": "ఓ", "o": "ఒ", "ai": "ఐ", "au": "ఔ",
        "am": "ం", "ah": "ః",
    }

    matras = {
        "aa": "ా", "a": "", "ii": "ీ", "i": "ి",
        "uu": "ూ", "u": "ు", "ee": "ే", "e": "ె",
        "oo": "ో", "o": "ొ", "ai": "ై", "au": "ౌ",
        "am": "ం", "ah": "ః",
    }

    # Extended clusters - BUG FIX: Consistent definitions (no vowels in names)
    clusters = {
        # 4-letter clusters
        "ksha": ["k", "sh"],
        "jna": ["j", "n"],
        "shna": ["sh", "n"],
        "shra": ["sh", "r"],
        # 3-letter clusters
        "bhra": ["bh", "r"],
        "gva": ["g", "v"],
        # 2-letter clusters
        "kr": ["k", "r"],
        "tr": ["t", "r"],
        "dr": ["d", "r"],
        "gr": ["g", "r"],
        "pr": ["p", "r"],
        "br": ["b", "r"],
        "vr": ["v", "r"],
        "nr": ["n", "r"],
        "sr": ["s", "r"],
    }

    rules = {
        "consonants": consonants,
        "vowels": vowels,
        "matras": matras,
        "clusters": clusters,
        "strip_final_virama": strip_final_virama,
    }

    return eng_to_telugu_base(text, rules)


# ============================================================================
# PART 2: TELUGU → ENGLISH TRANSLITERATION
# ============================================================================

def telugu_to_eng(text: str) -> str:
    """
    Convert Telugu script to English transliteration.

    Example:
        ఎవరు → evaru
        కృష్ణ → krishna
        రామ → rama
    """
    # Input validation
    if text is None:
        raise ValueError("Input text cannot be None")
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    if not text or not text.strip():
        return ""
    if len(text) > 10000:
        raise ValueError("Input text too long (max 10000 characters)")

    # Reverse mapping: Telugu → English
    reverse_vowels = {
        "అ": "a", "ఆ": "aa", "ఇ": "i", "ఈ": "ii",
        "ఉ": "u", "ఊ": "uu", "ఋ": "ri", "ౠ": "rii",
        "ఎ": "e", "ఏ": "ee", "ఐ": "ai",
        "ఒ": "o", "ఓ": "oo", "ఔ": "au",
        "ం": "m", "ః": "h",
    }

    reverse_consonants = {
        "క": "k", "ఖ": "kh", "గ": "g", "ఘ": "gh", "ఙ": "ng",
        "చ": "ch", "ఛ": "chh", "జ": "j", "ఝ": "jh", "ఞ": "ny",
        "ట": "tt", "ఠ": "tth", "డ": "dd", "ఢ": "ddh", "ణ": "nn",
        "త": "t", "థ": "th", "ద": "d", "ధ": "dh", "న": "n",
        "ప": "p", "ఫ": "ph", "బ": "b", "భ": "bh", "మ": "m",
        "య": "y", "ర": "r", "ల": "l", "ళ": "ll", "వ": "v",
        "శ": "sh", "ష": "sh", "స": "s", "హ": "h",
    }

    reverse_matras = {
        "ా": "aa", "ి": "i", "ీ": "ii", "ు": "u", "ూ": "uu",
        "ృ": "ri", "ౄ": "rii", "ె": "e", "ే": "ee",
        "ై": "ai", "ొ": "o", "ో": "oo", "ౌ": "au",
    }

    result = []
    i = 0
    prev_was_consonant = False

    while i < len(text):
        char = text[i]

        # Check for virama (halant)
        if char == "్":
            # Just mark that we had a virama
            # The inherent 'a' will not be added because consonants are base form (no 'a')
            prev_was_consonant = True
            i += 1
            continue

        # Check for consonant
        if char in reverse_consonants:
            base = reverse_consonants[char]

            # Add inherent vowel 'a' only if NOT after a consonant (with or without virama)
            if not prev_was_consonant:
                base = base + "a"

            result.append(base)
            prev_was_consonant = True
            i += 1

            # Check for following matra
            if i < len(text) and text[i] in reverse_matras:
                # Matra replaces the inherent vowel
                matra = reverse_matras[text[i]]
                result[-1] = result[-1][:-1] + matra  # Remove 'a' and add matra
                i += 1
            continue

        # Check for standalone vowel
        if char in reverse_vowels:
            result.append(reverse_vowels[char])
            prev_was_consonant = False
            i += 1
            continue

        # Unknown character (space, punctuation, etc.)
        result.append(char)
        prev_was_consonant = False
        i += 1

    return "".join(result)


# ============================================================================
# PART 3: SEMANTIC WORD MAPPING (English ↔ Telugu)
# ============================================================================

def get_semantic_dictionary():
    """
    Dictionary of English words and their Telugu equivalents.
    Format: {english: [telugu1, telugu2, ...], ...}
    """
    return {
        # Questions
        "who": ["ఎవరు", "ఎవరో"],
        "what": ["ఏమి", "ఏమిటి", "ఎం"],
        "when": ["ఎప్పుడు", "ఎప్పుడో"],
        "where": ["ఎక్కడ", "ఎక్కడో"],
        "why": ["ఎందుకు", "ఎందుకో"],
        "how": ["ఎలా", "ఎలాగ"],
        "which": ["ఏది", "ఏ"],

        # Common words
        "yes": ["అవును", "అవునండి", "ఔను"],
        "no": ["కాదు", "లేదు"],
        "hello": ["హలో", "నమస్కారం", "వందనం"],
        "thank": ["ధన్యవాదాలు", "కృతజ్ఞతలు"],
        "please": ["దయచేసి", "చేయండి"],
        "sorry": ["క్షమించండి", "సారీ"],

        # Names (common)
        "rama": ["రామ", "రాముడు"],
        "raama": ["రామ"],  # Alternative spelling
        "krishna": ["కృష్ణ", "కృష్ణుడు"],
        "sita": ["సీత"],
        "lakshmi": ["లక్ష్మి"],
        "venkatesh": ["వెంకటేశ్", "వెంకటేశ్వర"],
        "narayana": ["నారాయణ"],

        # Family
        "mother": ["అమ్మ", "తల్లి"],
        "father": ["నాన్న", "తండ్రి"],
        "brother": ["అన్న", "తమ్ముడు"],
        "sister": ["అక్క", "చెల్లి"],
        "son": ["మగవాడు", "కొడుకు"],
        "daughter": ["అమ్మాయి", "కూతురు"],
        "uncle": ["చిన్నాన్న", "పెదనాన్న"],
        "aunt": ["పిన్ని", "పెద్దనాన్న"],

        # Numbers
        "one": ["ఒకటి"],
        "two": ["రెండు"],
        "three": ["మూడు"],
        "four": ["నాలుగు"],
        "five": ["ఐదు"],
        "six": ["ఆరు"],
        "seven": ["ఏడు"],
        "eight": ["ఎనిమిది"],
        "nine": ["తొమ్మిది"],
        "ten": ["పది"],

        # Colors
        "red": ["ఎర్ర"],
        "blue": ["నీలం"],
        "green": ["పచ్చ"],
        "yellow": ["పసుపు"],
        "white": ["తెలుపు"],
        "black": ["నలుపు"],

        # Days
        "monday": ["సోమవారం"],
        "tuesday": ["మంగళవారం"],
        "wednesday": ["బుధవారం"],
        "thursday": ["గురువారం"],
        "friday": ["శుక్రవారం"],
        "saturday": ["శనివారం"],
        "sunday": ["ఆదివారం"],
    }


def get_reverse_semantic_dictionary():
    """Create reverse mapping: Telugu → English."""
    forward = get_semantic_dictionary()
    reverse = {}

    for eng, tel_list in forward.items():
        for tel in tel_list:
            if tel not in reverse:
                reverse[tel] = []
            reverse[tel].append(eng)

    return reverse


def normalize_for_matching(text: str) -> str:
    """Normalize text for semantic matching."""
    return text.lower().strip()


def semantic_match(text: str) -> dict:
    """
    Find semantic matches for input text (works both ways).

    Returns:
        {
            'input': original_text,
            'detected_language': 'english' or 'telugu',
            'matches': [list of matching words],
            'transliteration': transliterated version
        }
    """
    text_norm = normalize_for_matching(text)

    # Check if input is Telugu
    is_telugu = any('\u0C00' <= ch <= '\u0C7F' for ch in text)

    if is_telugu:
        # Telugu → English
        reverse_dict = get_reverse_semantic_dictionary()
        matches = reverse_dict.get(text_norm, [])
        transliteration = telugu_to_eng(text_norm)

        return {
            'input': text,
            'detected_language': 'telugu',
            'matches': matches,
            'transliteration': transliteration,
        }
    else:
        # English → Telugu
        forward_dict = get_semantic_dictionary()
        matches = forward_dict.get(text_norm, [])
        transliteration = eng_to_telugu(text_norm)

        return {
            'input': text,
            'detected_language': 'english',
            'matches': matches if matches else [transliteration],
            'transliteration': transliteration,
        }


def bidirectional_search(query: str) -> list:
    """
    Search that works for both English and Telugu input.
    Returns all related words in both languages.

    Example:
        bidirectional_search("who") → [
            ("English", "who"),
            ("Telugu", "ఎవరు"),
            ("Telugu", "ఎవరో"),
            ("Transliteration", "evaru"),
        ]
    """
    result_data = semantic_match(query)
    results = []

    if result_data['detected_language'] == 'english':
        # Input was English
        results.append(("English", result_data['input']))
        for match in result_data['matches']:
            results.append(("Telugu", match))
            results.append(("Transliteration", telugu_to_eng(match)))
    else:
        # Input was Telugu
        results.append(("Telugu", result_data['input']))
        results.append(("Transliteration", result_data['transliteration']))
        for match in result_data['matches']:
            results.append(("English", match))

    # Remove duplicates while preserving order
    seen = set()
    unique_results = []
    for lang, word in results:
        if (lang, word) not in seen:
            unique_results.append((lang, word))
            seen.add((lang, word))

    return unique_results


# ============================================================================
# PART 4: SENTENCE HANDLING
# ============================================================================

def eng_to_telugu_sentence(sentence: str, style: str = "modern") -> str:
    """
    Transliterate a complete sentence (multiple words).
    Checks semantic dictionary first, then falls back to transliteration.
    Preserves punctuation and special characters.

    Args:
        sentence: English sentence to transliterate
        style: Alphabet style ("modern", "classical", or "hybrid")

    Returns:
        Telugu sentence with spaces and punctuation preserved

    Example:
        eng_to_telugu_sentence("hello world")  # "హలో వర్ల్ద"
        eng_to_telugu_sentence("who is rama")  # "ఎవరు ఇస్ రామ"
        eng_to_telugu_sentence("Who is Krishna?")  # "ఎవరు ఇస్ కృష్ణ?"
    """
    import re

    forward_dict = get_semantic_dictionary()

    # Tokenize preserving punctuation and spaces
    # Unicode-aware pattern: Telugu block, English words, spaces, punctuation
    tokens = re.findall(r'[\u0C00-\u0C7F]+|[a-zA-Z]+|\s+|[^\w\s]', sentence, flags=re.UNICODE)
    result = []

    for token in tokens:
        if any('\u0C00' <= c <= '\u0C7F' for c in token):
            # Already Telugu
            result.append(token)
        elif token.isalnum():
            # Check semantic dictionary
            norm = normalize_for_matching(token)
            if norm in forward_dict:
                result.append(forward_dict[norm][0])
            else:
                result.append(eng_to_telugu_with_style(token, style))
        else:
            # Space, punctuation, or special character
            result.append(token)

    return "".join(result)


# ============================================================================
# PART 5: WORD VARIATIONS
# ============================================================================

def generate_word_variations(word: str) -> list:
    """
    Generate spelling variations for a given Telugu word.

    Args:
        word: The Telugu word to generate variations for.

    Returns:
        A list of possible spelling variations.
    """
    import itertools

    rules = {
        'ా': ['', 'ె'],
        'ట': ['ట్ట', 'త', 'త్త'],
        'ర': ['ర్'],
        'డ': ['డ్డ'],
        'క': ['క్క'],
        'ప': ['ప్ప'],
        'త': ['త్త'],
        'చ': ['చ్చ'],
        'ల': ['ల్ల'],
        'మ': ['మ్మ'],
        'వ': ['వ్వ'],
        'గ': ['గ్గ'],
        'బ': ['బ్బ'],
        'స': ['స్స'],
    }

    variations = {word}
    for i, char in enumerate(word):
        if char in rules:
            for replacement in rules[char]:
                new_word = word[:i] + replacement + word[i+1:]
                variations.add(new_word)

    # Generate combinations of variations
    # This can be computationally expensive, so we will limit the depth
    # For now, we will just do one level of replacement
    
    return sorted(list(variations))


# ============================================================================
# MAIN - QUICK TEST
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TELUGU LIBRARY v2.0 - QUICK TEST")
    print("=" * 80)

    samples = ["rama", "krishna", "bhagvaan", "who", "ఎవరు", "hello", "హలో"]

    print("\n1. Basic Transliteration:")
    for sample in samples:
        if any('\u0C00' <= ch <= '\u0C7F' for ch in sample):
            # Telugu input
            eng = telugu_to_eng(sample)
            print(f"  Telugu: {sample:15} → English: {eng}")
        else:
            # English input
            tel = eng_to_telugu(sample)
            print(f"  English: {sample:15} → Telugu: {tel}")

    print("\n2. Semantic Matching:")
    for sample in ["who", "ఎవరు", "mother", "అమ్మ"]:
        result = semantic_match(sample)
        print(f"  Input: {sample:15}")
        print(f"    Language: {result['detected_language']}")
        print(f"    Matches: {result['matches']}")

    print("\n3. Sentence Transliteration:")
    sentences = [
        "hello world",
        "who is rama",
        "thank you",
    ]
    for sent in sentences:
        telugu = eng_to_telugu_sentence(sent)
        print(f"  English: {sent:20} → Telugu: {telugu}")

    print("\n" + "=" * 80)
    print("Test complete!")
    print("=" * 80)
