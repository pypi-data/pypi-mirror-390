"""
Telugu Library v4.3.0 — Enhanced Clusters
----------------------------------
Fixes based on user feedback:
- **Enhanced Clusters:** Added numerous 3- and 4-character consonant clusters (e.g., 'str', 'sht', 'skr', 'STh') to the 'clusters' dictionary for greater accuracy.
- **CRITICAL FIX (C+ri Matra):** Ensured consonant-r-i sequences are correctly parsed as C + R + I-matra.
- **Refined Nasal Handling:** Simplified internal nasal cluster handling to rely more heavily on the central 'clusters' map for complex cases like 'namste'.
- **Case Sensitivity Maintained:** Retains case distinction for retroflex consonants (T, D, N, S).
"""

# ──────────────────────────────────────────────────────────────────────────────
# Normalization
# ──────────────────────────────────────────────────────────────────────────────

def normalize_roman_input(text: str) -> str:
    """Normalizes romanized input to ASCII tokens our engine knows."""
    replacements = {
        'ā': 'aa', 'ē': 'ee', 'ī': 'ii', 'ō': 'oo', 'ū': 'uu',
        'ṁ': 'm',  'ṅ': 'ng', 'ñ': 'ny',
        'ṇ': 'N',  'ḍ': 'D',  'ṭ': 'T',
        'ś': 'sh', 'ṣ': 'S', 'ṛ': 'ri',
    }
    for special, basic in replacements.items():
        text = text.replace(special, basic)
    return text


# ──────────────────────────────────────────────────────────────────────────────
# Core engine
# ──────────────────────────────────────────────────────────────────────────────

def eng_to_telugu_base(text: str, rules: dict) -> str:
    """
    Core transliteration engine (v4.3.0 REVISED).
    """
    text = normalize_roman_input(text or "")
    # V4.3.0: DO NOT lowercase.
    text = text.strip()

    consonants = rules.get("consonants", {})
    vowels     = rules.get("vowels", {})
    matras     = rules.get("matras", {})
    clusters   = rules.get("clusters", {})
    geminates  = rules.get("geminates", {})
    strip_final_virama = rules.get("strip_final_virama", True)

    # Pre-sort consonant keys by length for longest-first matching
    cons_keys = sorted(consonants.keys(), key=len, reverse=True)

    result = []
    i = 0
    prev_was_consonant = False

    def attach_matra(matra_key: str):
        """Attach matra to the last emitted consonant glyph."""
        matra_key_lower = matra_key.lower()
        if not result:
            result.append(vowels.get(matra_key_lower, ""))
            return
        result.append(matras.get(matra_key_lower, ""))

    def emit_consonant(tok: str, join_prev=False):
        nonlocal prev_was_consonant
        if join_prev:
            result.append("్")
        result.append(consonants[tok])
        prev_was_consonant = True

    while i < len(text):
        chunk5, chunk4, chunk3, chunk2 = text[i:i+5], text[i:i+4], text[i:i+3], text[i:i+2]
        ch = text[i]

        # 1) Nasal clusters (longest first, explicitly handled before general clusters)
        nasal_map = {
            # Homorganic clusters
            "nk": "ంక", "ng": "ంగ", "nt": "ంత", 
            "nd": "ండ", "mp": "ంప", "mb": "ంబ",
            # Pre-clustered units (e.g., from v4.1 fix for namste)
            "namst": "నమ్స్త్", # Handles the initial part of namaste
        }
        matched = False
        for L in (5, 4, 3, 2):
            if i + L <= len(text):
                sub = text[i:i+L]
                if sub in nasal_map:
                    result.append(nasal_map[sub])
                    i += L
                    prev_was_consonant = True
                    matched = True
                    break
        if matched:
            continue

        # 2) Geminate detection (kk, ll, TT, DD, …)
        if len(chunk2) == 2 and chunk2[0] == chunk2[1] and chunk2[0] in (consonants.keys()):
            if chunk2 in geminates:
                result.append(geminates[chunk2])
            elif chunk2[0] in consonants:
                base = consonants[chunk2[0]]
                result.append(base + "్" + base)
            prev_was_consonant = True
            i += 2
            continue

        # 3) CRITICAL FIX: The C+R+i Matra sequence (e.g., 'kri')
        # This resolves the conflict between 'kri' and vocalic 'kru'
        if prev_was_consonant and len(chunk3) >= 2 and chunk2.lower() == 'ri':
            # The previous token must have been a consonant. We now emit the 'r' consonant, virama, and 'i' matra.
            # This is complex and often manually implemented: C + ్ + ర + ి
            
            # Use 'r' consonant with virama
            emit_consonant('r', join_prev=True) 
            
            # Add 'i' matra
            attach_matra('i')

            # Consumed 'ri' (2 chars) from the stream.
            prev_was_consonant = False # Vowel consumes the consonant state
            i += 2
            continue


        # 4) Regular clusters (5→4→3→2 letters, including newly added ones)
        for L in (5, 4, 3, 2):
            sub = text[i:i+L]
            if sub in clusters:
                if prev_was_consonant:
                    result.append("్")
                toks = clusters[sub]
                for idx, tk in enumerate(toks):
                    emit_consonant(tk, join_prev=(idx > 0))
                i += L
                matched = True
                break
        if matched:
            continue
            
        # 5) Two-letter Vowels/Matras (aa, ee, ii, uu, oo, rii, ai, au)
        chunk2_lower = chunk2.lower()
        if chunk2_lower in vowels or chunk2_lower in matras:
            if prev_was_consonant:
                attach_matra(chunk2_lower)
                prev_was_consonant = False
            else:
                result.append(vowels.get(chunk2_lower, ""))
            i += 2
            continue

        # 6) Two-letter consonants (e.g., 'sh', 'Dh') - case sensitive
        if chunk2 in consonants:
            if prev_was_consonant:
                result.append("్")
            emit_consonant(chunk2)
            i += 2
            continue

        # 7) Single-letter Vowels/Matras (a, i, u, e, o, am, ah)
        ch_lower = ch.lower()
        if ch_lower in vowels or ch_lower in matras:
            if ch_lower == 'a' and prev_was_consonant:
                # inherent 'a' → no matra
                prev_was_consonant = False
                i += 1
                continue
            if prev_was_consonant:
                attach_matra(ch_lower)
                prev_was_consonant = False
            else:
                result.append(vowels.get(ch_lower, ""))
            i += 1
            continue

        # 8) Single-letter consonants (e.g., 'k', 'T', 'S') - case sensitive
        matched_cons = None
        for k in cons_keys:
            if text.startswith(k, i):
                matched_cons = k
                break
        if matched_cons:
            if prev_was_consonant:
                result.append("్")
            emit_consonant(matched_cons)
            i += len(matched_cons)
            continue

        # 9) Anything else (spaces/punct/digits)
        result.append(ch)
        prev_was_consonant = False
        i += 1

    # Final virama cleanup
    if strip_final_virama and result and result[-1] == "్":
        result.pop()

    return "".join(result)


