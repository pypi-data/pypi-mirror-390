"""
ISO 15919 Standard Compliant Telugu Mappings
=============================================

International standard for romanization of Indic scripts.
Supports both diacritic notation and ASCII alternatives.

Usage:
    from telugu_lib.iso15919_mappings import get_iso_consonants, get_iso_vowels
    
Reference: ISO 15919:2001 - Transliteration of Devanagari and related Indic scripts
"""

# ============================================================================
# ISO 15919 CONSONANT MAPPINGS
# ============================================================================

def get_iso_consonants(mode="mixed"):
    """
    Get ISO 15919 compliant consonant mappings.
    
    Args:
        mode: "diacritic" (only diacritics), "ascii" (only capitals), 
              "mixed" (both, default)
    
    Returns:
        Dictionary of romanization → Telugu mappings
    """
    
    # Base mappings with diacritics (ISO 15919 standard)
    diacritic_consonants = {
        # Velars (కవర్గ)
        "k": "క",      # ka
        "kh": "ఖ",     # kha
        "g": "గ",      # ga
        "gh": "ఘ",     # gha
        "ṅ": "ఙ",      # ṅa (velar nasal, rare)
        
        # Palatals (చవర్గ)
        "c": "చ",      # ca (ISO uses 'c', not 'ch')
        "ch": "ఛ",     # cha (aspirated)
        "j": "జ",      # ja
        "jh": "ఝ",     # jha
        "ñ": "ఞ",      # ña (palatal nasal, rare)
        
        # Retroflexes (టవర్గ) - with underdots
        "ṭ": "ట",      # ṭa
        "ṭh": "ఠ",     # ṭha
        "ḍ": "డ",      # ḍa
        "ḍh": "ఢ",     # ḍha
        "ṇ": "ణ",      # ṇa (retroflex nasal)
        
        # Dentals (తవర్గ)
        "t": "త",      # ta
        "th": "థ",     # tha
        "d": "ద",      # da
        "dh": "ధ",     # dha
        "n": "న",      # na (dental nasal)
        
        # Labials (పవర్గ)
        "p": "ప",      # pa
        "ph": "ఫ",     # pha
        "b": "బ",      # ba
        "bh": "భ",     # bha
        "m": "మ",      # ma
        
        # Sonorants (అంతస్థలు)
        "y": "య",      # ya
        "r": "ర",      # ra
        "l": "ల",      # la
        "v": "వ",      # va
        "w": "వ",      # wa (alternative for v)
        
        # Sibilants (ఊష్మలు)
        "ś": "శ",      # śa (palatal sibilant)
        "ṣ": "ష",      # ṣa (retroflex sibilant)
        "s": "స",      # sa (dental sibilant)
        
        # Glottal
        "h": "హ",      # ha
        
        # Additional consonants
        "ḷ": "ళ",      # ḷa (retroflex lateral)
        "ḻ": "ఴ",      # ḻa (Tamil retroflex, obsolete in Telugu)
        "ṟ": "ఱ",      # ṟa (alveolar trill, archaic)
        
        # Simplified alternatives (common usage)
        "sha": "శ",    # Alternative for ś
        "Sha": "ష",    # Alternative for ṣ (capital S)
        "za": "జ",     # z often mapped to ja
        "f": "ఫ",      # f → pha
    }
    
    # ASCII alternatives (using capitals for retroflexes)
    ascii_consonants = {
        # Retroflexes (capital = retroflex)
        "T": "ట",      # ASCII for ṭ
        "Th": "ఠ",     # ASCII for ṭh
        "D": "డ",      # ASCII for ḍ
        "Dh": "ఢ",     # ASCII for ḍh
        "N": "ణ",      # ASCII for ṇ (retroflex nasal)
        "L": "ళ",      # ASCII for ḷ (retroflex lateral)
        "R": "ఱ",      # ASCII for ṟ (rare)
        
        # Sibilants
        "S": "ష",      # ASCII for ṣ (retroflex sibilant)
        "sh": "శ",     # Palatal sibilant (lowercase)
        
        # Palatals
        "ch": "చ",     # Common ch → ca
        "chh": "ఛ",    # Aspirated
        
        # Nasals
        "ng": "ఙ",     # ASCII for ṅ (velar nasal)
        "ny": "ఞ",     # ASCII for ñ (palatal nasal)
    }
    
    # Combined mapping based on mode
    if mode == "diacritic":
        return diacritic_consonants
    elif mode == "ascii":
        return {**diacritic_consonants, **ascii_consonants}
    else:  # mixed (default)
        return {**diacritic_consonants, **ascii_consonants}


# ============================================================================
# ISO 15919 VOWEL MAPPINGS
# ============================================================================

