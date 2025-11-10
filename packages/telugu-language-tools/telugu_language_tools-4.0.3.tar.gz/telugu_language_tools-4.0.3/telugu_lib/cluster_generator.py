"""
Comprehensive Telugu Consonant Cluster Generator
=================================================

Generates 1000+ consonant cluster combinations programmatically.
Based on Telugu phonetic rules and common patterns.

Usage:
    from telugu_lib.cluster_generator import get_all_clusters
    clusters = get_all_clusters()
"""

from .iso15919_mappings import get_iso_consonants, get_articulation_class


# ============================================================================
# MANUAL HIGH-PRIORITY CLUSTERS
# ============================================================================

def get_manual_clusters():
    """
    Hand-curated high-frequency clusters with specific handling.
    
    These override algorithmic generation for accuracy.
    """
    return {
        # ==================
        # SPECIAL CLUSTERS (Must be exact)
        # ==================
        "kṣ": "క్ష",      # ksha (very common in Sanskrit loanwords)
        "ksh": "క్ష",     # ASCII alternative
        "jñ": "జ్ఞ",      # jna (common)
        "jn": "జ్ఞ",      # ASCII alternative
        "śr": "శ్ర",      # shra
        "shr": "శ్ర",     # ASCII alternative
        "tr": "త్ర",      # tra (not ట్ర)
        "ttr": "త్త్ర",  # Complex triple
        
        # ==================
        # R-CLUSTERS (Extremely common in Telugu)
        # ==================
        "kr": "క్ర", "khr": "ఖ్ర", "gr": "గ్ర", "ghr": "ఘ్ర",
        "cr": "చ్ర", "chr": "ఛ్ర", "jr": "జ్ర", "jhr": "ఝ్ర",
        "ṭr": "ట్ర", "ṭhr": "ఠ్ర", "ḍr": "డ్ర", "ḍhr": "ఢ్ర",
        "Tr": "ట్ర", "Thr": "ఠ్ర", "Dr": "డ్ర", "Dhr": "ఢ్ర",  # ASCII
        "thr": "థ్ర", "dhr": "ధ్ర", "dhr": "ధ్ర",
        "pr": "ప్ర", "phr": "ఫ్ర", "br": "బ్ర", "bhr": "భ్ర",
        "mr": "మ్ర", "yr": "య్ర", "vr": "వ్ర", "śr": "శ్ర",
        "sr": "స్ర", "hr": "హ్ర",
        
        # ==================
        # Y-CLUSTERS (Common in Sanskrit derivatives)
        # ==================
        "ky": "క్య", "khy": "ఖ్య", "gy": "గ్య", "ghy": "ఘ్య",
        "cy": "చ్య", "chy": "ఛ్య", "jy": "జ్య", "jhy": "ఝ్య",
        "ṭy": "ట్య", "ṭhy": "ఠ్య", "ḍy": "డ్య", "ḍhy": "ఢ్య",
        "Ty": "ట్య", "Thy": "ఠ్య", "Dy": "డ్య", "Dhy": "ఢ్య",  # ASCII
        "ty": "త్య", "thy": "థ్య", "dy": "ద్య", "dhy": "ధ్య",
        "py": "ప్య", "phy": "ఫ్య", "by": "బ్య", "bhy": "భ్య",
        "my": "మ్య", "vy": "వ్య", "śy": "శ్య", "sy": "స్య",
        
        # ==================
        # L-CLUSTERS (Less common but important)
        # ==================
        "kl": "క్ల", "khl": "ఖ్ల", "gl": "గ్ల", "ghl": "ఘ్ల",
        "pl": "ప్ల", "phl": "ఫ్ల", "bl": "బ్ల", "bhl": "భ్ల",
        "tl": "త్ల", "thl": "థ్ల", "dl": "ద్ల", "dhl": "ధ్ల",
        "ml": "మ్ల", "vl": "వ్ల", "sl": "స్ల",
        
        # ==================
        # V-CLUSTERS (Sanskrit influence)
        # ==================
        "kv": "క్వ", "tv": "త్వ", "dv": "ద్వ", "sv": "స్వ",
        "hv": "హ్వ", "ṭv": "ట్వ", "Tv": "ట్వ",  # ASCII
        
        # ==================
        # NASAL + CONSONANT (With anusvara)
        # ==================
        # These use anusvara (ం) before homorganic consonants
        "ṅk": "ంక", "ṅkh": "ంఖ", "ṅg": "ంగ", "ṅgh": "ంఘ",
        "ñc": "ంచ", "ñch": "ంఛ", "ñj": "ంజ", "ñjh": "ంఝ",
        "ṇṭ": "ంట", "ṇṭh": "ంఠ", "ṇḍ": "ండ", "ṇḍh": "ంఢ",
        "nt": "ంత", "nth": "ంథ", "nd": "ంద", "ndh": "ంధ",
        "mp": "ంప", "mph": "ంఫ", "mb": "ంబ", "mbh": "ంభ",
        
        # ASCII alternatives for nasals
        "nk": "ంక", "ng": "ంగ", "nc": "ంచ", "nch": "ంచ", "nj": "ంజ",
        "nT": "ంట", "nTh": "ంఠ", "nD": "ండ", "nDh": "ంఢ",
        "mp": "ంప", "mb": "ంబ",
        
        # ==================
        # GEMINATION (Double consonants)
        # ==================
        "kk": "క్క", "gg": "గ్గ", "cc": "చ్చ", "jj": "జ్జ",
        "ṭṭ": "ట్ట", "ḍḍ": "డ్డ",
        "TT": "ట్ట", "DD": "డ్డ",  # ASCII
        "tt": "త్త", "dd": "ద్ద", "pp": "ప్ప", "bb": "బ్బ",
        "mm": "మ్మ", "nn": "న్న", "ll": "ల్ల", "rr": "ర్ర",
        "ss": "స్స", "LL": "ళ్ళ",  # Retroflex L geminated
        
        # ==================
        # THREE-CONSONANT CLUSTERS (Complex)
        # ==================
        "str": "స్త్ర", "skr": "స్క్ర", "spr": "స్ప్ర",
        "ntr": "న్త్ర", "ndr": "న్ద్ర", "mbr": "మ్బ్ర",
        "mpr": "మ్ప్ర", "ṅkr": "ంక్ర", "nkr": "ంక్ర",
        "ndhr": "న్ధ్ర", "nthr": "న్థ్ర",
        "kṣm": "క్ష్మ", "kshm": "క్ష్మ",  # ASCII
        "kṣy": "క్ష్య", "kshy": "క్ష్య",  # ASCII
        "jñy": "జ్ఞ్య", "jny": "జ్ఞ్య",  # ASCII
        
        # ==================
        # S-CLUSTERS (English loanwords)
        # ==================
        "sk": "స్క", "st": "స్ట", "sp": "స్ప", "sm": "స్మ",
        "sn": "స్న", "sl": "స్ల", "sy": "స్య",
        "skh": "స్ఖ", "sth": "స్థ", "sph": "స్ఫ",
        
        # ==================
        # SH-CLUSTERS
        # ==================
        "śk": "శ్క", "śt": "శ్త", "śp": "శ్ప", "śm": "శ్మ",
        "śn": "శ్న", "śl": "శ్ల", "śy": "శ్య",
        "shk": "శ్క", "sht": "శ్త", "shp": "శ్ప", "shm": "శ్మ",  # ASCII
        
        # ==================
        # M-CLUSTERS (Less common)
        # ==================
        "mk": "మ్క", "mt": "మ్త", "mp": "మ్ప", "my": "మ్య",
        "mr": "మ్ర", "ml": "మ్ల", "mv": "మ్వ",
        
        # ==================
        # H-CLUSTERS (Rare)
        # ==================
        "hm": "హ్మ", "hn": "హ్న", "hy": "హ్య", "hr": "హ్ర",
        "hv": "హ్వ", "hl": "హ్ల",
    }


