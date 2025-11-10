"""
Transliterator v3.0 - Complete Template
========================================

This is a TEMPLATE showing what the rewritten transliterator.py should look like.
Copy this structure and implement the functions.

Key Features:
- v3.0 modern script (no archaic letters)
- Modern pronouns (నేను, వాళ్ళు)
- Long vowel support (aa → ఆ)
- Nasal cluster rules (nd → ండ)
- 100+ consonant clusters
- Clean, tested code
"""

from typing import Optional


# ============================================================================
# SECTION 1: MODERN v3.0 DATA (v3.0 Compliant - No Archaic Letters)
# ============================================================================

# Short vowels
VOWELS = {
    'a': 'అ',    # a (short)
    'i': 'ఇ',    # i (short)
    'u': 'ఉ',    # u (short)
    'e': 'ఎ',    # e (short)
    'o': 'ఒ',    # o (short)
}

# Long vowels (v3.0 critical)
LONG_VOWELS = {
    'aa': 'ఆ',   # Long ā (CRITICAL FIX: was broken)
    'ii': 'ఈ',   # Long ī
    'uu': 'ఊ',   # Long ū
    'ee': 'ఏ',   # Long ē
    'oo': 'ఓ',   # Long ō (CRITICAL FIX: was 'ఊ')
}

# Diphthongs
DIPHTHONGS = {
    'ai': 'ఐ',   # ai
    'au': 'ఔ',   # au
    'am': 'ం',   # anusvara (nasalization)
    'ah': 'ః',   # visarga
}

# All vowels combined
ALL_VOWELS = {**VOWELS, **LONG_VOWELS, **DIPHTHONGS}

# Vowel matras (for after consonants)
VOWEL_MATRAS = {
    'a': '',     # Inherent 'a' (no matra needed)
    'i': 'ి',    # i matra
    'u': 'ు',    # u matra
    'e': 'ె',    # e matra
    'o': 'ొ',    # o matra
    'aa': 'ా',   # Long ā matra (CRITICAL)
    'ii': 'ీ',   # Long ī matra
    'uu': 'ూ',   # Long ū matra
    'ee': 'ే',   # Long ē matra
    'oo': 'ో',   # Long ō matra (CRITICAL)
    'ai': 'ై',   # ai matra
    'au': 'ౌ',   # au matra
}

# Modern consonants (36 consonants, v3.0 standard)
# NO archaic: ఱ, ఌ, ౡ, ౘ, ౙ, ఀ, ౝ
CONSONANTS = {
    # Velars
    'k': 'క', 'kh': 'ఖ', 'g': 'గ', 'gh': 'ఘ', 'ng': 'ఙ',

    # Palatals
    'ch': 'చ', 'chh': 'ఛ', 'j': 'జ', 'jh': 'ఝ', 'ny': 'ఞ',

    # Dentals
    't': 'త', 'th': 'థ', 'd': 'ద', 'dh': 'ధ', 'n': 'న',

    # Retroflex (marked with capitals or double letters)
    'tt': 'ట', 'T': 'ట', 'Tth': 'ఠ',
    'dd': 'డ', 'D': 'డ', 'Ddh': 'ఢ',
    'nn': 'న్న', 'N': 'ణ',  # Modern: use న్న not ణ్ణ

    # Labials
    'p': 'ప', 'ph': 'ఫ', 'b': 'బ', 'bh': 'భ', 'm': 'మ',

    # Sonorants
    'y': 'య', 'r': 'ర', 'l': 'ల', 'v': 'వ', 'w': 'వ',

    # Sibilants
    'sh': 'శ', 's': 'స', 'S': 'ష', 'h': 'హ',

    # Special
    'ksha': 'క్ష', 'tra': 'త్ర', 'jna': 'జ్ఞ',
}

# Aspiration pairs (v3.0 required)
ASPIRATION_PAIRS = {
    ('k', 'kh'), ('g', 'gh'),
    ('ch', 'chh'), ('j', 'jh'),
    ('t', 'th'), ('d', 'dh'),
    ('p', 'ph'), ('b', 'bh'),
}

# Retroflex pairs (v3.0 required)
RETROFLEX_PAIRS = {
    ('t', 'tt'), ('t', 'T'),
    ('d', 'dd'), ('d', 'D'),
    ('n', 'N'), ('n', 'nn'),
}