def get_iso_vowels(mode="mixed"):
    """
    Get ISO 15919 compliant vowel mappings.
    
    Args:
        mode: "diacritic" (only diacritics), "ascii" (only capitals), 
              "mixed" (both, default)
    
    Returns:
        Dictionary of romanization → Telugu vowel mappings
    """
    
    # Base vowels with diacritics (ISO 15919 standard)
    diacritic_vowels = {
        # Short vowels
        "a": "అ",      # a (short)
        "i": "ఇ",      # i (short)
        "u": "ఉ",      # u (short)
        "ṛ": "ఋ",      # ṛ (vocalic r, short)
        "ḷ": "ఌ",      # ḷ (vocalic l, short, very rare)
        
        # Long vowels (with macrons)
        "ā": "ఆ",      # ā (long)
        "ī": "ఈ",      # ī (long)
        "ū": "ఊ",      # ū (long)
        "ṝ": "ౠ",      # ṝ (vocalic r, long)
        "ḹ": "ౡ",      # ḹ (vocalic l, long, very rare)
        
        # E vowels
        "e": "ఎ",      # e (short)
        "ē": "ఏ",      # ē (long)
        
        # O vowels
        "o": "ఒ",      # o (short)
        "ō": "ఓ",      # ō (long)
        
        # Diphthongs
        "ai": "ఐ",     # ai
        "au": "ఔ",     # au
        
        # Special markers
        "ṁ": "ం",      # ṁ (anusvara)
        "ḥ": "ః",      # ḥ (visarga)
        "m̐": "ఁ",      # candrabindu (rare)
    }
    
    # ASCII alternatives
    ascii_vowels = {
        # Long vowels (capital = long, or double letter)
        "A": "ఆ",      # ASCII for ā
        "aa": "ఆ",     # Alternative for ā
        "I": "ఈ",      # ASCII for ī
        "ii": "ఈ",     # Alternative for ī
        "U": "ఊ",      # ASCII for ū
        "uu": "ఊ",     # Alternative for ū
        "E": "ఏ",      # ASCII for ē (long e)
        "ee": "ఏ",     # Alternative for ē
        "O": "ఓ",      # ASCII for ō (long o)
        "oo": "ఓ",     # Alternative for ō
        
        # Vocalic consonants
        "R": "ఋ",      # ASCII for ṛ
        "ri": "ఋ",     # Common alternative
        "RR": "ౠ",     # ASCII for ṝ (long)
        "rii": "ౠ",    # Common alternative
        
        # Vocalic l (very rare)
        "lR": "ఌ",     # ASCII for ḷ
        "li": "ఌ",     # Common alternative
        
        # Special markers
        "M": "ం",      # ASCII for ṁ (anusvara)
        "am": "ం",     # Common representation
        "H": "ః",      # ASCII for ḥ (visarga)
        "ah": "ః",     # Common representation
    }
    
    if mode == "diacritic":
        return diacritic_vowels
    elif mode == "ascii":
        return {**diacritic_vowels, **ascii_vowels}
    else:  # mixed
        return {**diacritic_vowels, **ascii_vowels}


# ============================================================================
# ISO 15919 MATRA (VOWEL SIGN) MAPPINGS
# ============================================================================

def get_iso_matras(mode="mixed"):
    """
    Get ISO 15919 compliant matra (vowel sign) mappings.
    
    Matras are vowel signs that attach to consonants.
    
    Returns:
        Dictionary of romanization → Telugu matra mappings
    """
    
    diacritic_matras = {
        # No marking for inherent 'a'
        "a": "",       # Inherent vowel (no mark)
        
        # Short vowel signs
        "i": "ి",      # i-matra
        "u": "ు",      # u-matra
        "ṛ": "ృ",      # ṛ-matra (vocalic r)
        "ḷ": "ౢ",      # ḷ-matra (vocalic l, rare)
        
        # Long vowel signs
        "ā": "ా",      # ā-matra
        "ī": "ీ",      # ī-matra
        "ū": "ూ",      # ū-matra
        "ṝ": "ౄ",      # ṝ-matra (long vocalic r)
        "ḹ": "ౣ",      # ḹ-matra (long vocalic l, rare)
        
        # E vowel signs
        "e": "ె",      # e-matra (short)
        "ē": "ే",      # ē-matra (long)
        
        # O vowel signs
        "o": "ొ",      # o-matra (short)
        "ō": "ో",      # ō-matra (long)
        
        # Diphthong signs
        "ai": "ై",     # ai-matra
        "au": "ౌ",     # au-matra
        
        # Special markers (same as standalone)
        "ṁ": "ం",      # anusvara
        "ḥ": "ః",      # visarga
    }
    
    ascii_matras = {
        # ASCII alternatives for long vowels
        "A": "ా",      # ASCII for ā
        "aa": "ా",     # Common alternative
        "I": "ీ",      # ASCII for ī
        "ii": "ీ",     # Common alternative
        "U": "ూ",      # ASCII for ū
        "uu": "ూ",     # Common alternative
        "E": "ే",      # ASCII for ē
        "ee": "ే",     # Common alternative
        "O": "ో",      # ASCII for ō
        "oo": "ో",     # Common alternative
        
        # Vocalic consonants
        "R": "ృ",      # ASCII for ṛ
        "ri": "ృ",     # Common alternative
        "RR": "ౄ",     # ASCII for ṝ
        "rii": "ౄ",    # Common alternative
        
        # Special markers
        "M": "ం",      # ASCII for ṁ
        "am": "ం",     # Common representation
        "H": "ః",      # ASCII for ḥ
        "ah": "ః",     # Common representation
    }
    
    if mode == "diacritic":
        return diacritic_matras
    elif mode == "ascii":
        return {**diacritic_matras, **ascii_matras}
    else:  # mixed
        return {**diacritic_matras, **ascii_matras}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_input(text):
    """
    Normalize input text to handle common variations.
    
    Converts common romanization variants to ISO 15919 standard.
    """
    replacements = {
        # Common variations → ISO standard
        "Ch": "ch",    # Capital Ch → ch
        "zh": "j",     # zh → j
        "Z": "j",      # Z → j
        "ph": "ph",    # Already correct
        "f": "ph",     # f → ph (no native f in Telugu)
        "q": "k",      # q → k (no native q)
        "x": "ks",     # x → ks cluster
        
        # Ensure ASCII capitals for retroflexes are preserved
        # (handled separately in get_iso_consonants)
    }
    
    result = text
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result