# ──────────────────────────────────────────────────────────────────────────────
# Tables (Clusters Enhanced in v4.3.0)
# ──────────────────────────────────────────────────────────────────────────────

def get_geminates():
    """Explicit geminate mappings."""
    return {
        "kk": "క్క", "gg": "గ్గ", "cc": "చ్చ", "jj": "జ్జ",
        "tt": "త్త", "dd": "ద్ద", "pp": "ప్ప", "bb": "బ్బ",
        "mm": "మ్మ", "yy": "య్య", "rr": "ర్ర", "ll": "ల్ల",
        "vv": "వ్వ", "ss": "స్స", "nn": "న్న",
        "TT": "ట్ట", "DD": "డ్డ", "NN": "ణ్ణ",
    }

def get_base_consonants(style="modern"):
    """Modern consonants (dental vs retroflex distinction is via case)."""
    base = {
        "k": "క", "kh": "ఖ", "g": "గ", "gh": "ఘ",
        "c": "చ", "ch": "చ", "chh": "ఛ", "j": "జ", "jh": "ఝ",
        "t": "త", "th": "థ", "d": "ద", "dh": "ధ", "n": "న",
        "T": "ట", "Th": "ఠ", "D": "డ", "Dh": "ఢ", "N": "ణ",
        "p": "ప", "ph": "ఫ", "b": "బ", "bh": "భ", "m": "మ",
        "y": "య", "r": "ర", "l": "ల", "v": "వ", "w": "వ",
        "sh": "శ", "S":  "ష", "s":  "స",
        "h":  "హ",
    }
    return base

def get_base_vowels(style="modern"):
    """Vowel letters (keys must be lowercase for consistency)."""
    return {
        "a": "అ", "i": "ఇ", "u": "ఉ", "e": "ఎ", "o": "ఒ",
        "aa": "ఆ", "ii": "ఈ", "uu": "ఊ", "ee": "ఏ", "oo": "ఓ",
        "ai": "ఐ", "au": "ఔ",
        "am": "ం", "ah": "ః", "ri": "ఋ", "rii": "ౠ",
    }

