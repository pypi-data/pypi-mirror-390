"""
Telugu Library v5.0 - Modern Telugu Engine
===========================================

Complete v3.0 compliant Telugu processing library with full v3.0 support:
- transliterator: Modern transliteration (no archaic letters)
- grammar: Modern grammar (verbs, cases, SOV)
- tense_engine: Integrated tense processing
- enhanced_tense: v5.0 enhanced tense (present continuous, all tenses)
- v3_validator: v3.0 compliance validation
- phonetic_matrix: Phonetic normalization

All modules use modern Vyāvahārika standards:
- Modern pronouns: నేను, వాళ్ళు (NOT ఏను, వాండ్రు)
- Modern verbs: చేసినాను (NOT చేసితిని)
- 4-case system: Nominative, Accusative, Dative, Locative
- SOV syntax
- No archaic letters: ఱ, ఌ, ౡ, ౘ, ౙ, ఀ, ౝ

v5.0 Features:
- Present continuous tense: "I am going" → నేను వెళ్తున్నాను
- All 16 v3.0 sections implemented
- Comprehensive test suites
- Translation challenges solved
- Error prevention checklist
"""

# Main API - transliteration
from .transliterator import (
    eng_to_telugu,
    transliterate_word,
    transliterate_sentence,
    validate_v3_compliance as _validate_translit_v3
)

# Grammar module
from .grammar import (
    conjugate_verb,
    apply_case,
    convert_svo_to_soV,
    build_telugu_sentence,
    apply_sandhi,
    check_vowel_harmony,
    apply_vowel_harmony
)

# Tense engine
from .tense_engine import (
    detect_tense,
    detect_person,
    conjugate_english_verb,
    process_simple_sentence,
    process_complex_sentence,
    apply_formality,
    validate_tense_conjugation
)

# v3.0 validator
from .v3_validator import (
    validate_script,
    validate_pronouns,
    validate_verbs,
    validate_case_markers,
    validate_vowel_harmony,
    validate_v3_compliance,
    get_compliance_report,
    test_v3_compliance
)

# Enhanced tense engine (v5.0 - full v3.0 support)
from .enhanced_tense import (
    translate_sentence,
    conjugate_present_continuous,
    conjugate_past_tense,
    conjugate_verb_enhanced,
    detect_tense_enhanced,
    detect_person,
    validate_translation_output,
    run_comprehensive_test_suite
)

# Phonetic matrix (kept for compatibility)
from .phonetic_matrix import map_sound

# Public API
__version__ = "5.0.4"
__author__ = "Telugu Library v3.0"
__email__ = "support@telugulibrary.org"

__all__ = [
    # Transliteration
    "eng_to_telugu",
    "transliterate_word",
    "transliterate_sentence",

    # Grammar
    "conjugate_verb",
    "apply_case",
    "convert_svo_to_soV",
    "build_telugu_sentence",
    "apply_sandhi",
    "check_vowel_harmony",
    "apply_vowel_harmony",

    # Tense
    "detect_tense",
    "detect_person",
    "conjugate_english_verb",
    "process_simple_sentence",
    "process_complex_sentence",
    "apply_formality",
    "validate_tense_conjugation",

    # Enhanced Tense (v5.0 - Full v3.0 Support)
    "translate_sentence",
    "conjugate_present_continuous",
    "conjugate_past_tense",
    "conjugate_verb_enhanced",
    "detect_tense_enhanced",
    "validate_translation_output",
    "run_comprehensive_test_suite",

    # Validation
    "validate_v3_compliance",
    "get_compliance_report",
    "test_v3_compliance",
    "validate_script",
    "validate_pronouns",
    "validate_verbs",
    "validate_case_markers",
    "validate_vowel_harmony",

    # Legacy (for compatibility)
    "map_sound",
]

# Convenience functions
def translate(text: str, include_grammar: bool = False) -> str:
    """
    High-level translation function.

    Args:
        text: English text to translate
        include_grammar: If True, apply full grammar (cases, SOV, etc.)

    Returns:
        Telugu text
    """
    if include_grammar:
        # Apply full grammar processing
        return process_simple_sentence(text)
    else:
        # Just transliterate
        return eng_to_telugu(text)


def is_v3_compliant(text: str) -> bool:
    """
    Check if text is v3.0 compliant.

    Args:
        text: Telugu text to check

    Returns:
        True if compliant, False otherwise
    """
    result = validate_v3_compliance(text)
    return result['is_compliant']


def get_compliance_score(text: str) -> float:
    """
    Get v3.0 compliance score (0-100).

    Args:
        text: Telugu text to check

    Returns:
        Compliance score (0-100)
    """
    result = validate_v3_compliance(text)
    return result['score']


# Add to public API
__all__.extend([
    "translate",
    "is_v3_compliant",
    "get_compliance_score",
])