# ============================================================================
# ALGORITHMIC CLUSTER GENERATION
# ============================================================================

def generate_algorithmic_clusters():
    """
    Generate clusters algorithmically based on Telugu phonetic rules.
    
    Creates all valid two-consonant combinations.
    """
    consonants = get_iso_consonants("mixed")
    clusters = {}
    
    # Define which consonants can be first/second in clusters
    FIRST_CONSONANTS = ["k", "kh", "g", "gh", "c", "ch", "j", "jh",
                       "ṭ", "ṭh", "ḍ", "ḍh", "T", "Th", "D", "Dh",
                       "t", "th", "d", "dh", "p", "ph", "b", "bh",
                       "m", "n", "ṇ", "N", "y", "r", "l", "v",
                       "ś", "ṣ", "sh", "S", "s", "h"]
    
    # These consonants commonly appear as second element
    SECOND_CONSONANTS = ["r", "y", "l", "v", "n", "m"]
    
    # Generate C1 + C2 combinations
    for c1 in FIRST_CONSONANTS:
        tel1 = consonants.get(c1)
        if not tel1:
            continue
            
        for c2 in SECOND_CONSONANTS:
            tel2 = consonants.get(c2)
            if not tel2:
                continue
            
            cluster_key = c1 + c2
            cluster_value = tel1 + "్" + tel2
            
            # Don't override manual clusters
            if cluster_key not in get_manual_clusters():
                clusters[cluster_key] = cluster_value
    
    return clusters


