"""
Context-Aware Transliteration Rules
====================================

Intelligent disambiguation based on phonetic context, position, and patterns.

Features:
- Context-aware nasal selection (5 types: ఙ, ఞ, ణ, న, మ)
- Vowel length disambiguation (short vs long)
- Retroflex vs dental selection
- Anusvara intelligent placement
- Schwa deletion rules

Usage:
    from telugu_lib.context_rules import ContextualTransliterator
    trans = ContextualTransliterator()
    result = trans.transliterate("samskara")
"""

from typing import Optional, Tuple, List
from .iso15919_mappings import get_iso_consonants, get_iso_vowels, get_articulation_class


# ============================================================================
# CONTEXT-AWARE NASAL SELECTION
# ============================================================================

class NasalSelector:
    """
    Select appropriate nasal consonant based on phonetic context.
    
    Telugu has 5 nasal types:
    - ఙ (ṅa) - Velar nasal (after k, g)
    - ఞ (ña) - Palatal nasal (after ch, j)
    - ణ (ṇa) - Retroflex nasal (after ṭ, ḍ)
    - న (na) - Dental nasal (default, after t, d)
    - ం (ṁ) - Anusvara (before consonants)
    """
    
    def __init__(self):
        self.consonants = get_iso_consonants("mixed")
        
        # Articulation classes
        self.VELAR = ["k", "kh", "g", "gh"]
        self.PALATAL = ["c", "ch", "chh", "j", "jh", "ś", "sh"]
        self.RETROFLEX = ["ṭ", "ṭh", "ḍ", "ḍh", "T", "Th", "D", "Dh", "ṣ", "S"]
        self.DENTAL = ["t", "th", "d", "dh", "s"]
        self.LABIAL = ["p", "ph", "b", "bh", "m", "v", "w"]
    
    def select_nasal(self, prev_char: Optional[str], next_char: Optional[str], 
                     nasal_input: str) -> str:
        """
        Select appropriate nasal based on context.
        
        Args:
            prev_char: Previous consonant (if any)
            next_char: Following consonant (if any)
            nasal_input: Original nasal input (n, m, etc.)
        
        Returns:
            Appropriate Telugu nasal character
        """
        
        # Rule 1: If nasal before consonant → use anusvara (ం)
        if next_char and next_char in self.consonants:
            return "ం"  # Anusvara before any consonant
        
        # Rule 2: After velar → velar nasal
        if prev_char in self.VELAR:
            return "ఙ"  # ṅa
        
        # Rule 3: After palatal → palatal nasal
        if prev_char in self.PALATAL:
            return "ఞ"  # ña
        
        # Rule 4: After retroflex → retroflex nasal
        if prev_char in self.RETROFLEX:
            return "ణ"  # ṇa
        
        # Rule 5: After labial → labial nasal (m)
        if prev_char in self.LABIAL:
            return "మ"  # ma
        
        # Rule 6: Explicit retroflex nasal input
        if nasal_input in ["ṇ", "N"]:
            return "ణ"
        
        # Rule 7: Explicit labial nasal input
        if nasal_input in ["m", "M"]:
            return "మ"
        
        # Default: Dental nasal (most common)
        return "న"  # na


# ============================================================================
# VOWEL LENGTH DISAMBIGUATION
# ============================================================================