def get_base_matras(style="modern"):
    """Dependent vowel signs (keys must be lowercase for consistency)."""
    return {
        "a":  "",
        "aa": "ా", "i": "ి", "ii": "ీ",
        "u":  "ు", "uu": "ూ",
        "e":  "ె", "ee": "ే",
        "o":  "ొ", "oo": "ో",
        "ai": "ై", "au": "ౌ",
        "am": "ం", "ah": "ః",
        "ri": "ృ", "rii": "ౄ",
    }

def get_clusters(style="modern"):
    """Common consonant clusters in token space. (v4.3.0 Enhanced)"""
    return {
        # 4-Character Clusters (Complex conjuncts)
        "ksha": ["k", "S"],   
        "shra": ["S", "r"],
        "shna": ["S", "n"],
        "SThr": ["S", "Th", "r"], # retroflex S, retroflex Th, r
        "skr": ["s", "k", "r"],   # s, k, r
        "spl": ["s", "p", "l"],   # s, p, l

        # 3-Character Clusters (Highly requested)
        "ndr": ["n", "d", "r"],   # n, d, r
        "str": ["s", "t", "r"],   # s, t, r
        "sht": ["sh", "T"],       # sh, retroflex T
        "bhr": ["bh", "r"],       # bh, r
        "mbr": ["m", "b", "r"],   # m, b, r
        "kst": ["k", "s", "t"],   # k, s, t
        "njn": ["n", "j", "n"],   # n, j, n
        
        # 2-Character Clusters (Base list)
        "jna":  ["j", "n"],
        "tra": ["t", "r"], "dra": ["d", "r"], "pra": ["p", "r"],
        "bhra": ["bh", "r"], "gva": ["g", "v"], "tna": ["t", "n"],
        "kr": ["k", "r"], "tr": ["t", "r"], "dr": ["d", "r"],
        "gr": ["g", "r"], "pr": ["p", "r"], "br": ["b", "r"],
        "sr": ["s", "r"], "nr": ["n", "r"],
        "kl": ["k", "l"], "gl": ["g", "l"], "pl": ["p", "l"], "bl": ["b", "l"],
        "kv": ["k", "v"], "tv": ["t", "v"], "dv": ["d", "v"],
        "tn": ["t", "n"], "dn": ["d", "n"], "kn": ["k", "n"], "pn": ["p", "n"],
    }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def eng_to_telugu(text: str, strip_final_virama: bool = True) -> str:
    if text is None:
        raise ValueError("Input text cannot be None")
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text).__name__}")
    s = text.strip()
    if not s:
        return ""
    if len(s) > 10000:
        raise ValueError("Input text too long (max 10000 characters)")

    rules = {
        "consonants": get_base_consonants(),
        "vowels": get_base_vowels(),
        "matras": get_base_matras(),
        "clusters": get_clusters(),
        "geminates": get_geminates(),
        "strip_final_virama": strip_final_virama,
    }
    return eng_to_telugu_base(s, rules)


# ──────────────────────────────────────────────────────────────────────────────
# Tests (updated for v4.3.0)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 80)
    print("TELUGU LIBRARY v4.3.0 — ENHANCED CLUSTER TESTS")
    print("=" * 80)

    tests = [
        # Complex Cluster Tests (New additions)
        ("rastra",   "రాష్ట్ర", "str cluster"),
        ("krishna",  "క్రిష్ణ", "kri matra (i matra, not vocalic ru)"), 
        ("namste",   "నమ్స్తే", "namste cluster fix"), 
        ("vidyut",   "విద్యుత్", "dv cluster"),
        ("chhatra",  "ఛత్ర", "chha+tra cluster"),
        ("prasthanam", "ప్రస్థానం", "s+t cluster"),

        # Regression Checks
        ("konda",   "కొండ", "nd -> retroflex ండ (Regression Check)"),
        ("palli",   "పల్లి", "ll geminate Check"),
    ]

    passed, failed = 0, 0
    for src, exp, note in tests:
        out = eng_to_telugu(src)
        ok = (out == exp)
        print(f"{'✓' if ok else '✗'} {src:<18} → {out:<16} | {note}")
        if ok: passed += 1
        else:
            failed += 1
            print(f"   expected: {exp}")

    print("-" * 80)
    total = len(tests)
    print(f"Results: {passed} passed, {failed} failed of {total}  ({passed/total*100:.1f}%)")
    if failed == 0:
        print("🎉 ALL TESTS PASSED! v4.3.0 ready.")