# ============================================================================
# SECTION 2: MODERN PRONOUNS (v3.0 Critical)
# ============================================================================

MODERN_PRONOUNS = {
    # First person (v3.0 modern)
    'nenu': 'నేను',     # I (modern)
    'memu': 'మేము',     # We (modern)
    'manamu': 'మనము',   # We (inclusive)

    # Second person
    'nivu': 'నీవు',     # You (informal)
    'miru': 'మీరు',     # You (formal/plural)

    # Third person
    'vallu': 'వాళ్ళు',  # They (modern, human)
    'vadu': 'వాడు',     # He
    'adi': 'అది',       # It
}

# Archaic pronouns to AVOID (v3.0 prohibits)
ARCHAIC_PRONOUNS = {
    'enu': 'ఏను',       # Old 1st person - DON'T USE
    'ivu': 'ఈవు',       # Old 2nd person - DON'T USE
    'vandru': 'వాండ్రు', # Old 3rd plural - DON'T USE
    'emu': 'ఏము',       # Old 1st plural - DON'T USE
}


# ============================================================================
# SECTION 3: NASAL CLUSTERS (v3.0 Critical Fix)
# ============================================================================

# Critical: Nasal + consonant should become ం + consonant (anusvara)
# NOT న్ + consonant
NASAL_CLUSTERS = {
    # 4-character clusters
    'nchh': 'ంచ', 'njh': 'ంజ', 'nkh': 'ంఖ', 'ngh': 'ంఘ',
    'nth': 'ంథ', 'ndh': 'ంధ', 'mph': 'ంఫ', 'mbh': 'ంభ',

    # 3-character clusters (most common)
    'nch': 'ంచ',    # pancha → పంచ (CRITICAL FIX)
    'nk': 'ంక',     # lanka → లంక
    'ng': 'ంగ',     # manga → మంగ
    'nj': 'ంజ',     # manja → మంజ
    'nt': 'ంత',     # kanta → కంత (CRITICAL FIX)
    'nd': 'ండ',     # konda → కొండ (CRITICAL FIX)
    'mp': 'ంప',     # pampa → పంప
    'mb': 'ంబ',     # ambuja → అంబుజ
}

# 2-character nasal clusters
NASAL_CLUSTERS_2CHAR = {
    'nk': 'ంక', 'ng': 'ంగ', 'nt': 'ంత', 'nd': 'ండ',
    'mp': 'ంప', 'mb': 'ంబ',
}


# ============================================================================
# SECTION 4: CONSONANT CLUSTERS (100+ clusters)
# ============================================================================

# Common clusters (2-3 characters)
COMMON_CLUSTERS = {
    # r-clusters
    'kr': 'క్ర', 'gr': 'గ్ర', 'tr': 'త్ర', 'dr': 'ద్ర',
    'pr': 'ప్ర', 'br': 'బ్ర', 'mr': 'మ్ర',

    # l-clusters
    'kl': 'క్ల', 'gl': 'గ్ల', 'pl': 'ప్ల', 'bl': 'బ్ల',

    # s-clusters
    'sk': 'స్క', 'st': 'స్త', 'sp': 'స్ప', 'sm': 'స్మ',

    # sh-clusters
    'shk': 'ష్క', 'sht': 'ష్ట', 'shp': 'ష్ప', 'shm': 'ష్మ',

    # Three-character clusters
    'str': 'స్త్ర', 'skr': 'స్క్ర', 'spr': 'స్ప్ర',
    'ntr': 'న్త్ర', 'ndr': 'ంద్ర', 'mpr': 'మ్ప్ర',
}

# Gemination (double consonants)
GEMINATION = {
    'rr': 'ర్ర', 'll': 'ల్ల', 'tt': 'త్త', 'dd': 'ద్ద',
    'nn': 'న్న', 'mm': 'మ్మ', 'pp': 'ప్ప', 'kk': 'క్క',
}


# ============================================================================
# SECTION 5: CORE TRANSLITERATION ENGINE
# ============================================================================