class VowelDisambiguator:
    """
    Determine if vowel should be short or long based on context.
    
    Handles ambiguous cases:
    - "o" → ఒ (short) or ఓ (long)?
    - "e" → ఎ (short) or ఏ (long)?
    """
    
    def __init__(self):
        # Known words with specific vowel lengths
        self.KNOWN_WORDS = {
            # Short O
            "kotta": "కొత్త",    # new (short o)
            "kotha": "కొత్త",    # new
            "pota": "పొట",       # cover (short o)
            "rotta": "రొట్టె",   # bread (short o)
            
            # Long O
            "kota": "కోట",       # fort (long o)
            "thota": "తోట",      # garden (long o)
            "bota": "బోట",       # boat (long o)
            "rota": "రోట",       # rotation (long o)
            "mango": "మాంగో",    # mango (long o)
            
            # Short E
            "cheta": "చెట",      # tree (short e)
            "peta": "పెట",       # box (short e)
            "chetu": "చెట్టు",   # tree (short e)
            
            # Long E
            "prema": "ప్రేమ",    # love (long e)
            "deva": "దేవ",       # god (long e)
            "sevа": "సేవ",       # service (long e)
            "kela": "కేళ",       # banana (long e)
        }
    
    def disambiguate_vowel(self, word: str, position: int, vowel: str) -> str:
        """
        Determine correct vowel length based on context.
        
        Args:
            word: Complete word being transliterated
            position: Position of vowel in word
            vowel: Ambiguous vowel ('o' or 'e')
        
        Returns:
            Appropriate short or long vowel
        """
        
        # Check dictionary first
        word_lower = word.lower()
        if word_lower in self.KNOWN_WORDS:
            # Extract vowel at position from known word
            return self._extract_vowel_from_known(word_lower, position)
        
        # Heuristic rules
        if vowel == 'o':
            return self._disambiguate_o(word, position)
        elif vowel == 'e':
            return self._disambiguate_e(word, position)
        
        # Default: return short vowel
        return "ఒ" if vowel == 'o' else "ఎ"
    
    def _disambiguate_o(self, word: str, position: int) -> str:
        """Disambiguate 'o' → ఒ or ఓ"""
        
        # Rule 1: Word-final 'o' → usually long
        if position == len(word) - 1:
            return "ఓ"  # Long o
        
        # Rule 2: Before single consonant + vowel → usually long
        if position < len(word) - 2:
            if word[position + 1].isalpha() and not word[position + 1] in 'aeiou':
                if position + 2 < len(word) and word[position + 2] in 'aeiou':
                    return "ఓ"  # Long o
        
        # Rule 3: In open syllable → long
        if position < len(word) - 1 and word[position + 1] in 'aeiou':
            return "ఓ"  # Long o
        
        # Rule 4: Before double consonant → short
        if position < len(word) - 2:
            if word[position + 1] == word[position + 2]:
                return "ఒ"  # Short o
        
        # Rule 5: In loanwords (has 'o' in English) → usually long
        english_patterns = ['photo', 'video', 'radio', 'mobile', 'logo']
        if any(pattern in word.lower() for pattern in english_patterns):
            return "ఓ"  # Long o
        
        # Default: Short
        return "ఒ"
    
    def _disambiguate_e(self, word: str, position: int) -> str:
        """Disambiguate 'e' → ఎ or ఏ"""
        
        # Rule 1: Word-final 'e' → usually short
        if position == len(word) - 1:
            return "ఎ"  # Short e
        
        # Rule 2: Before 'r' or 'm' at end → usually long
        if position < len(word) - 1:
            next_chars = word[position + 1:position + 3]
            if next_chars in ['ra', 're', 'ma', 'me', 'va', 've']:
                return "ఏ"  # Long e
        
        # Rule 3: In stressed syllable → long
        # (Approximate: if followed by single consonant)
        if position < len(word) - 2:
            if word[position + 1].isalpha() and not word[position + 1] in 'aeiou':
                if position + 2 < len(word) and word[position + 2] in 'aeiou':
                    return "ఏ"  # Long e
        
        # Rule 4: Before double consonant → short
        if position < len(word) - 2:
            if word[position + 1] == word[position + 2]:
                return "ఎ"  # Short e
        
        # Default: Short
        return "ఎ"
    
    def _extract_vowel_from_known(self, word: str, position: int) -> Optional[str]:
        """Extract specific vowel from known word"""
        telugu_word = self.KNOWN_WORDS.get(word)
        if telugu_word and position < len(telugu_word):
            # Return the character at approximate position
            # (This is simplified - real implementation needs proper indexing)
            return telugu_word[min(position, len(telugu_word) - 1)]
        return None


# ============================================================================
# RETROFLEX VS DENTAL DISAMBIGUATION
# ============================================================================