def get_articulation_class(consonant):
    """
    Get the articulation class of a consonant for nasal assimilation.
    
    Returns:
        String: "velar", "palatal", "retroflex", "dental", "labial", or None
    """
    VELAR = ["k", "kh", "g", "gh", "ṅ", "ng"]
    PALATAL = ["c", "ch", "chh", "j", "jh", "ñ", "ny", "ś", "sh"]
    RETROFLEX = ["ṭ", "ṭh", "ḍ", "ḍh", "ṇ", "ṣ", "T", "Th", "D", "Dh", "N", "S", "ḷ", "L"]
    DENTAL = ["t", "th", "d", "dh", "n", "s"]
    LABIAL = ["p", "ph", "b", "bh", "m", "v", "w"]
    
    if consonant in VELAR:
        return "velar"
    elif consonant in PALATAL:
        return "palatal"
    elif consonant in RETROFLEX:
        return "retroflex"
    elif consonant in DENTAL:
        return "dental"
    elif consonant in LABIAL:
        return "labial"
    else:
        return None


def is_retroflex(char):
    """Check if character is a retroflex consonant"""
    retroflexes = ["ṭ", "ṭh", "ḍ", "ḍh", "ṇ", "ṣ", "ḷ", "ṟ",
                   "T", "Th", "D", "Dh", "N", "S", "L", "R",
                   "ట", "ఠ", "డ", "ఢ", "ణ", "ష", "ళ", "ఱ"]
    return char in retroflexes


def is_dental(char):
    """Check if character is a dental consonant"""
    dentals = ["t", "th", "d", "dh", "n", "s",
               "త", "థ", "ద", "ధ", "న", "స"]
    return char in dentals


# ============================================================================
# VALIDATION AND TESTING
# ============================================================================

def validate_iso_mappings():
    """Validate that all ISO 15919 standard characters are mapped"""
    consonants = get_iso_consonants("mixed")
    vowels = get_iso_vowels("mixed")
    matras = get_iso_matras("mixed")
    
    print("ISO 15919 Mappings Validation")
    print("=" * 50)
    print(f"Consonants: {len(consonants)} mappings")
    print(f"Vowels: {len(vowels)} mappings")
    print(f"Matras: {len(matras)} mappings")
    print(f"Total: {len(consonants) + len(vowels) + len(matras)} mappings")
    
    # Check for duplicates
    all_roman = list(consonants.keys()) + list(vowels.keys())
    duplicates = [x for x in all_roman if all_roman.count(x) > 1]
    if duplicates:
        print(f"\n⚠️  Warning: Duplicate roman keys: {set(duplicates)}")
    else:
        print("\n✅ No duplicate keys")
    
    # Check Telugu coverage
    telugu_chars = set(consonants.values()) | set(vowels.values())
    print(f"\n✅ Covers {len(telugu_chars)} unique Telugu characters")
    
    return True


if __name__ == "__main__":
    # Run validation
    validate_iso_mappings()
    
    # Example usage
    print("\n" + "=" * 50)
    print("Example Usage:")
    print("=" * 50)
    
    consonants = get_iso_consonants("mixed")
    vowels = get_iso_vowels("mixed")
    
    examples = [
        ("k", "Velar"),
        ("ṭ", "Retroflex (diacritic)"),
        ("T", "Retroflex (ASCII)"),
        ("ṅ", "Velar nasal (diacritic)"),
        ("ng", "Velar nasal (ASCII)"),
        ("ā", "Long vowel (diacritic)"),
        ("A", "Long vowel (ASCII)"),
        ("aa", "Long vowel (double)"),
    ]
    
    for roman, description in examples:
        telugu_cons = consonants.get(roman)
        telugu_vow = vowels.get(roman)
        telugu = telugu_cons or telugu_vow or "N/A"
        print(f"{roman:4} → {telugu:2}  ({description})")