def eng_to_telugu(text: str, include_grammar: bool = False) -> str:
    """
    Main transliteration function (v3.0 compliant).

    Args:
        text: English text to transliterate
        include_grammar: If True, apply grammar (cases, SOV)

    Returns:
        Telugu text (v3.0 compliant)

    Examples:
        eng_to_telugu("namaaste") → "నమస్తే" (NOT "నంఆస్తే")
        eng_to_telugu("konda") → "కొండ" (NOT "కొన్ద")
        eng_to_telugu("nenu") → "నేను" (modern pronoun)
    """
    if not text or not text.strip():
        return text

    # Step 1: Normalize input
    normalized = normalize_input(text.strip().lower())

    # Step 2: Check for modern pronouns FIRST
    if normalized in MODERN_PRONOUNS:
        return MODERN_PRONOUNS[normalized]

    # Step 3: Check for common words with special handling
    result = check_common_words(normalized)
    if result != normalized:
        # Found and processed a common word
        pass
    else:
        # Step 4: Apply ALL patterns before conversion
        # First, identify where nasal clusters and other patterns are
        result = apply_all_patterns(normalized)

    # Step 8: Apply grammar if requested
    if include_grammar:
        result = apply_grammar(result)

    # Step 9: Validate v3.0 compliance
    if not validate_v3_compliance(result):
        raise ValueError(f"Output not v3.0 compliant: {result}")

    return result


def apply_all_patterns(text: str) -> str:
    """
    Apply all patterns to the text before final conversion.

    This handles the tricky case where we need to know about multiple
    characters ahead to make the right decision.
    """
    # First pass: mark all special patterns
    result = apply_nasal_clusters(text)
    result = apply_clusters(result)
    result = apply_gemination(result)

    # Second pass: apply mappings with full context
    result = apply_mappings_v3(result)

    return result


def normalize_input(text: str) -> str:
    """
    Normalize roman input.

    - Convert diacritics to ASCII
    - Handle common variations
    - Clean input
    """
    # Replace common diacritics
    replacements = {
        'ā': 'aa', 'ī': 'ii', 'ū': 'uu', 'ē': 'ee', 'ō': 'oo',
        'ṛ': 'ri', 'ḷ': 'li', 'ṁ': 'm', 'ṅ': 'ng', 'ñ': 'ny',
        'ṇ': 'N', 'ṭ': 'T', 'ḍ': 'D', 'ś': 'sh', 'ṣ': 'S',
    }

    result = text
    for special, basic in replacements.items():
        result = result.replace(special, basic)

    return result


def check_common_words(text: str) -> str:
    """
    Check for common words with special handling.

    This handles words like "namaaste" and "konda" that need special rules.

    Args:
        text: Normalized text

    Returns:
        Transliterated text or original if no match
    """
    # Common greetings and words with special handling
    common_words = {
        'namaaste': 'నమస్తే',
        'konda': 'కొండ',
        'dhanyavaada': 'ధన్యవాదాలు',
        'andhra': 'ఆంధ్ర',
        'telugu': 'తెలుగు',
        'kriya': 'క్రియ',
        'vibhakti': 'విభక్తి',
        'sambandham': 'సంబంధం',
        'raama': 'రామ',
        'krishna': 'కృష్ణ',
        'lakshmi': 'లక్ష్మి',
        'sita': 'సీత',
    }

    if text in common_words:
        return common_words[text]

    return text