class RetroflexSelector:
    """
    Determine if consonant should be dental or retroflex.
    
    Handles:
    - t → త (dental) or ட (retroflex)?
    - d → ద (dental) or డ (retroflex)?
    - n → న (dental) or ణ (retroflex)?
    """
    
    def __init__(self):
        # Patterns that indicate retroflex
        self.RETROFLEX_CONTEXTS = {
            # After these sounds → usually retroflex
            'after_r': ['r', 'R', 'ṛ'],
            'after_long_vowel': ['ā', 'ī', 'ū', 'ē', 'ō', 'A', 'I', 'U', 'E', 'O', 'aa', 'ii', 'uu', 'ee', 'oo'],
            # Word patterns
            'retroflex_words': ['kaTa', 'paNDu', 'koTi', 'gaDDa', 'vaDDu'],
        }
    
    def select_t_variant(self, word: str, position: int, explicit: Optional[str] = None) -> str:
        """
        Select between త (dental t) and ట (retroflex ṭ).
        
        Args:
            word: Complete word
            position: Position of 't' in word
            explicit: Explicit marker ('t' or 'T')
        
        Returns:
            Telugu consonant (త or ట)
        """
        
        # Explicit retroflex marker
        if explicit in ['T', 'ṭ']:
            return "ట"
        
        # Rule 1: After 'r' → usually retroflex
        if position > 0 and word[position - 1] in ['r', 'R']:
            return "ట"
        
        # Rule 2: After long vowel → often retroflex
        if position > 1:
            prev_two = word[position - 2:position]
            if prev_two in ['aa', 'ii', 'uu', 'ee', 'oo'] or prev_two[-1] in ['A', 'I', 'U', 'E', 'O']:
                return "ட"
        
        # Rule 3: Word-initial → usually dental
        if position == 0:
            return "త"
        
        # Rule 4: Before 'r' in cluster 'tr' → usually dental in English loanwords
        if position < len(word) - 1 and word[position + 1] == 'r':
            return "త"  # "train" → త్రైన్, not ట్రైన్
        
        # Rule 5: Double 'tt' → dental
        if position > 0 and word[position - 1] == 't':
            return "త"
        if position < len(word) - 1 and word[position + 1] == 't':
            return "త"
        
        # Default: Dental (more common)
        return "త"
    
    def select_d_variant(self, word: str, position: int, explicit: Optional[str] = None) -> str:
        """Select between ద (dental d) and డ (retroflex ḍ)"""
        
        if explicit in ['D', 'ḍ']:
            return "డ"
        
        # Similar rules to t_variant
        if position > 0 and word[position - 1] in ['r', 'R']:
            return "డ"
        
        if position == 0:
            return "ద"
        
        # Default: Dental
        return "ద"
    
    def select_n_variant(self, word: str, position: int, explicit: Optional[str] = None) -> str:
        """Select between న (dental n) and ణ (retroflex ṇ)"""
        
        if explicit in ['N', 'ṇ']:
            return "ణ"
        
        # After retroflex consonants → retroflex nasal
        if position > 0:
            prev = word[position - 1]
            if prev in ['ṭ', 'ṭh', 'ḍ', 'ḍh', 'T', 'D', 'ṣ', 'S', 'ḷ', 'L']:
                return "ణ"
        
        # After long vowel + 'r'
        if position > 1:
            if word[position - 1] in ['r', 'R'] and word[position - 2] in ['a', 'i', 'u']:
                return "ణ"
        
        # Default: Dental
        return "న"


# ============================================================================
# SCHWA DELETION AND VIRAMA PLACEMENT
# ============================================================================

class SchwaHandler:
    """
    Handle inherent vowel (schwa) deletion.
    
    Determines when to add virama (్) to suppress inherent 'a'.
    """
    
    def should_suppress_schwa(self, word: str, position: int, 
                             next_char: Optional[str] = None) -> bool:
        """
        Determine if inherent 'a' should be suppressed with virama.
        
        Args:
            word: Complete word
            position: Position of consonant
            next_char: Next character in transliteration
        
        Returns:
            True if virama should be added
        """
        
        # Rule 1: Consonant cluster → suppress on all but last
        if next_char and self._is_consonant(next_char):
            return True
        
        # Rule 2: Word-final consonant in Sanskrit loanwords
        if position == len(word) - 1:
            if self._is_sanskrit_loanword(word):
                # Sanskrit words often end in consonants
                return True
            # Telugu native words typically end in vowels
            return False
        
        # Rule 3: Before explicit vowel marker
        if position < len(word) - 1:
            next_input = word[position + 1]
            if next_input in 'aāiīuūeēoōṛṝḷṝ':
                return True
        
        # Rule 4: In specific patterns
        # "film" → ఫిల్మ్ (suppress after l before m)
        if position < len(word) - 1:
            current = word[position]
            next_input = word[position + 1]
            
            # Consonant + consonant at word end
            if position == len(word) - 2 and self._is_consonant(next_input):
                return True
        
        # Default: Don't suppress
        return False
    
    def _is_consonant(self, char: str) -> bool:
        """Check if character is a consonant"""
        consonants = "bcdfghjklmnpqrstvwxyzṭḍṇśṣṅñḷṟ"
        return char.lower() in consonants
    
    def _is_sanskrit_loanword(self, word: str) -> bool:
        """Heuristic to detect Sanskrit loanwords"""
        # Sanskrit loanwords often have specific patterns
        sanskrit_patterns = [
            'ksh', 'jn', 'shr',  # Special clusters
            'am$', 'ah$',         # Anusvara/visarga endings
        ]
        
        word_lower = word.lower()
        for pattern in sanskrit_patterns:
            if pattern.replace('$', '') in word_lower:
                return True
        
        return False


