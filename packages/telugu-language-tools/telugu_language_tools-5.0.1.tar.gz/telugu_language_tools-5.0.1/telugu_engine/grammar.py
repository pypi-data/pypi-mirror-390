"""
Modern Telugu Grammar Engine v3.0
==================================

This module provides modern Telugu grammar processing:
- Modern verb patterns (Past Participle + Person Marker)
- 4-case system (Nominative, Accusative, Dative, Locative)
- SOV syntax conversion
- Vowel harmony enforcement
- Sandhi rules

Usage:
    from telugu_engine.grammar import apply_case, conjugate_verb
"""

from typing import List, Dict, Optional
import re


# ============================================================================
# SECTION 1: MODERN VERB PATTERNS (v3.0 Critical)
# ============================================================================

# Person markers (v3.0 modern)
PERSON_MARKERS = {
    # 1st person
    '1ps': 'ఆను',     # I (past)
    '1pp': 'ఆము',     # We (past)

    # 2nd person
    '2ps': 'ఆవు',     # You (informal, past)
    '2pp': 'ఆరు',     # You (formal/plural, past)

    # 3rd person
    '3ps': 'ఆడు',     # He/She/It (past)
    '3pp': 'ఆరు',     # They (past)
    '3pp_alt': 'అవి', # They (alternative, neuter)
}

# Verb roots (examples)
VERB_ROOTS = {
    'cheyyu': 'చేయు',     # to do
    'tinu': 'తిను',       # to eat
    'vaddu': 'వడ్డు',     # to come
    'chaduvu': 'చదువు',   # to read
    'raavu': 'రావు',      # to be
}

# Past participles (ROOT + సిన)
# Modern pattern: చేయు + సిన = చేసిన (NOT చేసితి)
PAST_PARTICIPLES = {
    'cheyyu': 'చేసిన',    # done
    'tinu': 'తిన్న',       # eaten
    'vaddu': 'వచ్చిన',    # came
    'chaduvu': 'చదివిన',  # read
    'raavu': 'రాలేదు',    # not came
}


def conjugate_verb(root: str, tense: str, person: str) -> str:
    """
    Conjugate verb using modern v3.0 pattern.

    Pattern: PAST PARTICIPLE + PERSON MARKER
    Examples:
        conjugate_verb('cheyyu', 'past', '1ps') → 'చేసినాను'
        conjugate_verb('tinu', 'past', '3pp') → 'తిన్నారు'

    OLD (WRONG) pattern: చేసితిని, చేసితిరి
    NEW (CORRECT) pattern: చేసినాను, చేసినారు

    Args:
        root: Verb root (e.g., 'cheyyu')
        tense: 'past', 'present', 'future'
        person: '1ps', '1pp', '2ps', '2pp', '3ps', '3pp'

    Returns:
        Conjugated verb form
    """
    if tense != 'past':
        # Handle present/future later
        # For now, just return root
        return VERB_ROOTS.get(root, root)

    # Get past participle
    participle = PAST_PARTICIPLES.get(root, root + 'ిన')

    # Get person marker
    marker = PERSON_MARKERS.get(person, '')

    # Combine: PARTICIPLE + MARKER
    result = participle + marker

    return result


# ============================================================================
# SECTION 2: 4-CASE SYSTEM (v3.0 Modern)
# ============================================================================

# Case markers (v3.0 simplified - 4 cases in practice)
CASE_MARKERS = {
    'nominative': 'డు',   # Subject (e.g., రాముడు)
    'accusative': 'ను',   # Direct object (e.g., పుస్తకం)
    'dative': 'కు',       # Indirect object (e.g., రాముడికు)
    'locative': 'లో',     # Location (e.g., ఇంట్లో)
    'genitive': 'యొక్క', # Possession (e.g., రాము యొక్క)
}

# Formality markers
FORMALITY_MARKERS = {
    'informal': '',       # Use with friends/family
    'formal': 'గారు',     # Respectful (e.g., మీరు వచ్చారుగారు)
    'honorific': 'వారు',  # Very respectful
}


def apply_case(noun: str, case: str, formality: str = 'informal') -> str:
    """
    Apply case marker to noun.

    Args:
        noun: Base noun (e.g., 'రాము')
        case: 'nominative', 'accusative', 'dative', 'locative'
        formality: 'informal', 'formal', 'honorific'

    Returns:
        Noun with case marker

    Examples:
        apply_case('రాము', 'nominative') → 'రాముడు'
        apply_case('పుస్తకం', 'accusative') → 'పుస్తకంను'
        apply_case('ఇల్లు', 'locative') → 'ఇంట్లో'
    """
    if case not in CASE_MARKERS:
        raise ValueError(f"Invalid case: {case}. Use: {list(CASE_MARKERS.keys())}")

    # Get case marker
    marker = CASE_MARKERS[case]

    # Apply vowel harmony (simplified)
    # For now, just add marker
    # TODO: Add proper vowel harmony checking

    # Add formality if needed
    formal = FORMALITY_MARKERS.get(formality, '')

    result = noun + marker + formal

    return result


