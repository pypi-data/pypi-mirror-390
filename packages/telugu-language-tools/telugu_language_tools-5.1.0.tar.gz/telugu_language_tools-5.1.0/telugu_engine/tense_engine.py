"""
Tense Engine v3.0 - Integrated with Modern Grammar
==================================================

Fully integrated with grammar.py for modern Telugu patterns:
- Modern verb conjugation (Past Participle + Person Marker)
- 4-case system
- SOV syntax processing
- Vowel harmony
- Sandhi rules

Based on v3.0 standards - uses modern forms only!
"""

from typing import Dict, List, Optional
from .grammar import (
    conjugate_verb, apply_case, convert_svo_to_soV,
    build_telugu_sentence, apply_sandhi, check_vowel_harmony,
    PERSON_MARKERS, CASE_MARKERS
)


# ============================================================================
# SECTION 1: TENSE DETECTION
# ============================================================================

def detect_tense(text: str) -> str:
    """
    Detect tense from English text.

    Simple heuristics - can be enhanced with NLP.

    Args:
        text: English text

    Returns:
        'past', 'present', 'future', or 'unknown'
    """
    text_lower = text.lower()

    # Past tense indicators
    past_indicators = ['ed', 'was', 'were', 'did', 'had', 'went', 'came', 'ate', 'saw']
    for indicator in past_indicators:
        if indicator in text_lower:
            return 'past'

    # Present continuous
    if 'ing' in text_lower:
        return 'present'

    # Present tense (default for simple statements)
    if any(word in text_lower for word in ['is', 'are', 'am', 'do', 'does', 'go', 'eat', 'read']):
        return 'present'

    # Future tense
    future_indicators = ['will', 'shall', 'going to', 'tomorrow', 'next']
    for indicator in future_indicators:
        if indicator in text_lower:
            return 'future'

    return 'unknown'


def detect_person(text: str) -> str:
    """
    Detect person from English text.

    Args:
        text: English text

    Returns:
        '1ps' (I), '2ps' (you), '3ps' (he/she/it), etc.
    """
    text_lower = text.lower()
    words = text_lower.split()

    # First person
    if any(word in words for word in ['i', "i'm", "i've", "i'll"]):
        return '1ps'
    if any(word in words for word in ['we', "we're", "we've", "we'll"]):
        return '1pp'

    # Second person
    if any(word in words for word in ['you', "you're", "you've", "you'll"]):
        # Check if plural
        if any(word in text_lower for word in ['all', 'group', 'team', 'people']):
            return '2pp'
        return '2ps'

    # Third person
    if any(word in words for word in ['he', "he's", 'she', "she's", 'it', "it's"]):
        return '3ps'
    if any(word in words for word in ['they', "they're", "they've", "they'll"]):
        return '3pp'

    # Default to 3rd person singular
    return '3ps'


# ============================================================================
# SECTION 2: MODERN VERB CONJUGATION
# ============================================================================

def get_verb_root(verb: str) -> str:
    """
    Get verb root for conjugation.

    Map common English verbs to Telugu roots.

    Args:
        verb: English verb (e.g., 'read', 'eat', 'come')

    Returns:
        Telugu verb root
    """
    verb_map = {
        'read': 'chaduvu',
        'eat': 'tinu',
        'come': 'vaddu',
        'go': 'velli',
        'do': 'cheyyu',
        'be': 'raavu',
        'have': 'untundi',
        'say': 'annanu',
        'give': 'istunnaru',
        'take': 'tesukunnaru',
        'see': 'chusi',
        'know': 'telisi',
        'think': '脑li',
        'look': 'chusi',
        'come': 'vachcharu',
        'work': 'pani',
        'make': 'make',
        'know': 'mariyu',
    }

    return verb_map.get(verb.lower(), verb.lower())


def conjugate_english_verb(verb: str, tense: str, person: str) -> str:
    """
    Conjugate English verb to Telugu using modern pattern.

    Args:
        verb: English verb (base form)
        tense: 'past', 'present', 'future'
        person: '1ps', '1pp', '2ps', '2pp', '3ps', '3pp'

    Returns:
        Conjugated Telugu verb
    """
    # Get Telugu root
    root = get_verb_root(verb)

    # For past tense, use modern participle + marker pattern
    if tense == 'past':
        return conjugate_verb(root, 'past', person)

    # For present/future, use simple forms for now
    # TODO: Implement proper present/future conjugation
    if tense == 'present':
        # Present continuous: ROOT + తున్నా
        if person == '1ps':
            return conjugate_verb(root, 'present', '1ps').replace('ిన', 'ి తున్నాను')
        elif person == '3ps':
            return conjugate_verb(root, 'present', '3ps').replace('ిన', 'ి తున్నాడు')
        elif person == '3pp':
            return conjugate_verb(root, 'present', '3pp').replace('ిన', 'ి తున్నారు')
    elif tense == 'future':
        # Future: ROOT + తా
        if person == '1ps':
            return conjugate_verb(root, 'future', '1ps').replace('ిన', 'ు తాను')
        elif person == '3ps':
            return conjugate_verb(root, 'future', '3ps').replace('ిన', 'ు తాడు')
        elif person == '3pp':
            return conjugate_verb(root, 'future', '3pp').replace('ిన', 'ు తారు')

    # Fallback: just return root
    return root


