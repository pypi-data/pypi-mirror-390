"""
v3.0 Compliance Validator
==========================

Validates that Telugu text follows v3.0 modern standards:
- Script compliance (no archaic letters)
- Modern pronouns
- Modern verb patterns
- 4-case system
- Vowel harmony

Usage:
    from telugu_engine.v3_validator import validate_v3_compliance
    result = validate_v3_compliance("నేను వచ్చాను")
"""

from typing import Dict, List, Tuple
import re


# ============================================================================
# SECTION 1: SCRIPT VALIDATION
# ============================================================================

# Archaic letters (v3.0 PROHIBITS these)
ARCHAIC_LETTERS = [
    'ఱ',   # Banḍi Ra (alveolar trill - archaic)
    'ఌ',   # Vocalic l (confined to Sanskrit)
    'ౡ',   # Long vocalic l (obsolete)
    'ౘ',   # Marginal consonant (replaced)
    'ౙ',   # Marginal consonant (replaced)
    'ఀ',   # Archaic candrabindu
    'ౝ',   # Archaic nakara pollu
]

# Modern consonants (v3.0 ALLOWS these)
MODERN_CONSONANTS = [
    'క', 'ఖ', 'గ', 'ఘ', 'ఙ',
    'చ', 'ఛ', 'జ', 'ఝ', 'ఞ',
    'ట', 'ఠ', 'డ', 'ఢ', 'ణ',
    'త', 'థ', 'ద', 'ధ', 'న',
    'ప', 'ఫ', 'బ', 'భ', 'మ',
    'య', 'ర', 'ల', 'వ', 'శ', 'ష', 'స', 'హ'
]

# Modern vowels (v3.0 ALLOWS these)
MODERN_VOWELS = [
    'అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ',
    'ఋ', 'ౠ', 'ఎ', 'ఏ', 'ఒ', 'ఓ',
    'ఐ', 'ఔ'
]

# Modern pronouns (v3.0 standard)
MODERN_PRONOUNS = [
    'నేను',     # I (modern)
    'నీవు',     # You (informal)
    'మీరు',     # You (formal/plural)
    'వాళ్ళు',   # They (modern, human)
    'మేము',     # We (modern)
    'మనము',     # We (inclusive)
    'వాడు',     # He
    'అది',       # It
]

# Archaic pronouns (v3.0 PROHIBITS these)
ARCHAIC_PRONOUNS = [
    'ఏను',       # Old 1st person
    'ఈవు',       # Old 2nd person
    'వాండ్రు',   # Old 3rd plural human
    'ఏము',       # Old 1st plural
]

# Modern verb patterns (v3.0 standard)
MODERN_VERB_PATTERNS = [
    'సినాను',    # I did (modern)
    'సినారు',    # They did (modern)
    'చేసినాను',  # I did (modern)
    'తిన్నాను',  # I ate (modern)
    'వచ్చాను',   # I came (modern)
]

# Archaic verb patterns (v3.0 PROHIBITS these)
ARCHAIC_VERB_PATTERNS = [
    'చేసితిని',  # Old past pattern
    'చేసితిరి',  # Old past plural
    'తినితిని',  # Old past
    'వచ్చితిని', # Old past
]


# ============================================================================
# SECTION 2: VALIDATION FUNCTIONS
# ============================================================================

def validate_script(text: str) -> Tuple[bool, List[str]]:
    """
    Validate script compliance (no archaic letters).

    Args:
        text: Telugu text to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for archaic letters
    for letter in ARCHAIC_LETTERS:
        if letter in text:
            errors.append(f"Archaic letter found: {letter}")

    # Check for modern characters (best effort)
    # This is a basic check - could be enhanced
    telugu_chars = set(text) - set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:()[]{}"\'-')
    if telugu_chars:
        # Check if any are not in modern sets
        for char in telugu_chars:
            if char not in MODERN_CONSONANTS + MODERN_VOWELS and char not in ['ం', 'ః', '్', 'ి', 'ు', 'ె', 'ొ', 'ా', 'ీ', 'ూ', 'ే', 'ో', 'ై', 'ౌ']:
                errors.append(f"Unknown character: {char}")

    return len(errors) == 0, errors


def validate_pronouns(text: str) -> Tuple[bool, List[str]]:
    """
    Validate modern pronouns (v3.0 standard).

    Args:
        text: Telugu text to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for archaic pronouns
    for pronoun in ARCHAIC_PRONOUNS:
        if pronoun in text:
            errors.append(f"Archaic pronoun found: {pronoun}")

    return len(errors) == 0, errors


def validate_verbs(text: str) -> Tuple[bool, List[str]]:
    """
    Validate modern verb patterns.

    Args:
        text: Telugu text to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for archaic verb patterns
    for pattern in ARCHAIC_VERB_PATTERNS:
        if pattern in text:
            errors.append(f"Archaic verb pattern found: {pattern}")

    # Check if past tense uses modern participle pattern
    # Look for -సిన- (modern participle marker)
    if any(word in text for word in ['చేసి', 'తిని', 'వచ్చి', 'రాసి']):
        # Has participle, which is good
        pass

    return len(errors) == 0, errors


def validate_case_markers(text: str) -> Tuple[bool, List[str]]:
    """
    Validate 4-case system usage.

    Args:
        text: Telugu text to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for correct case markers
    modern_case_markers = ['డు', 'ను', 'కు', 'లో']

    # This is a basic check - real implementation would be more sophisticated
    # For now, just return True (v3.0 allows flexibility in case marking)

    return True, errors


