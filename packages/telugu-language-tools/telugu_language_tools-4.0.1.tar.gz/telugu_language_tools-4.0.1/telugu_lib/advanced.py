# ============================================================================
# PART 5: ADVANCED FEATURES & UTILITIES
# ============================================================================

from functools import lru_cache
import json
import os
from typing import List, Dict, Tuple, Optional, Union

# Import existing transliteration functions
from .transliterate import (
    eng_to_telugu_with_style,
    telugu_to_eng,
    semantic_match,
    compare_old_new_alphabets,
    get_semantic_dictionary
)

class TeluguEngineConfig:
    """Configuration manager for Telugu transliteration engine."""

    def __init__(self,
                 default_style: str = "modern",
                 enable_semantic_cache: bool = True,
                 enable_transliteration_cache: bool = True,
                 auto_detect_language: bool = True,
                 preserve_english_words: bool = True,
                 english_word_threshold: float = 0.8):
        """
        Args:
            default_style: Default alphabet style ("modern", "classical", "hybrid")
            enable_semantic_cache: Cache semantic dictionary lookups
            enable_transliteration_cache: Cache transliteration results
            auto_detect_language: Automatically detect input language
            preserve_english_words: Keep common English words untransliterated
            english_word_threshold: Threshold for detecting English words (0-1)
        """
        self.default_style = default_style
        self.enable_semantic_cache = enable_semantic_cache
        self.enable_transliteration_cache = enable_transliteration_cache
        self.auto_detect_language = auto_detect_language
        self.preserve_english_words = preserve_english_words
        self.english_word_threshold = english_word_threshold
        self._common_english_words = self._load_common_english_words()

    def _load_common_english_words(self) -> set:
        """Load common English words that should not be transliterated."""
        return {
            "the", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "shall",
            "and", "or", "but", "if", "then", "than", "because", "so",
            "a", "an", "in", "on", "at", "to", "for", "of", "with", "by",
            "from", "up", "about", "into", "through", "during", "before",
            "after", "above", "below", "between", "among", "i", "you", "he",
            "she", "it", "we", "they", "me", "him", "her", "us", "them",
            "my", "your", "his", "her", "its", "our", "their", "this", "that",
            "these", "those", "what", "which", "who", "when", "where", "why",
            "how", "all", "any", "both", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "than",
            "too", "very", "can", "just", "but", "also", "even", "ever", "still",
            "yet"
        }

# Global configuration instance
_config = TeluguEngineConfig()

def set_config(**kwargs):
    """Update global configuration."""
    global _config
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown config parameter: {key}")

def get_config():
    """Get current configuration."""
    return _config

@lru_cache(maxsize=1024)
def cached_eng_to_telugu(text: str, style: str) -> str:
    """Cached version of eng_to_telugu_with_style."""
    return eng_to_telugu_with_style(text, style)

@lru_cache(maxsize=1024)
def cached_telugu_to_eng(text: str) -> str:
    """Cached version of telugu_to_eng."""
    return telugu_to_eng(text)

def transliterate(text: str, style: Optional[str] = None) -> str:
    """
    Intelligent transliteration with auto-detection and caching.

    Args:
        text: Text to transliterate (English or Telugu)
        style: Alphabet style (auto-detected if None)

    Returns:
        Transliterated text
    """
    if not text or not text.strip():
        return ""

    # Auto-detect language if enabled
    if _config.auto_detect_language:
        is_telugu = any('\u0C00' <= ch <= '\u0C7F' for ch in text)
        if is_telugu:
            if _config.enable_transliteration_cache:
                return cached_telugu_to_eng(text)
            return telugu_to_eng(text)

    # English to Telugu
    style = style or _config.default_style

    # Check if word should be preserved
    if _config.preserve_english_words:
        words = text.split()
        if len(words) == 1 and words[0].lower() in _config._common_english_words:
            return text

    if _config.enable_transliteration_cache:
        return cached_eng_to_telugu(text, style)
    return eng_to_telugu_with_style(text, style)

def batch_transliterate(items: List[str],
                       style: Optional[str] = None,
                       show_progress: bool = False) -> List[str]:
    """
    Transliterate a list of strings efficiently.

    Args:
        items: List of strings to transliterate
        style: Alphabet style
        show_progress: Show progress bar

    Returns:
        List of transliterated strings
    """
    results = []
    total = len(items)

    for idx, item in enumerate(items):
        if show_progress and idx % 100 == 0:
            print(f"Processing... {idx}/{total} ({idx/total*100:.1f}%)")
        results.append(transliterate(item, style))

    return results

