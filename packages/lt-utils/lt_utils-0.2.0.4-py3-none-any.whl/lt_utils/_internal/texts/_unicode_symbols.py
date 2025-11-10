# Unicode ranges grouped by script/language family
def get_unicode_map():
    return {
        # --- Core Latin + IPA ---
        "latin_basic": [("0000", "007F")],  # ASCII
        "latin_1": [("0080", "00FF")],  # Latin-1 Supplement
        "latin_extended": [
            ("0100", "017F"),  # Extended-A
            ("0180", "024F"),  # Extended-B
            ("1E00", "1EFF"),  # Extended Additional
        ],
        "ipa": [
            ("0250", "02AF"),  # IPA Extensions
            ("02B0", "02FF"),  # Spacing Modifier Letters
            ("0300", "036F"),  # Combining Diacritical Marks
            ("1D00", "1D7F"),  # Phonetic Extensions
            ("1D80", "1DBF"),  # Phonetic Extensions Supplement
        ],
        # --- Europe ---
        "greek": [("0370", "03FF")],
        "cyrillic": [("0400", "04FF")],
        # --- Middle East ---
        "hebrew": [("0590", "05FF")],
        "arabic": [
            ("0600", "06FF"),  # Arabic
            ("0750", "077F"),  # Arabic Supplement
            ("08A0", "08FF"),  # Arabic Extended-A
        ],
        # --- South Asia ---
        "devanagari": [("0900", "097F")],
        "bengali": [("0980", "09FF")],
        "gurmukhi": [("0A00", "0A7F")],
        "gujarati": [("0A80", "0AFF")],
        "oriya": [("0B00", "0B7F")],
        "tamil": [("0B80", "0BFF")],
        "telugu": [("0C00", "0C7F")],
        "kannada": [("0C80", "0CFF")],
        "malayalam": [("0D00", "0D7F")],
        "sinhala": [("0D80", "0DFF")],
        "thai": [("0E00", "0E7F")],
        "khmer": [("1780", "17FF")],
        # --- East Asia ---
        "hiragana": [("3040", "309F")],
        "katakana": [
            ("30A0", "30FF"),  # Katakana
            ("31F0", "31FF"),  # Katakana Extensions
        ],
        "cjk": [
            ("4E00", "9FFF"),  # Unified Ideographs
            ("3400", "4DBF"),  # Extension A
        ],
        "hangul": [
            ("AC00", "D7AF"),  # Hangul Syllables
            ("1100", "11FF"),  # Hangul Jamo
        ],
        # --- Southeast Asia / Philippines ---
        "tagalog": [("1700", "171F")],
        "hanunoo": [("1720", "173F")],
        "buhid": [("1740", "175F")],
        "tagbanwa": [("1760", "177F")],
        # --- Punctuation ---
        "punctuation": [
            ("2000", "206F"),  # General Punctuation
            ("2E00", "2E7F"),  # Supplemental Punctuation
        ],
    }