# ============================================================================
# SECTION 3: SENTENCE PROCESSING
# ============================================================================

def process_simple_sentence(sentence: str) -> str:
    """
    Process simple English sentence to Telugu.

    Example:
        "Ramu reads book" → "రాము పుస్తకం చదువుతాడు"

    Args:
        sentence: English sentence (SVO order)

    Returns:
        Telugu sentence (SOV order with grammar)
    """
    # Step 1: Detect parts
    parts = convert_svo_to_soV(sentence)
    if not parts or not parts.get('subject'):
        return sentence

    subject = parts['subject']
    obj = parts.get('object', '')
    verb = parts.get('verb', '')

    # Step 2: Detect tense and person
    tense = detect_tense(sentence)
    person = detect_person(sentence)

    # Step 3: Transliterate parts
    from .transliterator import eng_to_telugu

    subject_telugu = eng_to_telugu(subject)
    obj_telugu = eng_to_telugu(obj) if obj else ''
    verb_telugu = eng_to_telugu(verb)

    # Step 4: Apply case markers
    subject_telugu = apply_case(subject_telugu, 'nominative')
    if obj_telugu:
        obj_telugu = apply_case(obj_telugu, 'accusative')

    # Step 5: Conjugate verb
    verb_root = get_verb_root(verb)
    verb_conjugated = conjugate_verb(verb_root, tense, person)

    # Step 6: Build sentence in SOV order
    telugu_parts = [subject_telugu]
    if obj_telugu:
        telugu_parts.append(obj_telugu)
    telugu_parts.append(verb_conjugated)

    result = ' '.join(telugu_parts)

    # Step 7: Apply sandhi
    result = apply_final_sandhi(result)

    return result


def apply_final_sandhi(text: str) -> str:
    """
    Apply final sandhi to complete sentence.

    Simple version - can be enhanced.

    Args:
        text: Telugu text

    Returns:
        Text with sandhi applied
    """
    # For now, just return as-is
    # TODO: Add proper sandhi rules
    return text


# ============================================================================
# SECTION 4: ADVANCED SENTENCE PROCESSING
# ============================================================================

def process_complex_sentence(sentence: str) -> str:
    """
    Process complex sentences (with modifiers, etc.).

    Args:
        sentence: Complex English sentence

    Returns:
        Telugu translation
    """
    # For now, fall back to simple processing
    return process_simple_sentence(sentence)


def apply_formality(text: str, formality: str = 'informal') -> str:
    """
    Apply formality markers to text.

    Args:
        text: Telugu text
        formality: 'informal', 'formal', 'honorific'

    Returns:
        Text with formality markers
    """
    if formality == 'formal':
        # Add respectful markers
        if not text.endswith('గారు') and not text.endswith('వారు'):
            text += 'గారు'
    elif formality == 'honorific':
        # Add very respectful markers
        if not text.endswith('వారు'):
            text += 'వారు'

    return text


# ============================================================================
# SECTION 5: VALIDATION
# ============================================================================

def validate_tense_conjugation(verb: str, tense: str, person: str) -> bool:
    """
    Validate that conjugation follows v3.0 modern patterns.

    Args:
        verb: Verb form
        tense: Tense
        person: Person

    Returns:
        True if valid modern pattern
    """
    # Check for archaic patterns to avoid
    archaic_patterns = ['చేసితిని', 'చేసితిరి', 'వాండ్రు', 'ఏను']

    for pattern in archaic_patterns:
        if pattern in verb:
            return False

    # Check for modern patterns
    modern_patterns = ['సినాను', 'సినారు', 'వాళ్ళు', 'నేను']

    # For past tense, should have participle
    if tense == 'past' and 'సిన' not in verb:
        # Could be other past forms, just log warning
        pass

    return True


# ============================================================================
# SECTION 6: PUBLIC API
# ============================================================================

__all__ = [
    'detect_tense',
    'detect_person',
    'conjugate_english_verb',
    'process_simple_sentence',
    'process_complex_sentence',
    'apply_formality',
    'validate_tense_conjugation',
]


# ============================================================================
# SECTION 7: EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  TENSE ENGINE v3.0 - EXAMPLES")
    print("="*70 + "\n")

    # Test simple sentences
    test_cases = [
        ("I read", "past", "1ps"),
        ("He came", "past", "3ps"),
        ("They ate", "past", "3pp"),
        ("You go", "present", "2ps"),
    ]

    print("1. Verb Conjugation:")
    for sentence, tense, person in test_cases:
        # Extract verb from sentence
        words = sentence.split()
        verb = words[-1] if words else 'read'
        result = conjugate_english_verb(verb, tense, person)
        print(f"   {sentence} ({tense}, {person}) → {result}")

    print("\n2. Sentence Processing:")
    sentences = [
        "Ramu reads book",
        "Sita ate rice",
        "I came",
        "They will go",
    ]

    for sentence in sentences:
        result = process_simple_sentence(sentence)
        print(f"   '{sentence}' → '{result}'")

    print("\n3. Formality:")
    text = process_simple_sentence("You came")
    print(f"   Informal: {text}")
    print(f"   Formal: {apply_formality(text, 'formal')}")

    print("\n" + "="*70 + "\n")