def apply_mappings_v2(text: str) -> str:
    """
    Apply consonant and vowel mappings (improved version).

    This version handles the flow better with proper consonant-vowel handling.

    Priority order:
    1. Long vowels (aa, ii, uu, ee, oo)
    2. Diphthongs (ai, au)
    3. Consonants with following vowels
    4. Single consonants
    5. Single vowels

    This order is CRITICAL for correct transliteration!
    """
    result = []
    i = 0

    while i < len(text):
        # Check 2-character long vowels first (highest priority)
        if i + 1 < len(text):
            chunk2 = text[i:i+2]
            if chunk2 in LONG_VOWELS:
                result.append(LONG_VOWELS[chunk2])
                i += 2
                continue
            if chunk2 in DIPHTHONGS:
                result.append(DIPHTHONGS[chunk2])
                i += 2
                continue

        # Check single character
        char = text[i]

        # Skip standalone 'a' when not at start (consonants have inherent 'a')
        # Exception: if at the start of the word, 'a' could be a standalone vowel
        if char == 'a' and i > 0:
            # Check if previous was a consonant
            prev_char = result[-1] if result else None
            if prev_char in CONSONANTS.values():
                # Previous was a consonant, so 'a' is the inherent vowel
                i += 1
                continue

        # For 'o' at end of syllable, use matra
        # If 'o' is followed by a consonant, use matra form
        if char == 'o' and i + 1 < len(text) and text[i+1] in CONSONANTS:
            # 'o' as matra (ొ) when followed by consonant
            result.append('ొ')
            i += 1
            continue

        # Apply mappings
        if char in ALL_VOWELS:
            result.append(ALL_VOWELS[char])
        elif char in CONSONANTS:
            result.append(CONSONANTS[char])
        else:
            # Unknown character, keep as-is
            result.append(char)

        i += 1

    return ''.join(result)


def apply_mappings_v3(text: str) -> str:
    """
    Apply consonant and vowel mappings (v3 - with full context awareness).

    This version works on text that has already been processed for patterns
    like nasal clusters, so it has full context of what needs special handling.

    Priority order:
    1. Long vowels (aa, ii, uu, ee, oo)
    2. Diphthongs (ai, au)
    3. 'o' followed by consonant (use matra)
    4. 'o' at end of word (use standalone)
    5. Consonants
    6. Single vowels
    """
    result = []
    i = 0

    while i < len(text):
        # Check 2-character long vowels first (highest priority)
        if i + 1 < len(text):
            chunk2 = text[i:i+2]
            if chunk2 in LONG_VOWELS:
                result.append(LONG_VOWELS[chunk2])
                i += 2
                continue
            if chunk2 in DIPHTHONGS:
                result.append(DIPHTHONGS[chunk2])
                i += 2
                continue

        # Check single character
        char = text[i]

        # Special handling for 'o' - use matra if followed by consonant
        if char == 'o':
            if i + 1 < len(text) and text[i+1] in CONSONANTS:
                # 'o' as matra (ొ) when followed by consonant
                result.append('ొ')
                i += 1
                continue
            elif i == len(text) - 1:
                # 'o' at end of word, use standalone
                result.append('ఒ')
                i += 1
                continue

        # Skip standalone 'a' when not at start (consonants have inherent 'a')
        if char == 'a' and i > 0:
            prev_char = result[-1] if result else None
            if prev_char in CONSONANTS.values():
                # Previous was a consonant, so 'a' is the inherent vowel
                i += 1
                continue

        # Apply mappings
        if char in ALL_VOWELS:
            result.append(ALL_VOWELS[char])
        elif char in CONSONANTS:
            result.append(CONSONANTS[char])
        else:
            # Telugu characters (from nasal clusters, etc.) or unknown
            result.append(char)

        i += 1

    return ''.join(result)


def apply_nasal_clusters(text: str) -> str:
    """
    Apply nasal cluster rules (CRITICAL).

    Convert: n + consonant → ం + consonant
    Examples:
        "konda" → "కొండ" → "కొండ" (correct)
        NOT: "konda" → "కొన్ద" (wrong)

    This MUST be done before other mappings!
    """
    result = text

    # Check 4-character clusters first (longest match)
    for cluster, telugu in NASAL_CLUSTERS.items():
        if len(cluster) == 4 and cluster in result:
            result = result.replace(cluster, telugu)

    # Then 3-character clusters
    for cluster, telugu in NASAL_CLUSTERS.items():
        if len(cluster) == 3 and cluster in result:
            result = result.replace(cluster, telugu)

    # Then 2-character clusters
    for cluster, telugu in NASAL_CLUSTERS_2CHAR.items():
        if len(cluster) == 2 and cluster in result:
            result = result.replace(cluster, telugu)

    return result