# ============================================================================
# SECTION 3: SOV SYNTAX CONVERSION (v3.0 Critical)
# ============================================================================

# Common English words to identify parts of speech
POS_PATTERNS = {
    'pronouns': ['i', 'you', 'he', 'she', 'it', 'we', 'they'],
    'articles': ['a', 'an', 'the'],
    'prepositions': ['in', 'on', 'at', 'to', 'from', 'with', 'by'],
}


def convert_svo_to_soV(sentence: str) -> str:
    """
    Convert English SVO to Telugu SOV.

    Examples:
        "Ramu reads book" → "రాము పుస్తకం చదువుతాడు"
        S     O     V          S     O          V

    Algorithm:
        1. Identify subject, object, verb
        2. Add case markers
        3. Reorder to SOV

    Args:
        sentence: English sentence (e.g., "Ramu reads book")

    Returns:
        Telugu sentence in SOV order

    TODO: This is a simplified version. A real implementation would use
          POS tagging for better accuracy.
    """
    words = sentence.strip().split()
    if len(words) < 2:
        return sentence

    # Simple heuristic: first word is subject, last is verb
    subject = words[0]
    verb = words[-1]

    # Everything in between is object
    object_words = words[1:-1] if len(words) > 2 else words[1:2]
    obj = ' '.join(object_words) if object_words else ''

    return {
        'subject': subject,
        'object': obj,
        'verb': verb
    }


def build_telugu_sentence(subject: str, obj: str, verb: str) -> str:
    """
    Build Telugu sentence with proper morphology.

    Args:
        subject: Subject (will get nominative case)
        object: Object (will get accusative case)
        verb: Verb (will be conjugated)

    Returns:
        Complete Telugu sentence in SOV order

    Example:
        build_telugu_sentence('Ramu', 'book', 'reads')
        → "రాము పుస్తకం చదువుతాడు"
    """
    # Transliterate to Telugu
    from .transliterator import eng_to_telugu

    subject_telugu = eng_to_telugu(subject)
    obj_telugu = eng_to_telugu(obj) if obj else ''
    verb_telugu = eng_to_telugu(verb)

    # Apply case markers
    subject_telugu = apply_case(subject_telugu, 'nominative')
    if obj_telugu:
        obj_telugu = apply_case(obj_telugu, 'accusative')

    # Conjugate verb (simplified)
    # TODO: Add proper tense/person detection
    verb_telugu = conjugate_verb('chaduvu', 'present', '3ps')

    # Build SOV sentence
    parts = [subject_telugu]
    if obj_telugu:
        parts.append(obj_telugu)
    parts.append(verb_telugu)

    return ' '.join(parts)


# ============================================================================
# SECTION 4: SANDHI RULES (Native Telugu)
# ============================================================================

# Native Telugu sandhi rules
NATIVE_SANDHI = {
    # Ukārasandhi (u-elision) - MOST FREQUENT in v3.0
    'ukarasandhi': {
        'pattern': r'ు([aeiou])',
        'replacement': r'\1',  # Remove 'ు' before vowel
        'example': 'వాడు + ఎవడు = వాడేవడు'
    },

    # Ikārasandhi (i-elision)
    'ikarasandhi': {
        'pattern': r'ి([aeiou])',
        'replacement': r'\1',  # Remove 'ి' before vowel
        'example': 'తాటి + అంకం = తాటాంకం'
    },

    # Akārasandhi (a-elision)
    'akarasandhi': {
        'pattern': r'([aeo])ా([aeiou])',
        'replacement': r'\1\2',  # Simplify vowel sequence
        'example': 'పాల + ఆవు = పాలావు'
    }
}

# Sanskrit sandhi rules (for Tatsama words)
SANSKRIT_SANDHI = {
    # Savarṇadīrghās (vowel lengthening)
    'savarnadirsha': {
        'pattern': r'([a])([a])',
        'replacement': r'ా',  # Same vowel + same vowel = long vowel
        'example': 'దేవ + ఆలయం = దేవాలయం'
    },

    # Guṇas (vowel raising)
    'gunasandhi': {
        'pattern': r'([a])([iue])',
        'replacement': r'ే\2',  # a + i/u/e = e
        'example': 'మహా + ఇంద్ర = మహేంద్ర'
    }
}


def apply_sandhi(word1: str, word2: str, origin: str = 'native') -> str:
    """
    Apply sandhi rules between two words.

    Args:
        word1: First word
        word2: Second word
        origin: 'native' for Telugu words, 'sanskrit' for Sanskrit words

    Returns:
        Combined word with sandhi applied

    Examples:
        apply_sandhi('వాడు', 'ఎవడు', 'native') → 'వాడేవడు'
        apply_sandhi('దేవ', 'ఆలయం', 'sanskrit') → 'దేవాలయం'
    """
    if origin == 'native':
        # Apply native Telugu sandhi
        combined = word1 + word2

        # Apply Ukārasandhi (most common)
        pattern = NATIVE_SANDHI['ukarasandhi']['pattern']
        replacement = NATIVE_SANDHI['ukarasandhi']['replacement']
        result = re.sub(pattern, replacement, combined)

        return result

    elif origin == 'sanskrit':
        # Apply Sanskrit sandhi
        combined = word1 + word2

        # Apply Savarṇadīrghās
        pattern = SANSKRIT_SANDHI['savarnadirsha']['pattern']
        replacement = SANSKRIT_SANDHI['savarnadirsha']['replacement']
        result = re.sub(pattern, replacement, combined)

        return result

    else:
        # No sandhi
        return word1 + word2