def batch_transliterate_dict(data: Dict[str, str],
                             style: Optional[str] = None) -> Dict[str, str]:
    """
    Transliterate dictionary values (preserves keys).

    Args:
        data: Dictionary with translatable values
        style: Alphabet style

    Returns:
        Dictionary with transliterated values
    """
    return {k: transliterate(v, style) for k, v in data.items()}

def process_file(input_path: str,
                 output_path: Optional[str] = None,
                 style: Optional[str] = None,
                 encoding: str = 'utf-8') -> str:
    """
    Transliterate entire file content.

    Args:
        input_path: Input file path
        output_path: Output file path (optional)
        style: Alphabet style
        encoding: File encoding

    Returns:
        Transliterated content
    """
    try:
        with open(input_path, 'r', encoding=encoding) as f:
            content = f.read()

        result = transliterate(content, style)

        if output_path:
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(result)
            print(f"✓ Written to {output_path}")

        return result
    except Exception as e:
        print(f"✗ Error processing file {input_path}: {str(e)}")
        return ""

# ============================================================================
# PART 6: ENHANCED SEMANTIC DICTIONARY
# ============================================================================

def get_enhanced_semantic_dictionary():
    """
    Extended dictionary with categories and metadata.

    Returns:
        Dictionary with structure:
        {
            "category": {
                "english": ["telugu1", "telugu2", ...],
                ...
            }
        }
    """
    return {
        "pronouns": {
            "i": ["నేను"], "you": ["నువ్వు", "మీరు"], "he": ["అతను"],
            "she": ["ఆమె"], "it": ["అది"], "we": ["మనం", "మేము"],
            "they": ["వాళ్లు"], "me": ["నన్ను"], "him": ["అతన్ని"],
            "her": ["ఆమెను"], "us": ["మమ్మల్ని"], "them": ["వాళ్ళను"],
        },
        "verbs": {
            "go": ["వెళ్ళు"], "come": ["వచ్చు"], "eat": ["తిను"],
            "drink": ["తాగు"], "sleep": ["నిద్ర పో"], "see": ["చూడు"],
            "do": ["చేయి"], "say": ["చెప్పు"], "get": ["పొందు"],
            "make": ["తయారు చేయి"], "know": ["తెలుసు"], "think": ["అనుకో"],
        },
        "directions": {
            "up": ["పైకి"], "down": ["కిందికి"], "left": ["ఎడమ"],
            "right": ["కుడి"], "north": ["ఉత్తరం"], "south": ["దక్షిణం"],
            "east": ["తూర్పు"], "west": ["పశ్చిమం"], "front": ["ముందు"],
            "back": ["వెనుక"], "inside": ["లోపల"], "outside": ["బయట"],
        },
        "time": {
            "today": ["ఈరోజు"], "tomorrow": ["రేపు"], "yesterday": ["నిన్న"],
            "now": ["ఇప్పుడు"], "later": ["తర్వాత"], "soon": ["త్వరలో"],
            "morning": ["ఉదయం"], "evening": ["సాయంత్రం"], "night": ["రాత్రి"],
            "day": ["ఈదుర"], "week": ["వారం"], "month": ["నెల"], "year": ["సంవత్సరం"],
        },
        "food": {
            "rice": ["అన్నం"], "bread": ["రొట్టె"], "milk": ["పాలు"],
            "water": ["నీరు"], "curry": ["కూర"], "vegetable": ["కూరగాయ"],
            "fruit": ["పండు"], "sweet": ["ఇనిపిండి"], "salt": ["ఉప్పు"],
        },
        "emotions": {
            "happy": ["సంతోషం"], "sad": ["దుఃఖం"], "angry": ["కోపం"],
            "love": ["ప్రేమ"], "hate": ["ద్వేషం"], "fear": ["భయం"],
            "hope": ["భావన"], "worry": ["చింత"], "surprise": ["ఆశ్చర్యం"],
        },
        "technology": {
            "computer": ["కంప్యూటర్"], "phone": ["ఫోను"], "internet": ["ఇంటర్నెట్"],
            "email": ["ఈమెయిల్"], "website": ["వెబ్సైటు"], "video": ["వీడియో"],
            "audio": ["ఆడియో"], "data": ["డేటా"], "software": ["సాఫ్ట్‌వేర్"],
        },
        "common_phrases": {
            "good morning": ["శుభోదయం"], "good night": ["శుభరాత్రి"],
            "thank you": ["ధన్యవాదాలు"], "excuse me": ["క్షమించండి"],
            "how are you": ["మీరు ఎలా ఉన్నారు"], "i am fine": ["నేను బాగున్నాను"],
            "what is your name": ["మీ పేరు ఏమిటి"], "my name is": ["నా పేరు"],
        }
    }