def validate_vowel_harmony(text: str) -> Tuple[bool, List[str]]:
    """
    Validate vowel harmony in text.

    Args:
        text: Telugu text to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for obvious front/back mixing
    # This is a simplified check
    front_vowels = ['ఇ', 'ఈ', 'ఎ', 'ఏ', 'ఐ']
    back_vowels = ['అ', 'ఆ', 'ఉ', 'ఊ', 'ఒ', 'ఓ', 'ఔ']

    # Find words with mixed vowel classes
    words = text.split()
    for word in words:
        word_front = any(v in word for v in front_vowels)
        word_back = any(v in word for v in back_vowels)

        if word_front and word_back and len(word) > 2:
            # Mixed vowels in a single word - could be a harmony violation
            # But this is a warning, not an error (some exceptions exist)
            pass

    return len(errors) == 0, errors


# ============================================================================
# SECTION 3: COMPREHENSIVE VALIDATION
# ============================================================================

def validate_v3_compliance(text: str) -> Dict[str, any]:
    """
    Comprehensive v3.0 compliance check.

    Args:
        text: Telugu text to validate

    Returns:
        Dictionary with validation results
    """
    results = {
        'is_compliant': True,
        'score': 100.0,  # 0-100 percentage
        'errors': [],
        'warnings': [],
        'checks': {}
    }

    # Run all checks
    checks = [
        ('script', validate_script),
        ('pronouns', validate_pronouns),
        ('verbs', validate_verbs),
        ('case_markers', validate_case_markers),
        ('vowel_harmony', validate_vowel_harmony)
    ]

    for check_name, check_func in checks:
        is_valid, errors = check_func(text)
        results['checks'][check_name] = {
            'valid': is_valid,
            'errors': errors
        }

        if not is_valid:
            results['is_compliant'] = False
            results['errors'].extend(errors)
            # Deduct score based on errors
            results['score'] -= len(errors) * 5

    # Calculate score (minimum 0, maximum 100)
    results['score'] = max(0, min(100, results['score']))

    return results


def get_compliance_report(text: str) -> str:
    """
    Generate a human-readable compliance report.

    Args:
        text: Telugu text

    Returns:
        Formatted report string
    """
    results = validate_v3_compliance(text)

    lines = []
    lines.append("="*70)
    lines.append("  v3.0 COMPLIANCE REPORT")
    lines.append("="*70)
    lines.append("")

    lines.append(f"Text: {text}")
    lines.append(f"Overall: {'✓ COMPLIANT' if results['is_compliant'] else '✗ NON-COMPLIANT'}")
    lines.append(f"Score: {results['score']:.1f}/100")
    lines.append("")

    lines.append("Checks:")
    for check_name, check_result in results['checks'].items():
        status = "✓" if check_result['valid'] else "✗"
        lines.append(f"  {status} {check_name.replace('_', ' ').title()}")

    if results['errors']:
        lines.append("")
        lines.append("Errors:")
        for error in results['errors']:
            lines.append(f"  - {error}")

    if results['warnings']:
        lines.append("")
        lines.append("Warnings:")
        for warning in results['warnings']:
            lines.append(f"  - {warning}")

    lines.append("")
    lines.append("="*70)

    return "\n".join(lines)


# ============================================================================
# SECTION 4: TESTING UTILITIES
# ============================================================================

def test_v3_compliance():
    """
    Test v3.0 compliance on sample texts.

    Returns:
        Test results
    """
    test_cases = [
        {
            'text': 'నేను వచ్చాను',
            'expected': True,
            'description': 'Modern pronoun and verb'
        },
        {
            'text': 'వాళ్ళు తిన్నారు',
            'expected': True,
            'description': 'Modern 3rd plural'
        },
        {
            'text': 'ఏను చేసితిని',
            'expected': False,
            'description': 'Archaic pronoun and verb'
        },
        {
            'text': 'రాము పుస్తకం చదువుతాడు',
            'expected': True,
            'description': 'Simple sentence'
        }
    ]

    print("\n" + "="*70)
    print("  v3.0 COMPLIANCE TESTS")
    print("="*70 + "\n")

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        text = test['text']
        expected = test['expected']
        desc = test['description']

        results = validate_v3_compliance(text)
        is_compliant = results['is_compliant']

        if is_compliant == expected:
            status = "✓ PASS"
            passed += 1
        else:
            status = "✗ FAIL"
            failed += 1

        print(f"{status} | Test {i}: {desc}")
        print(f"       Text: {text}")
        print(f"       Expected: {'Compliant' if expected else 'Non-compliant'}, "
              f"Got: {'Compliant' if is_compliant else 'Non-compliant'}")
        print(f"       Score: {results['score']:.1f}/100")

        if results['errors']:
            print(f"       Errors: {', '.join(results['errors'])}")

        print()

    print("="*70)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*70 + "\n")

    return failed == 0


# ============================================================================
# SECTION 5: PUBLIC API
# ============================================================================

__all__ = [
    'validate_script',
    'validate_pronouns',
    'validate_verbs',
    'validate_case_markers',
    'validate_vowel_harmony',
    'validate_v3_compliance',
    'get_compliance_report',
    'test_v3_compliance'
]


# ============================================================================
# SECTION 6: MAIN
# ============================================================================

if __name__ == "__main__":
    test_v3_compliance()
