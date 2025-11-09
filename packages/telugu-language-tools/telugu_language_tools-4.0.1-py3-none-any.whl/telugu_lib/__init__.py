"""
telugu_lib - A simple Telugu language helper library

This library provides utilities for working with Telugu text including:
- Transliteration between English and Telugu
- Text analysis and character counting
- Text statistics and validation
"""

from .transliterate import (
    # Core transliteration (v0.9 backwards compatible)
    eng_to_telugu,
    telugu_to_eng,
    # Old vs New alphabet styles (v1.0)
    eng_to_telugu_with_style,
    eng_to_telugu_old_new_options,
    compare_old_new_alphabets,
    # Semantic matching (v2.0)
    semantic_match,
    bidirectional_search,
    get_semantic_dictionary,
    # Sentence handling (v2.0)
    eng_to_telugu_sentence,
    generate_word_variations,
)
from .text_tools import (
    count_telugu_chars,
    count_english_chars,
    count_digits,
    is_telugu_text,
    split_telugu_words,
    get_text_stats
)
from .advanced import (
    # Configuration management
    TeluguEngineConfig,
    set_config,
    get_config,
    # Caching and utilities
    transliterate,
    batch_transliterate,
    batch_transliterate_dict,
    process_file,
    # Enhanced semantic dictionary
    get_enhanced_semantic_dictionary,
    get_semantic_dictionary_by_category,
    search_semantic_dictionary,
    # Testing
    run_comprehensive_tests,
    # Performance monitoring
    PerformanceMonitor,
    get_performance_report,
    reset_performance_stats,
)

# Import sentence tools (with graceful handling if not available)
try:
    from .sentence_tools import (
        find_similar_sentence,
        correct_sentence,
        rank_sentences,
        batch_similarity,
        is_sentence_transformers_available
    )
    SENTENCE_TOOLS_AVAILABLE = True
except ImportError:
    SENTENCE_TOOLS_AVAILABLE = False

__version__ = "4.0.1"
__author__ = "Your Name"
__email__ = "your@email.com"

__all__ = [
    # Core transliteration (v0.9 backwards compatible)
    "eng_to_telugu",
    "telugu_to_eng",
    # Old vs New alphabet styles (v1.0)
    "eng_to_telugu_with_style",
    "eng_to_telugu_old_new_options",
    "compare_old_new_alphabets",
    # Semantic matching (v2.0)
    "semantic_match",
    "bidirectional_search",
    "get_semantic_dictionary",
    # Sentence handling (v2.0)
    "eng_to_telugu_sentence",
    "generate_word_variations",
    # Text tools
    "count_telugu_chars",
    "count_english_chars",
    "count_digits",
    "is_telugu_text",
    "split_telugu_words",
    "get_text_stats",
    # Advanced features
    "TeluguEngineConfig",
    "set_config",
    "get_config",
    "transliterate",
    "batch_transliterate",
    "batch_transliterate_dict",
    "process_file",
    "get_enhanced_semantic_dictionary",
    "get_semantic_dictionary_by_category",
    "search_semantic_dictionary",
    "run_comprehensive_tests",
    "PerformanceMonitor",
    "get_performance_report",
    "reset_performance_stats",
]

if SENTENCE_TOOLS_AVAILABLE:
    __all__.extend([
        "find_similar_sentence",
        "correct_sentence",
        "rank_sentences",
        "batch_similarity",
        "is_sentence_transformers_available"
    ])
