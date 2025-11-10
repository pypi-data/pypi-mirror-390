__all__ = ["remove_symbols", "replace_numbers"]
import re


from lt_utils.common import *


# Remove content in brackets
BRACKET_PATTERNS = [
    r"\([^)]*\)",  # (...)
    r"\[[^\]]*\]",  # [...]
    r"\{[^}]*\}",  # {...}
    r"⟨[^⟩]*⟩",  # ⟨...⟩
]

SYMBOL_REPLACEMENTS = {
    "$": " dollar ",
    "%": " percent ",
    "&": " and ",
    "#": " number ",
    "@": " at ",
    "§": " section ",
    "|": " or ",
    "~": " tilde ",
    "^": " caret ",
    "/": " slash ",
    "\\": " slash ",
    "<": " less than ",
    ">": " greater than ",
}

BULLET_REPLACEMENTS_A = {
    "•": "-",
    "·": "-",
    "‧": "-",
    "∙": "-",
    "−": "-",
}
BULLET_REPLACEMENTS_B = {
    "•": "—",
    "·": "—",
    "‧": "—",
    "∙": "—",
    "−": "-",
}


def remove_symbols(text: str) -> str:
    import unicodedata

    return "".join(
        c
        for c in text
        if not (
            unicodedata.category(c).startswith("So")
            or "EMOJI" in unicodedata.name(c, "").upper()
        )
    )


def replace_numbers(text: str) -> str:
    from num2words import num2words

    text = re.sub(
        r"\b\d+\.\d+\b",
        lambda x: num2words(float(x.group()), lang="en").replace("-", " "),
        text,
    )
    return re.sub(
        r"\b\d+\b",
        lambda x: num2words(int(x.group()), lang="en").replace("-", " "),
        text,
    )