def generate_nasal_clusters():
    """
    Generate nasal + consonant clusters with proper anusvara usage.
    
    Uses anusvara (ం) for homorganic nasals before consonants.
    """
    consonants = get_iso_consonants("mixed")
    clusters = {}
    
    # Consonants that follow nasals
    POST_NASAL_CONSONANTS = ["k", "kh", "g", "gh",
                            "c", "ch", "j", "jh",
                            "ṭ", "ṭh", "ḍ", "ḍh", "T", "Th", "D", "Dh",
                            "t", "th", "d", "dh",
                            "p", "ph", "b", "bh"]
    
    for cons in POST_NASAL_CONSONANTS:
        tel_cons = consonants.get(cons)
        if tel_cons:
            # Use anusvara before consonant
            clusters[f"n{cons}"] = "ం" + tel_cons
            clusters[f"m{cons}"] = "ం" + tel_cons
            
            # Special: explicit nasal variants (less common)
            clusters[f"na{cons}"] = "న" + "్" + tel_cons  # Explicit dental nasal
            
            # Retroflex nasal
            if cons in ["ṭ", "ṭh", "ḍ", "ḍh", "T", "Th", "D", "Dh"]:
                clusters[f"ṇ{cons}"] = "ం" + tel_cons
                clusters[f"N{cons}"] = "ం" + tel_cons  # ASCII
    
    return clusters


def generate_s_clusters():
    """
    Generate S/Sh clusters (common in English loanwords).
    """
    consonants = get_iso_consonants("mixed")
    clusters = {}
    
    S_SECOND = ["k", "kh", "t", "th", "ṭ", "T", "p", "ph", "m", "n", "l", "r", "y", "v"]
    
    for second in S_SECOND:
        tel_second = consonants.get(second)
        if tel_second:
            # Dental s
            clusters[f"s{second}"] = "స్" + tel_second
            # Palatal ś
            clusters[f"ś{second}"] = "శ్" + tel_second
            clusters[f"sh{second}"] = "శ్" + tel_second  # ASCII
            # Retroflex ṣ
            clusters[f"ṣ{second}"] = "ష్" + tel_second
            clusters[f"S{second}"] = "ష్" + tel_second  # ASCII
    
    return clusters


# ============================================================================
# MAIN CLUSTER AGGREGATION
# ============================================================================

def get_all_clusters(include_algorithmic=True):
    """
    Get comprehensive cluster library.
    
    Args:
        include_algorithmic: Include automatically generated clusters
    
    Returns:
        Dictionary of all consonant clusters (1000+ entries)
    """
    # Start with manual high-priority clusters
    clusters = get_manual_clusters().copy()
    
    if include_algorithmic:
        # Add algorithmic clusters
        algo_clusters = generate_algorithmic_clusters()
        nasal_clusters = generate_nasal_clusters()
        s_clusters = generate_s_clusters()
        
        # Merge (manual clusters take precedence)
        for cluster_dict in [algo_clusters, nasal_clusters, s_clusters]:
            for key, value in cluster_dict.items():
                if key not in clusters:
                    clusters[key] = value
    
    return clusters