def get_semantic_dictionary_by_category(category: str) -> Dict[str, List[str]]:
    """Get semantic dictionary for a specific category."""
    enhanced = get_enhanced_semantic_dictionary()
    return enhanced.get(category, {})

def search_semantic_dictionary(query: str,
                             category: Optional[str] = None) -> List[Tuple[str, str]]:
    """
    Search for words in semantic dictionary.

    Args:
        query: Search query (partial match)
        category: Specific category to search

    Returns:
        List of (english, telugu) matches
    """
    results = []
    enhanced = get_enhanced_semantic_dictionary()

    if category:
        categories = [category]
    else:
        categories = enhanced.keys()

    for cat in categories:
        for eng, tel_list in enhanced[cat].items():
            if query.lower() in eng.lower():
                for tel in tel_list:
                    results.append((eng, tel))

    return results

# ============================================================================
# PART 7: COMPREHENSIVE TEST SUITE
# ============================================================================

def run_comprehensive_tests():
    """Run all tests and report results."""

    tests_passed = 0
    tests_failed = 0
    failures = []

    print("=" * 80)
    print("COMPREHENSIVE TEST SUITE")
    print("=" * 80)

    # Test 1: Basic transliteration
    print("\n[TEST 1] Basic Transliteration")
    test_cases = [
        ("rama", "రామ", "modern"),
        ("krishna", "కృష్ణ", "modern"),
        ("lakshmi", "లక్ష్మి", "modern"),
        ("shiva", "శివ", "modern"),
        ("ganesha", "గణేశ", "modern"),
        ("anjaneya", "అంజనేయ", "modern"),
    ]

    for eng, expected, style in test_cases:
        result = eng_to_telugu_with_style(eng, style)
        if result == expected:
            print(f"  ✓ {eng:12} → {result}")
            tests_passed += 1
        else:
            print(f"  ✗ {eng:12} → {result} (expected {expected})")
            tests_failed += 1
            failures.append(f"Basic: {eng} → {result} != {expected}")

    # Test 2: Classical style
    print("\n[TEST 2] Classical Style")
    classical_cases = [
        ("rama", "రామ", "classical"),
        ("karma", "కర్మ", "classical"),
        ("yantra", "యంత్ర", "classical"),
    ]

    for eng, expected, style in classical_cases:
        result = eng_to_telugu_with_style(eng, style)
        if result == expected:
            print(f"  ✓ {eng:12} → {result}")
            tests_passed += 1
        else:
            print(f"  ✗ {eng:12} → {result} (expected {expected})")
            tests_failed += 1
            failures.append(f"Classical: {eng} → {result} != {expected}")

    # Test 3: Telugu to English
    print("\n[TEST 3] Telugu to English")
    telugu_cases = [
        ("కృష్ణ", "krishna"),
        ("ఎవరు", "evaru"),
        ("లక్ష్మి", "lakshmi"),
        ("రామ", "rama"),
        ("శివ", "shiva"),
    ]

    for tel, expected in telugu_cases:
        result = telugu_to_eng(tel)
        if result == expected:
            print(f"  ✓ {tel:8} → {result}")
            tests_passed += 1
        else:
            print(f"  ✗ {tel:8} → {result} (expected {expected})")
            tests_failed += 1
            failures.append(f"Tel→Eng: {tel} → {result} != {expected}")

    # Test 4: Semantic matching
    print("\n[TEST 4] Semantic Matching")
    semantic_cases = [
        ("who", ["ఎవరు", "ఎవరో"]),
        ("mother", ["అమ్మ", "తల్లి"]),
        ("krishna", ["కృష్ణ", "కృష్ణుడు"]),
    ]

    for eng, expected_list in semantic_cases:
        result = semantic_match(eng)
        if any(exp in result['matches'] for exp in expected_list):
            print(f"  ✓ {eng:10} → {result['matches']}")
            tests_passed += 1
        else:
            print(f"  ✗ {eng:10} → {result['matches']} (expected one of {expected_list})")
            tests_failed += 1
            failures.append(f"Semantic: {eng} → {result['matches']} not in {expected_list}")

    # Test 5: Sentence processing
    print("\n[TEST 5] Sentence Processing")
    from .transliterate import eng_to_telugu_sentence
    sentence_cases = [
        ("hello world", "హలో వర్ల్ద"),
        ("who is rama", "ఎవరు ఇస్ రామ"),
        ("thank you", "ధన్యవాదాలు"),
    ]

    for eng, expected in sentence_cases:
        result = eng_to_telugu_sentence(eng)
        if result == expected:
            print(f"  ✓ '{eng}' → '{result}'")
            tests_passed += 1
        else:
            print(f"  ✗ '{eng}' → '{result}' (expected '{expected}')")
            tests_failed += 1
            failures.append(f"Sentence: '{eng}' → '{result}' != '{expected}'")

    # Test 6: Edge cases
    print("\n[TEST 6] Edge Cases")
    edge_cases = [
        ("", ""),  # Empty string
        ("   ", ""),  # Whitespace
        ("123", "123"),  # Numbers
        ("hello!", "హలో!"),  # Punctuation
        ("mixed123", "మిక్సెడ్123"),  # Alphanumeric
    ]

    for eng, expected in edge_cases:
        result = eng_to_telugu_sentence(eng)
        if result == expected:
            print(f"  ✓ '{eng}' → '{result}'")
            tests_passed += 1
        else:
            print(f"  ✗ '{eng}' → '{result}' (expected '{expected}')")
            tests_failed += 1
            failures.append(f"Edge: '{eng}' → '{result}' != '{expected}'")

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"Passed: {tests_passed}")
    print(f"Failed: {tests_failed}")
    print(f"Success Rate: {tests_passed/(tests_passed + tests_failed)*100:.1f}%")

    if failures:
        print("\nFailed Tests:")
        for failure in failures:
            print(f"  - {failure}")

    print("=" * 80)

    return tests_failed == 0

