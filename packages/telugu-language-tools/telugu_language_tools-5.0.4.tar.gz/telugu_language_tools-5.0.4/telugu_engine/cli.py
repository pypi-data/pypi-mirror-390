"""
Command-line interface for Telugu Engine
"""

from __future__ import annotations

import sys
from typing import List, Tuple


def parse_args(argv: List[str]) -> Tuple[str, str, str, bool]:
    """
    Parse command-line arguments.

    Returns:
        (subject, root, tense, auto_mode)
    """
    auto_mode = False

    # Check for --auto flag
    if "--auto" in argv:
        auto_mode = True
        argv = [arg for arg in argv if arg != "--auto"]

    # Check for --help flag
    if "--help" in argv or "-h" in argv:
        print("""
Telugu Engine - Convert English to Telugu with tense formation

Usage:
    python -m telugu_engine.cli <subject> <root> <tense> [--auto]

Arguments:
    subject     The subject (e.g., 'amma', 'nenu')
    root        The verb root (e.g., 'tina', 'ceyu')
    tense       The tense (past, present, future)

Options:
    --auto      Automatically select the first option (non-interactive mode)
    --help, -h  Show this help message

Examples:
    python -m telugu_engine.cli amma tina past
    python -m telugu_engine.cli amma tina past --auto
        """)
        sys.exit(0)

    # Check if we have enough args
    if len(argv) < 3:
        print("Error: Need 3 arguments: <subject> <root> <tense>")
        print("Use --help for usage information")
        sys.exit(2)

    subject, root, tense = argv[0], argv[1], argv[2]
    return subject, root, tense, auto_mode


def main(argv: List[str] | None = None) -> int:
    """Main CLI entry point."""
    argv = argv if argv is not None else sys.argv[1:]

    try:
        subject, root, tense, auto_mode = parse_args(argv)
    except SystemExit:
        # Help was shown, exit with 0
        return 0

    from .phonetic_matrix import map_sound
    from .tense_engine import build_tense
    from .transliterator import eng_to_telugu
    from .choice import choose

    # Normalize phonetics first
    subject_norm = map_sound(subject)
    root_norm = map_sound(root)

    # Build tense form
    try:
        tense_form = build_tense(root_norm, tense)
    except Exception as e:
        print(f"Error forming tense: {e}")
        return 1

    # Compose sentence candidates (simple variants)
    options = [
        f"{subject_norm} {tense_form}",            # subject first
        f"{tense_form} {subject_norm}",            # verb first
    ]

    # Select final option
    if auto_mode:
        final = options[0]  # Auto-select first option
    else:
        final = choose(options)
        if not final:
            print("No selection made.")
            return 1

    # Transliterate to Telugu script
    try:
        final_telugu = eng_to_telugu(final)
        print("Output:", final_telugu)
    except Exception as e:
        print(f"Error during transliteration: {e}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