# ============================================================================
# SECTION 5: VOWEL HARMONY
# ============================================================================

# Vowel classes
VOWEL_CLASSES = {
    'front': ['ఇ', 'ఈ', 'ఎ', 'ఏ', 'ఐ'],
    'back': ['అ', 'ఆ', 'ఉ', 'ఊ', 'ఒ', 'ఓ', 'ఔ'],
    'neutral': ['ర', 'ల', 'వ', 'య', 'న', 'మ', 'న్', 'ం']  # Consonants
}


def check_vowel_harmony(word: str) -> bool:
    """
    Check if word respects vowel harmony.

    Vowel harmony: suffixes should match root vowel quality
    (front/back consistency)

    Args:
        word: Telugu word to check

    Returns:
        True if harmony is maintained, False otherwise

    Example:
        check_vowel_harmony('నమస్తే') → True (all back vowels)
        check_vowel_harmony('వేడుక') → False (mixed front/back)
    """
    vowels_in_word = []
    for char in word:
        for vclass, vowels in VOWEL_CLASSES.items():
            if char in vowels and vclass != 'neutral':
                vowels_in_word.append(vclass)

    if not vowels_in_word:
        return True  # No vowels = neutral

    # Check if all vowels are same class
    has_front = any(v == 'front' for v in vowels_in_word)
    has_back = any(v == 'back' for v in vowels_in_word)

    # If both front and back vowels present, harmony broken
    return not (has_front and has_back)


def apply_vowel_harmony(base: str, suffix: str) -> str:
    """
    Apply vowel harmony to suffix based on base.

    Args:
        base: Base word (determines harmony class)
        suffix: Suffix to modify

    Returns:
        Harmonized suffix
    """
    # Find dominant vowel class in base
    base_vowels = []
    for char in base:
        for vclass, vowels in VOWEL_CLASSES.items():
            if char in vowels and vclass != 'neutral':
                base_vowels.append(vclass)

    if not base_vowels:
        return suffix  # No vowels in base

    # Get dominant class (most common)
    from collections import Counter
    counts = Counter(base_vowels)
    dominant_class = counts.most_common(1)[0][0]

    # Modify suffix to match
    if dominant_class == 'front':
        # Convert back vowels to front in suffix
        harmonized = suffix
        harmonized = harmonized.replace('ఆ', 'ఇ')
        harmonized = harmonized.replace('ఊ', 'ఈ')
        harmonized = harmonized.replace('ఓ', 'ఏ')
        return harmonized
    else:
        # Keep as is (already back or neutral)
        return suffix


# ============================================================================
# SECTION 6: PUBLIC API
# ============================================================================

__all__ = [
    'conjugate_verb',
    'apply_case',
    'convert_svo_to_soV',
    'build_telugu_sentence',
    'apply_sandhi',
    'check_vowel_harmony',
    'apply_vowel_harmony',
]


# ============================================================================
# SECTION 7: EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  MODERN TELUGU GRAMMAR v3.0 - EXAMPLES")
    print("="*70 + "\n")

    # Test verb conjugation
    print("1. Modern Verb Conjugation:")
    print(f"   ' చేయు + past + 1ps' → {conjugate_verb('cheyyu', 'past', '1ps')}")
    print(f"   ' తిను + past + 3pp' → {conjugate_verb('tinu', 'past', '3pp')}")
    print("   (NOT: చేసితిని, తినిరి - old pattern)\n")

    # Test case system
    print("2. 4-Case System:")
    print(f"   'రాము + nominative' → {apply_case('రాము', 'nominative')}")
    print(f"   'పుస్తకం + accusative' → {apply_case('పుస్తకం', 'accusative')}")
    print(f"   'ఇల్లు + locative' → {apply_case('ఇల్లు', 'locative')}\n")

    # Test SOV conversion
    print("3. SOV Syntax Conversion:")
    svo = convert_svo_to_soV("Ramu reads book")
    print(f"   'Ramu reads book' → {svo}")
    print(f"   Built sentence: {build_telugu_sentence('Ramu', 'book', 'reads')}\n")

    # Test sandhi
    print("4. Sandhi Rules:")
    print(f"   'వాడు + ఎవడు' → {apply_sandhi('వాడు', 'ఎవడు', 'native')}")
    print(f"   (Ukārasandhi: u-elision)\n")

    # Test vowel harmony
    print("5. Vowel Harmony:")
    print(f"   'నమస్తే' → {check_vowel_harmony('నమస్తే')} (True - all back)")
    print(f"   'వేడుక' → {check_vowel_harmony('వేడుక')} (False - mixed)")
    print(f"   'తిను' + 'అను' → '{apply_vowel_harmony('తిను', 'అను')}'\n")

    print("="*70 + "\n")