# ============================================================================
# PART 8: COMMAND-LINE INTERFACE
# ============================================================================

def main_cli(argv=None):
    """Command-line interface for Telugu transliteration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Telugu Library v2.1 - Transliteration Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m telugu_lib.advanced --text "krishna"
  python -m telugu_lib.advanced --text "కృష్ణ" --reverse
  python -m telugu_lib.advanced --file input.txt --output output.txt
  python -m telugu_lib.advanced --style classical --sentence "rama is great"
  python -m telugu_lib.advanced --test
  python -m telugu_lib.advanced --search "who"
        """
    )

    parser.add_argument("--text", "-t", help="Text to transliterate")
    parser.add_argument("--file", "-f", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--reverse", "-r", action="store_true", help="Telugu to English")
    parser.add_argument("--style", "-s", choices=["modern", "classical", "hybrid"],
                       default="modern", help="Alphabet style")
    parser.add_argument("--sentence", help="Process as sentence")
    parser.add_argument("--test", action="store_true", help="Run comprehensive tests")
    parser.add_argument("--search", help="Search semantic dictionary")
    parser.add_argument("--category", help="Filter by category (with --search)")
    parser.add_argument("--compare", action="store_true", help="Show alphabet comparison")
    parser.add_argument("--batch", nargs="+", help="Batch transliterate multiple texts")

    args = parser.parse_args(argv)

    # Handle different modes
    if args.test:
        success = run_comprehensive_tests()
        exit(0 if success else 1)

    elif args.compare:
        compare_old_new_alphabets()
        exit(0)

    elif args.search:
        results = search_semantic_dictionary(args.search, args.category)
        if results:
            print(f"\nSearch results for '{args.search}':")
            for eng, tel in results:
                print(f"  {eng:20} → {tel}")
        else:
            print(f"No results found for '{args.search}'")
        exit(0)

    elif args.batch:
        results = batch_transliterate(args.batch, args.style)
        print("\nBatch Transliteration Results:")
        for orig, trans in zip(args.batch, results):
            print(f"  {orig:20} → {trans}")
        exit(0)

    elif args.file:
        result = process_file(args.file, args.output, args.style)
        if not args.output:
            print(result)
        exit(0)

    elif args.sentence:
        from .transliterate import eng_to_telugu_sentence
        result = eng_to_telugu_sentence(args.sentence, args.style)
        print(result)
        exit(0)

    elif args.text:
        if args.reverse:
            result = telugu_to_eng(args.text)
        else:
            result = transliterate(args.text, args.style)
        print(result)
        exit(0)

    else:
        parser.print_help()
        exit(1)

# ============================================================================
# PART 9: WEB API INTERFACE (Flask)
# ============================================================================

def create_web_api():
    """
    Create a Flask web API for transliteration.
    Usage: python -m telugu_lib.advanced --serve
    """
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("Flask is not installed. Install with: pip install flask")
        return None

    app = Flask(__name__)

    @app.route('/transliterate', methods=['POST'])
    def api_transliterate():
        """API endpoint for transliteration."""
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400

        text = data['text']
        style = data.get('style', 'modern')
        direction = data.get('direction', 'auto')

        try:
            if direction == 'telugu_to_eng':
                result = telugu_to_eng(text)
            elif direction == 'eng_to_telugu':
                result = eng_to_telugu_with_style(text, style)
            else:  # auto-detect
                result = transliterate(text, style)

            return jsonify({
                'success': True,
                'text': text,
                'result': result,
                'style': style
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/semantic', methods=['POST'])
    def api_semantic():
        """API endpoint for semantic matching."""
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({'error': 'Missing required field: text'}), 400

        text = data['text']

        try:
            result = semantic_match(text)
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/search', methods=['GET'])
    def api_search():
        """API endpoint for dictionary search."""
        query = request.args.get('q', '')
        category = request.args.get('category')

        try:
            results = search_semantic_dictionary(query, category)
            return jsonify({
                'success': True,
                'query': query,
                'results': [{'english': eng, 'telugu': tel} for eng, tel in results]
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/health', methods=['GET'])
    def api_health():
        """Health check endpoint."""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'version': '3.5.2'
        })

    return app

def serve_web_api(host='localhost', port=5000, debug=False):
    """Start the web API server."""
    app = create_web_api()
    if app is None:
        print("Error: Cannot start web API. Please install Flask: pip install flask")
        return False
    
    try:
        print(f"Starting Telugu API server on http://{host}:{port}")
        print("Endpoints:")
        print("  POST /transliterate - Transliterate text")
        print("  POST /semantic - Get semantic matches")
        print("  GET  /search?q=<query> - Search dictionary")
        print("  GET  /health - Health check")
        app.run(host=host, port=port, debug=debug)
        return True
    except Exception as e:
        print(f"Error starting web server: {e}")
        return False

# ============================================================================
# PART 10: PERFORMANCE MONITORING
# ============================================================================

class PerformanceMonitor:
    """Monitor and report transliteration performance."""

    def __init__(self):
        self.stats = {
            'transliterations': 0,
            'cache_hits': 0,
            'semantic_lookups': 0,
            'avg_time': 0.0
        }
        self._start_time = None

    def start(self):
        """Start timing."""
        import time
        self._start_time = time.time()

    def end(self, operation: str = 'transliteration'):
        """End timing and update stats."""
        import time
        if self._start_time:
            duration = time.time() - self._start_time
            self.stats['avg_time'] = (self.stats['avg_time'] * self.stats['transliterations'] + duration) / (self.stats['transliterations'] + 1)
            self._start_time = None

    def record_cache_hit(self):
        """Record a cache hit."""
        self.stats['cache_hits'] += 1

    def record_semantic_lookup(self):
        """Record a semantic lookup."""
        self.stats['semantic_lookups'] += 1

    def get_report(self) -> dict:
        """Get performance report."""
        total_ops = self.stats['transliterations'] + self.stats['cache_hits']
        hit_rate = (self.stats['cache_hits'] / total_ops * 100) if total_ops > 0 else 0

        return {
            **self.stats,
            'cache_hit_rate': hit_rate,
            'total_operations': total_ops
        }

# Global performance monitor
_perf_monitor = PerformanceMonitor()

def get_performance_report():
    """Get current performance statistics."""
    return _perf_monitor.get_report()

def reset_performance_stats():
    """Reset performance statistics."""
    global _perf_monitor
    _perf_monitor = PerformanceMonitor()

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys

    # Check for web serve mode
    if '--serve' in sys.argv:
        idx = sys.argv.index('--serve')
        host = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else 'localhost'
        port = int(sys.argv[idx + 2]) if len(sys.argv) > idx + 2 else 5000
        serve_web_api(host, port)
    else:
        # Run CLI with all arguments except the script name
        main_cli()