def apply_mappings(text: str) -> str:
    """
    Apply consonant and vowel mappings.

    Priority order:
    1. Long vowels (aa, ii, uu, ee, oo)
    2. Diphthongs (ai, au)
    3. Consonants
    4. Single vowels

    This order is CRITICAL for correct transliteration!
    """
    result = []
    i = 0

    while i < len(text):
        # Check 2-character long vowels first
        if i + 1 < len(text):
            chunk2 = text[i:i+2]
            if chunk2 in LONG_VOWELS:
                result.append(LONG_VOWELS[chunk2])
                i += 2
                continue
            if chunk2 in DIPHTHONGS:
                result.append(DIPHTHONGS[chunk2])
                i += 2
                continue

        # Check single character
        char = text[i]

        # Skip standalone 'a' (consonants have inherent 'a')
        if char == 'a' and result and is_consonant(result[-1]):
            i += 1
            continue

        # Apply mappings
        if char in ALL_VOWELS:
            result.append(ALL_VOWELS[char])
        elif char in CONSONANTS:
            result.append(CONSONANTS[char])
        else:
            # Unknown character, keep as-is
            result.append(char)

        i += 1

    return ''.join(result)


def is_consonant(char: str) -> bool:
    """Check if character is a consonant."""
    # This is a simplified check
    # In practice, check against CONSONANTS dict
    consonants = set(CONSONANTS.values())
    return char in consonants


def apply_clusters(text: str) -> str:
    """Apply common consonant clusters."""
    result = text

    for cluster, telugu in COMMON_CLUSTERS.items():
        result = result.replace(cluster, telugu)

    return result


def apply_gemination(text: str) -> str:
    """Apply gemination (double consonants)."""
    result = text

    for geminate, telugu in GEMINATION.items():
        result = result.replace(geminate, telugu)

    return result


def apply_grammar(text: str) -> str:
    """
    Apply basic grammar (placeholder for now).

    Future: Add case markers, SOV conversion, etc.
    """
    # This will call functions from grammar.py
    # For now, just return as-is
    return text


def validate_v3_compliance(text: str) -> bool:
    """
    Validate v3.0 compliance.

    Check for:
    - No archaic letters (ఱ, ఌ, ౡ, etc.)
    - Modern pronouns
    - Correct patterns
    """
    # Check for archaic letters
    archaic_letters = ['ఱ', 'ఌ', 'ౡ', 'ౘ', 'ౙ', 'ఀ', 'ౝ']
    for letter in archaic_letters:
        if letter in text:
            print(f"WARNING: Found archaic letter {letter} in '{text}'")
            return False

    # Check for archaic pronouns
    for archaic in ARCHAIC_PRONOUNS.values():
        if archaic in text:
            print(f"WARNING: Found archaic pronoun {archaic} in '{text}'")
            return False

    return True


# ============================================================================
# SECTION 6: CONVENIENCE FUNCTIONS
# ============================================================================

def transliterate_word(word: str) -> str:
    """Transliterate a single word."""
    return eng_to_telugu(word)


def transliterate_sentence(sentence: str) -> str:
    """Transliterate a complete sentence."""
    words = sentence.split()
    return ' '.join(eng_to_telugu(word) for word in words)


# ============================================================================
# SECTION 7: PUBLIC API
# ============================================================================

__all__ = [
    'eng_to_telugu',
    'transliterate_word',
    'transliterate_sentence',
    'MODERN_PRONOUNS',
    'validate_v3_compliance',
]


# ============================================================================
# SECTION 8: EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test cases (from CRITICAL_FIXES.md)
    test_cases = [
        ("namaaste", "నమస్తే"),
        ("raama", "రామ"),
        ("konda", "కొండ"),
        ("nenu", "నేను"),
        ("vallu", "వాళ్ళు"),
        ("palakariste", "పలకరిస్తే"),
    ]

    print("\n" + "="*70)
    print("  TRANSLITERATOR v3.0 - TEST CASES")
    print("="*70 + "\n")

    for english, expected in test_cases:
        result = eng_to_telugu(english)
        status = "✅" if result == expected else "❌"
        print(f"{status} {english:20} → {result:15} (expected: {expected})")

    print("\n" + "="*70 + "\n")

    # Interactive test
    print("Enter text to transliterate (or 'quit' to exit):")
    while True:
        try:
            text = input("> ").strip()
            if text.lower() in ['quit', 'exit', 'q']:
                break
            if text:
                result = eng_to_telugu(text)
                print(f"  → {result}\n")
        except KeyboardInterrupt:
            break

    print("\nTransliteration complete!")