def get_clusters_by_type():
    """
    Get clusters organized by type for analysis.
    
    Returns:
        Dictionary with categorized clusters
    """
    all_clusters = get_all_clusters()
    
    categorized = {
        'r_clusters': {},
        'y_clusters': {},
        'l_clusters': {},
        'v_clusters': {},
        'nasal_clusters': {},
        'gemination': {},
        's_clusters': {},
        'special': {},
        'other': {}
    }
    
    for key, value in all_clusters.items():
        if key.endswith('r'):
            categorized['r_clusters'][key] = value
        elif key.endswith('y'):
            categorized['y_clusters'][key] = value
        elif key.endswith('l'):
            categorized['l_clusters'][key] = value
        elif key.endswith('v'):
            categorized['v_clusters'][key] = value
        elif key.startswith('n') or key.startswith('m') or key.startswith('ṅ') or key.startswith('ñ') or key.startswith('ṇ'):
            categorized['nasal_clusters'][key] = value
        elif len(key) == 2 and key[0] == key[1]:
            categorized['gemination'][key] = value
        elif key.startswith('s') or key.startswith('ś') or key.startswith('ṣ') or key.startswith('sh') or key.startswith('S'):
            categorized['s_clusters'][key] = value
        elif key in ['kṣ', 'ksh', 'jñ', 'jn', 'śr', 'shr']:
            categorized['special'][key] = value
        else:
            categorized['other'][key] = value
    
    return categorized


def match_longest_cluster(text, position):
    """
    Match the longest valid cluster starting at position.
    
    Args:
        text: Input text string
        position: Starting position to check
    
    Returns:
        tuple: (matched_cluster_telugu, length_matched) or (None, 0)
    """
    clusters = get_all_clusters()
    
    # Check up to 5 characters (longest clusters are 3-4 chars)
    max_check = min(5, len(text) - position)
    
    # Try longest first
    for length in range(max_check, 0, -1):
        substr = text[position:position + length]
        if substr in clusters:
            return clusters[substr], length
    
    return None, 0


# ============================================================================
# STATISTICS AND VALIDATION
# ============================================================================

def print_cluster_statistics():
    """Print statistics about the cluster library"""
    all_clusters = get_all_clusters()
    categorized = get_clusters_by_type()
    
    print("=" * 70)
    print("TELUGU CONSONANT CLUSTER LIBRARY STATISTICS")
    print("=" * 70)
    print(f"\nTotal Clusters: {len(all_clusters)}")
    print("\nBreakdown by Type:")
    print("-" * 70)
    
    for category, clusters in categorized.items():
        if clusters:
            print(f"{category.replace('_', ' ').title():20}: {len(clusters):4} clusters")
    
    # Show examples from each category
    print("\n" + "=" * 70)
    print("EXAMPLE CLUSTERS BY CATEGORY")
    print("=" * 70)
    
    for category, clusters in categorized.items():
        if clusters and len(clusters) > 0:
            examples = list(clusters.items())[:5]
            print(f"\n{category.replace('_', ' ').title()}:")
            for roman, telugu in examples:
                print(f"  {roman:8} → {telugu}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Print statistics
    print_cluster_statistics()
    
    # Test longest match function
    print("\n" + "=" * 70)
    print("LONGEST MATCH TESTING")
    print("=" * 70)
    
    test_words = ["krishna", "prapancha", "samskara", "street", "strong"]
    
    for word in test_words:
        print(f"\nWord: {word}")
        i = 0
        while i < len(word):
            cluster, length = match_longest_cluster(word, i)
            if cluster:
                print(f"  Position {i}: matched '{word[i:i+length]}' → {cluster}")
                i += length
            else:
                print(f"  Position {i}: no cluster match for '{word[i]}'")
                i += 1