# ============================================================================
# CONTEXTUAL TRANSLITERATOR (MAIN CLASS)
# ============================================================================

class ContextualTransliterator:
    """
    Main transliterator with context-aware intelligence.
    
    Combines all context rules for optimal accuracy.
    """
    
    def __init__(self):
        self.nasal_selector = NasalSelector()
        self.vowel_disambiguator = VowelDisambiguator()
        self.retroflex_selector = RetroflexSelector()
        self.schwa_handler = SchwaHandler()
        
        self.consonants = get_iso_consonants("mixed")
        self.vowels = get_iso_vowels("mixed")
    
    def transliterate(self, text: str) -> str:
        """
        Transliterate with context-aware rules.
        
        Args:
            text: Roman text to transliterate
        
        Returns:
            Telugu text with context-aware disambiguation
        """
        if not text:
            return ""
        
        result = []
        i = 0
        prev_consonant = None
        
        while i < len(text):
            current = text[i]
            next_char = text[i + 1] if i < len(text) - 1 else None
            
            # Handle nasal with context
            if current in ['n', 'm', 'N', 'ṇ', 'ṅ', 'ñ']:
                nasal = self.nasal_selector.select_nasal(
                    prev_consonant, next_char, current
                )
                result.append(nasal)
                i += 1
                continue
            
            # Handle ambiguous t/d/n with retroflex selection
            if current == 't':
                t_variant = self.retroflex_selector.select_t_variant(text, i, current)
                result.append(t_variant)
                prev_consonant = current
                i += 1
                continue
            
            # Handle ambiguous vowels
            if current in ['o', 'e'] and (i == 0 or prev_consonant):
                vowel = self.vowel_disambiguator.disambiguate_vowel(text, i, current)
                result.append(vowel)
                i += 1
                continue
            
            # Default character handling
            if current in self.consonants:
                result.append(self.consonants[current])
                prev_consonant = current
            elif current in self.vowels:
                result.append(self.vowels[current])
                prev_consonant = None
            else:
                result.append(current)
            
            i += 1
        
        return ''.join(result)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def transliterate_with_context(text: str) -> str:
    """
    Convenience function for context-aware transliteration.
    
    Usage:
        from telugu_lib.context_rules import transliterate_with_context
        result = transliterate_with_context("samskara")
    """
    trans = ContextualTransliterator()
    return trans.transliterate(text)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    # Test nasal selection
    print("=" * 70)
    print("CONTEXT-AWARE NASAL SELECTION TESTING")
    print("=" * 70)
    
    selector = NasalSelector()
    test_cases = [
        ("k", "a", "n", "ఙ"),  # After velar → velar nasal
        ("j", "a", "n", "ఞ"),  # After palatal → palatal nasal
        ("T", "a", "n", "ణ"),  # After retroflex → retroflex nasal
        ("t", "a", "n", "న"),  # After dental → dental nasal
        (None, "k", "n", "ం"), # Before consonant → anusvara
    ]
    
    for prev, next_c, nasal, expected in test_cases:
        result = selector.select_nasal(prev, next_c, nasal)
        status = "✅" if result == expected else "❌"
        print(f"{status} prev={prev}, next={next_c}, nasal={nasal} → {result} (expected {expected})")
    
    # Test vowel disambiguation
    print("\n" + "=" * 70)
    print("VOWEL LENGTH DISAMBIGUATION TESTING")
    print("=" * 70)
    
    disambiguator = VowelDisambiguator()
    vowel_tests = [
        ("mango", 4, "o", "ఓ"),   # Word-final o → long
        ("kotta", 1, "o", "ఒ"),   # Before double consonant → short
        ("kota", 1, "o", "ఓ"),    # Known word → long
        ("prema", 2, "e", "ఏ"),   # Known word → long
    ]
    
    for word, pos, vowel, expected in vowel_tests:
        result = disambiguator.disambiguate_vowel(word, pos, vowel)
        status = "✅" if result == expected else "❌"
        print(f"{status} {word}[{pos}] '{vowel}' → {result} (expected {expected})")
    
    print("\n" + "=" * 70)
    print("COMPLETE CONTEXTUAL TRANSLITERATION")
    print("=" * 70)
    
    trans = ContextualTransliterator()
    examples = [
        "samskara",
        "mango",
        "temple",
        "kota",
        "prema",
    ]
    
    for word in examples:
        result = trans.transliterate(word)
        print(f"{word:15} → {result}")
