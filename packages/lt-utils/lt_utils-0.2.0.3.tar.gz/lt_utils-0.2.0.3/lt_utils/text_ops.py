__all__ = [
    "spacy_tokenizer",
    "tokenize_text",
    "similarity_simplified",
    "similarity",
    "has_digit",
    "entropy",
    "scramble_text",
    "compare_texts",
    "stem_text",
    "recursive_replacer",
    "clipboard",
    "html_to_markdown",
    "markdown_to_html",
    "split",
    "lemmatize_text",
    "generate_ngrams",
    "max_rfinder",
    "check_next",
    "trim_incomplete_sentence",
    "simplify_quotes",
    "clear_empty",
    "extract_named_entities",
    "find_repeated_words",
    "normalize_text",
    "remove_non_printable",
    "split_by_paragraph",
    "extract_hashtags",
    "extract_mentions",
    "count_sentences",
    "extract_keywords",
    "formatter",
    "count_words",
    "extract_keys",
    "has_any",
    "unescape",
    "escape",
    "extract_fs_keywords",
    "requoter",
    "fragment_text",
    "get_unicode_hex",
    "get_encoding_aliases",
    "get_unicode_chars",
    "get_unicode_map",
    "get_mapped_unicode_chars",
    "format_num_to_str",
    "spacer",
    "clean_text",
    "replace_numbers",
    "remove_symbols",
    "SplitTextV2",
    "SplitText",
]

import gc
import re

from collections import Counter

from lt_utils.common import *
from lt_utils.type_checks import is_str, is_array
from lt_utils._internal.texts.requoter import requoter
from lt_utils._internal.texts.nlp_stuff import nlp_instance
from lt_utils._internal.texts._unicode_symbols import get_unicode_map
from lt_utils._internal.texts.clean_up import replace_numbers, remove_symbols


def spacy_tokenizer(
    text: str,
    allowed_pos: set[str] = {"NOUN", "ADJ"},
    spacy_model: Literal["en_core_web_md", "en_core_web_lg"] = None,
) -> List[str]:
    """Tokenize and lemmatize text, filtering by POS tags."""
    nlp_instance.initialize_spacy(spacy_model)
    doc = nlp_instance.spc(text)
    return [
        token.lemma_.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.pos_ in allowed_pos
    ]


def tokenize_text(
    text: str,
    by: Literal["word", "sentence"] = "word",
    language: str = "english",
    preserve_line: bool = False,
) -> List[str]:
    """Tokenize text by words or sentences.

    Args:
        text (str): The input text to tokenize.
        by (Literal["word", "sentence"], optional): The level of tokenization ("word" or "sentence"). Defaults to "word".

    Returns:
        List[str]: A list of tokens based on the specified level.
    """
    assert by in ["word", "sentence"], "Invalid tokenization type"
    import nltk

    nlp_instance.initialize_nltk()
    if by == "word":
        return [
            recursive_replacer(
                x,
                {
                    "``": '"',
                    "`": '"',
                },
            )
            for x in nltk.word_tokenize(
                text,
                language=language,
                preserve_line=preserve_line,
            )
        ]
    return nltk.sent_tokenize(text, language=language)


def similarity_simplified(text1: str, text2: str) -> float:
    """Compute similarity between two texts using cosine similarity.

    Args:
        text1 (str): The first text for comparison.
        text2 (str): The second text for comparison.

    Returns:
        float: The cosine similarity score between the two texts.
    """
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    vectorizer = CountVectorizer().fit_transform([text1, text2])
    vectors = vectorizer.toarray()
    return cosine_similarity([vectors[0]], [vectors[1]])[0][0]


def similarity(
    text1: str,
    text2: str,
    spacy_model: Literal["en_core_web_md", "en_core_web_lg"] = None,
) -> float:
    """Compute similarity between two texts using TF-IDF cosine or spaCy vectors.

    Args:
        text1 (str): First input text.
        text2 (str): Second input text.

    Returns:
        float: Similarity score.
    """
    nlp_instance.initialize_spacy(spacy_model)
    doc1, doc2 = nlp_instance.spc(text1), nlp_instance.spc(text2)
    return doc1.similarity(doc2)


def has_digit(text: str):
    for char in text.strip():
        if char.isdigit():
            return True
    return False


def entropy(
    text: str,
    level: Literal["char", "word"] = "char",
    normalize: bool = False,
    language: str = "english",
) -> float:
    """Calculate entropy of a text using either character or word-level tokenization.

    Args:
        text (str): Input string.
        level (str): Tokenization level ("char" or "word").
        normalize (bool): If True, normalize entropy to [0, 1] range.
        language (str): Language for word tokenization.

    Returns:
        float: Entropy value.
    """
    import numpy as np

    if level == "word":
        tokens = tokenize_text(text.lower(), by="word", language=language)
    else:
        tokens = list(text.lower())

    if not tokens:
        return 0.0

    counter = Counter(tokens)
    total = len(tokens)
    probs = np.array([count / total for count in counter.values()])

    ent = -np.sum(probs * np.log2(probs))

    if normalize:
        import math

        max_entropy = math.log2(len(counter)) if len(counter) > 0 else 1
        ent /= max_entropy

    return float(ent)


def scramble_text(text: str, seed: Optional[int] = None) -> str:
    """Randomly shuffle the words in a text.

    Args:
        text (str): The input text to be scrambled.
        seed (int, optional): Seed for reproducing the results

    Returns:
        str: The text with its words randomly shuffled.
    """
    import random

    words = text.split()
    if seed is not None:
        random.seed(seed)
    random.shuffle(words)
    return " ".join(words)


def compare_texts(text1: str, text2: str) -> List[str]:
    """Compare two texts and highlight the differences.

    Args:
        text1 (str): The first text to compare.
        text2 (str): The second text to compare.

    Returns:
        List[str]: A list of lines that differ between the two texts, prefixed with '- ' for deletions and '+ ' for additions.
    """
    import difflib

    differ = difflib.Differ()
    result = list(differ.compare(text1.splitlines(), text2.splitlines()))
    return [line for line in result if line.startswith("- ") or line.startswith("+ ")]


def stem_text(
    text: str,
    language: str = "english",
) -> str:
    """Reduce words in the text to their stem or root form.

    Args:
        text (str): The input text to be stemmed.

    Returns:
        str: The text with words reduced to their stems.
    """
    import nltk

    tokens = tokenize_text(
        text,
        by="word",
        language=language,
        preserve_line=False,
    )
    stemmer = nltk.PorterStemmer()

    return " ".join([stemmer.stem(token) for token in tokens])


def recursive_replacer(entry: str, dic: dict[str, str]) -> str:
    """
    Recursively replaces all keys of the dictionary with their corresponding values within a given string.

    Args:
        text (str): The original text.
        replacements (Dict[str, str]): A dictionary where keys are what to replace and values is what they will be replaced by

    Returns:
        str: The final modified text
    """
    for i, j in dic.items():
        entry = entry.replace(i, j)
    return entry


def clipboard(
    task: Literal["copy", "paste"], text: Optional[str] = None
) -> Optional[str]:
    """
    If  the task is set to:
    Copy: Set the clipboard to the given text.
    Paste: Returns the contents from the clipboard.
    """
    import pyperclip

    if task == "copy":
        pyperclip.copy(text or "")
    else:
        return pyperclip.paste()


def html_to_markdown(
    html: Union[str, bytes],
    escape_asterisks: bool = True,
    escape_underscores: bool = True,
    escape_misc: bool = True,
    heading_style: bool = "underlined",
    strong_em_symbol: bool = "*",
    sub_symbol: bool = "",
    sup_symbol: bool = "",
    wrap: bool = False,
    wrap_width: bool = 80,
) -> str:
    """
    Converts HTML content to Markdown format.

    Args:
        html (str): The HTML string that needs to be converted.
                    Example - "<h1>Hello, World!</h1>"

    Returns:
        str: The corresponding markdown version of the inputted HTML
             Example - "# Hello, World!"
    """
    import markdownify

    return markdownify.markdownify(
        html=html,
        escape_asterisks=escape_asterisks,
        escape_underscores=escape_underscores,
        escape_misc=escape_misc,
        heading_style=heading_style,
        strong_em_symbol=strong_em_symbol,
        sub_symbol=sub_symbol,
        sup_symbol=sup_symbol,
        wrap=wrap,
        wrap_width=wrap_width,
    )


def markdown_to_html(markdown: Union[str, bytes]) -> str:
    """
    Converts Markdown text to HTML.

    Args:
        markdown (Union[str, bytes]): The input Markdown text. Can be either a string or bytes object.

    Returns:
        str: The converted HTML.
    """
    import markdown2

    return markdown2.markdown(markdown)


def _blob_split(text: str, *, __recall: bool = False) -> List[str]:
    """
    Splits the input text into sentences using TextBlob.

    Args:
        text (str): The input text to split.

    Returns:
        list[str]: A list of the detected sentences in the provided text.
    """
    from textblob import TextBlob
    from textblob.exceptions import MissingCorpusError

    try:
        return [x for x in TextBlob(text).raw_sentences]
    except MissingCorpusError as e:
        if not __recall:
            import subprocess

            _ = subprocess.run(
                "python -m textblob.download_corpora",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )
            gc.collect()
            return _blob_split(text, __recall=True)
        raise e


def split(
    entry: str,
    *,
    desired_length: int = 100,
    max_length: int = 300,
    simplify_quote: bool = False,
    mode: Literal["base", "blob", "v1", "v2"] = "v2",
    honorifics: List[str] = [
        "mr.",
        "mrs.",
        "miss.",
        "ms.",
        "sr.",
        "dr.",
        "cap.",
        "cpt.",
    ],
    **kwargs,
):
    """Split the text into a list of sentences.

    On "base" mode, this function tries to make each of those splits at an approximated length
    to the desired_length, and below the max limit.

    Args:
        entry (str): The text to be splitten
        desired_length (int, optional): Size that the split will try to be done (available only at "base" mode). Defaults to 100.
        max_length (int, optional): Limits the size of the text. Its only enforced on splitter 'v1', but is more a loose guardrail for both blob and v2.
        simplify_quote (bool, optional): If True, will replace "fancy" quotes to simpler ones. It will be applied regardless when using v2. (available only at "base" mode). Defaults to False.
        honorifics (Sequence[str], optional): Used only by v2, it will prevent slicing honorifics that uses dots as a end of sentence. Example: 'mr. John' would be sliced by 'mr.' and 'John' as a new sentence by the older version.
        mode (Literal["v1", 'v2, "blob"], optional): Splitting mode. Defaults to "v2".

    Returns:
        _type_: _description_
    """
    mode = mode.lower()
    assert mode in [
        "base",
        "v1",
        "v2",
        "blob",
    ], f'Invalid mode "{mode}". It must be either "v1", "v2", "blob" and "base" (legacy)'
    if simplify_quote:
        entry = simplify_quotes(entry)
    if mode in ["v1", "base"]:
        return SplitText()(
            entry,
            desired_length=desired_length,
            max_length=max_length,
        )
    elif mode == "v2":
        return SplitTextV2(honorifics=honorifics)(
            text=entry,
            desired_length=desired_length,
            safe_ceil=max_length,
        )
    split_sents = _blob_split(entry)
    results = []
    _last_size: int = -1
    for s in split_sents:
        if all(
            [
                _last_size > -1,
                _last_size < desired_length,
                _last_size + len(s) <= max_length,
            ]
        ):
            results[-1] += s
        else:
            results.append(s)
        _last_size = len(results[-1])
    return results


def lemmatize_text(text: str) -> str:
    """Reduce words in the text to their base or dictionary form.

    Args:
        text (str): The input text to be lemmatized.

    Returns:
        str: The text with words reduced to their base forms.
    """
    from textblob import TextBlob

    return " ".join([word.lemmatize() for word in TextBlob(text=text).words])


def generate_ngrams(
    inputs: str | Sequence[Any],
    n: int = 5,
    text_language: str = "english",
    split_text_by: Literal["word", "sentence"] = "word",
    split_ngram_text_by: Literal["char", "full"] = "char",
) -> List[Any]:
    """Generate n-grams (sequences of n items) from the text.

    Args:
        inputs (str | Sequence[Any]): The input text or a list of components from which to
                generate n-grams.
        n (int): The number of items in each n-gram.
        text_language (str, optional): Used only when the input is a string.
                It will be used to split the words/sentences properly.
        split_text_by (Literal["word", "sentence"], optional): Used only when the input is a string.
                If set to words the split will be word by word, otherwise will be the sentence.
        split_ngram_text_by (Literal["char", "full"], optional):  Used only when the input is a string.
                If set to 'char' it will split char by char, otherwise will do the n-grams for the entire
                words or sentences.
    Returns:
        List[Any]: A list of n-grams generated from the inputs.
    """
    import nltk

    if is_array(inputs, True):
        return [x for x in nltk.ngrams(inputs, n)]
    is_str(inputs, False, False, True)
    assert split_ngram_text_by in [
        "char",
        "full",
    ], f'Invalid option for "split_ngram_text_by": {split_ngram_text_by}, it must be either "char" or "full"'
    tokens = tokenize_text(
        inputs,
        by=split_text_by,
        language=text_language,
        preserve_line=False,
    )

    if split_ngram_text_by == "char":
        return [[x for x in nltk.ngrams(word, n)] for word in tokens]
    return [x for x in nltk.ngrams(tokens, n)]


def max_rfinder(entry: str, items_to_find: Union[List[str], Tuple[str, ...]]):
    """
    Finds the last occurrence of any item in a list or tuple within a string.

    Args:
        entry (str): The input string.
        items_to_find (Union[list[str], tuple[str]]): A list or tuple containing strings to find in 'txt'.

    Returns:
        int: The index of the last found item, -1 if no item is found.
    """
    highest_results = -1
    for item in items_to_find:
        current = entry.rfind(item)
        if current > highest_results:
            highest_results = current
    return highest_results


def check_next(
    entry: str,
    current_id: int,
    text_to_match: str | list[str] | None = None,
    is_out_of_index_valid: bool = False,
):
    """
    Checks if the next character in a string matches one or more possibilities.

    Args:
        entry (str): The input string.
        current_id (int): The index of the current character within the string.
        text_to_match (Union[str, list[str], None]): A single character to match or a list/tuple of characters.
                        If not provided and is_out_of_index_valid will be used as a result. Defaults to None.
        is_out_of_index_valid (bool): Whether returning True when the index is out of bounds should be valid. Defaults to False.

    Returns:
        bool: True, if any condition is met; False otherwise.
    """
    try:
        if is_array(text_to_match):
            return entry[current_id + 1] in text_to_match
        return entry[current_id + 1] == text_to_match
    except IndexError:
        return is_out_of_index_valid


def trim_incomplete_sentence(entry: str) -> str:
    """
    Tries to trim an incomplete sentence to the nearest complete one. If it fails returns the original sentence back.

    Args:
        entry (str): The original string containing sentences.
            If not complete, it will be trimmed to end with a valid punctuation mark.

    Returns:
        str: The finalized string.

    Example:

        >>> trimincompletesentence("Hello World! How are you doing?")
        "Hello World!"

        >>> trimincompletesentence("I like programming.")
        "I like programming." # Returns the sentence as it was.
        >>> trimincompletesentence("Hello there. This sentence is incomplete")
        "Hello there." # Returns the latest complete sequence.
        >>> trimincompletesentence("Hello there This sentence is incomplete")
        "Hello there This sentence is incomplete" # Returns the entire sentence if no cutting point was found.
    """
    possible_ends = (".", "?", "!", '."', '?"', '!"')
    entry = str(entry).rstrip()
    lastpunc = max_rfinder(entry, possible_ends)
    ln = len(entry)
    lastpunc = max(entry.rfind("."), entry.rfind("!"), entry.rfind("?"))
    if lastpunc < ln - 1:
        if entry[lastpunc + 1] == '"':
            lastpunc = lastpunc + 1
    if lastpunc >= 0:
        entry = entry[: lastpunc + 1]
    return entry


def simplify_quotes(entry: str) -> str:
    """
    Replaces special characters with standard single or double quotes.

    Args:
        entry (str): The input string containing special quote characters.

    Returns:
        str: The simplified string without the special quote characters.
    """
    is_str(entry, False, False, True)
    return requoter(entry, True)


def clear_empty(text: str, clear_empty_lines: bool = True) -> str:
    """
    Clear empty lines (optional) and empty spaces on a given text.
    """
    return "\n".join(
        [
            re.sub(r"\s+", " ", x.strip())
            for x in text.splitlines()
            if not clear_empty_lines or x.strip()
        ]
    )


def extract_named_entities(
    text: str,
    language: str = "english",
) -> List[str]:
    """Extract named entities from the text.

    Args:
        text (str): The input text from which to extract named entities.

    Returns:
        List[str]: A list of named entities found in the text.
    """
    import nltk

    nlp_instance.initialize_nltk()
    tokens = tokenize_text(
        text,
        by="word",
        language=language,
        preserve_line=False,
    )
    tagged = nltk.pos_tag(tokens)
    chunked = nltk.ne_chunk(tagged)
    return list(
        set([chunk.label() for chunk in chunked if isinstance(chunk, nltk.Tree)])
    )


def find_repeated_words(text: str, language: str = "english") -> Dict[str, int]:
    """Find and count repeated words in a text.

    Args:
        text (str): The input text to search for repeated words.

    Returns:
        Dict[str, int]: A dictionary where keys are repeated words and values are their counts.
    """

    words = [
        tokenize_text(
            text.lower(),
            by="word",
            language=language,
            preserve_line=False,
        )
    ]
    return dict(Counter(word for word in words if words.count(word) > 1))


def normalize_text(entry: str, lines_sep: str = "\n\n") -> str:
    """Convert text to lowercase and remove extra whitespace.
    Lines are preserved

    Args:
        text (str): The input text to normalize.
        lines_sep (str, optional): what will be used to divide the lines,
        "\\n\\n" will keep a paragraph style, while " " will make everything
        in a single line or "\n" a single line break per non-empty line.
    Returns:
        str: The normalized text.
    """
    entry = simplify_quotes(entry)
    return f"{lines_sep}".join(
        [re.sub(r"\s+", " ", x) for x in entry.splitlines() if x.strip()]
    )


def remove_non_printable(entry: str) -> str:
    """Remove non-printable characters from a text.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The text with non-printable characters removed.
    """
    from string import printable

    return "".join([x for x in entry if x in printable])


def split_by_paragraph(text: str) -> List[str]:
    """Split text into paragraphs.

    Args:
        text (str): The input text to split.

    Returns:
        List[str]: A list of paragraphs from the text.
    """
    text = re.sub(r"\n\n+", "\n\n", text)
    return [x.rstrip() for x in text.splitlines() if x.strip()]


def extract_hashtags(entry: str) -> list[str]:
    """Extract hashtags from a text.

    Args:
        text (str): The input text from which to extract hashtags.

    Returns:
        list[str]: A list of hashtags found in the text.
    """
    return re.findall(r"#\w+", entry)


def extract_mentions(entry: str) -> list[str]:
    """Extract mentions (e.g., @user) from a text.

    Args:
        text (str): The input text from which to extract mentions.

    Returns:
        list[str]: A list of mentions found in the text.
    """
    return re.findall(r"@\w+", entry)


def count_sentences(entry: str) -> int:
    """Count the number of sentences in a text.

    Args:
        text (str): The input text to analyze.

    Returns:
        int: The number of sentences in the text.
    """
    split_text = _blob_split(entry)
    return len(split_text)


def extract_keywords(
    entries: Union[str, List[str]],
    top_n: int = 5,
    return_scores: bool = False,
    allowed_pos: set[str] = {"NOUN", "ADJ"},
    ngram_range: Tuple[int, int] = (1, 2),
) -> Union[List[str], List[Tuple[str, float]]]:
    """
    Extract top-N keywords with highest TF-IDF scores after POS filtering and lemmatization.

    Args:
        entries (str | List[str]): One or more input documents.
        top_n (int): Number of keywords to return.
        return_scores (bool): Whether to return (keyword, score) pairs.
        allowed_pos (set[str]): POS tags to allow (e.g., {"NOUN", "ADJ"}).
        ngram_range (tuple): ngram range for vectorizer.

    Returns:
        List[str] or List[Tuple[str, float]]: Keywords or (keyword, score) pairs.
    """
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer

    if isinstance(entries, str):
        entries = [entries]

    # Preprocess texts using spaCy
    processed = [" ".join(spacy_tokenizer(doc, allowed_pos)) for doc in entries]

    try:
        vectorizer = TfidfVectorizer(ngram_range=ngram_range)
        tfidf_matrix = vectorizer.fit_transform(processed)
    except ValueError:
        return []

    # Compute average TF-IDF score across all docs
    tfidf_means = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
    top_indices = tfidf_means.argsort()[::-1][:top_n]
    features = vectorizer.get_feature_names_out()

    if return_scores:
        return [(features[i], float(tfidf_means[i])) for i in top_indices]
    return [features[i] for i in top_indices]


def formatter(entry: str, width: int) -> str:
    """Format text to fit a certain width.

    Args:
        text (str): The input text to format.
        width (int): The maximum width of each line in the formatted text.

    Returns:
        str: The formatted text.
    """
    import textwrap

    return textwrap.fill(entry, width)


def count_words(entry: str, language: str = "english") -> int:
    """Count the number of words in a text.

    Args:
        text (str): The input text to analyze.

    Returns:
        int: The total word count in the text.
    """
    tokenized_text = tokenize_text(
        entry, by="word", language=language, preserve_line=False
    )
    return len(tokenized_text)


def extract_keys(entry: str) -> list | list[str]:
    # Use a regular expression to find all occurrences of {key} in the string
    keys = re.findall(r"\{(\w+)\}", entry)
    return keys


def has_any(
    entry: str,
    any_of: Union[str, List[str]],
    force_lower_case: bool = False,
):
    """Basically the reverse of **in** function, it can be used to locate if **sources** contains anything from the **any_of** into it.

    Args:
        sources (str):
            Target string to be checked if has any of the provided keys.
        any_of (str | list[str]):
            The string or list of strings to be checked if they are or not in the text.
            If its a string each letter will be checked, if its a list of string, then each word in the list will be checked instead.
        force_lower_case (bool, optional):
            If true will set everything to lower-case (both source and any_of).
            This is useful for tasks that dont require a case-sensitive scan. Defaults to False.

    Returns:
        bool: If any key was found will be returned as true, otherwise False.
    """
    if not entry or not isinstance(any_of, (str, tuple, list)) or not any_of:
        return False

    if isinstance(any_of, (list, tuple)):
        any_of = [
            x.lower() if force_lower_case else x for x in any_of if isinstance(x, str)
        ]
        if not any_of:
            return False
    else:
        any_of = [any_of.lower() if force_lower_case else any_of]

    for elem in any_of:
        if elem in entry:
            return True
    return False


def unescape(
    entry: Union[str, bytes], errors: Literal["strict", "ignore"] = "strict"
) -> str:
    """
    Unescapes the given string.

    Args:
        entry (str, bytes): The input string.

    Raises:
        Assertion: If entry is not a valid string or bytes.

    Returns:
        (str, bytes): The unescaped entry same type as the input.

    Example:

        ```python

        results = unescape("This is the first line.\\\\n\\\\nThis is the last line!")
        # results = "This is the first line.\\n\\nThis is the last line!"

        ```
    """
    assert isinstance(
        entry, (str, bytes)
    ), "The input should be a valid string or bytes."
    if isinstance(entry, bytes):
        return entry.decode(encoding="unicode-escape", errors=errors).encode(
            errors=errors
        )
    return entry.encode(errors=errors).decode("unicode-escape", errors=errors)


def escape(
    entry: Union[str, bytes],
    errors: Literal["strict", "ignore"] = "strict",
    encoding: Union[
        str, Literal["utf-8", "ascii", "unicode-escape", "latin-1"]
    ] = "utf-8",
) -> Union[str, bytes]:
    """
    Escapes the given string.

    Args:
        entry (str, bytes): The input string.

    Raises:
        Assertion: If entry is not a valid string or bytes.

    Returns:
        (str, bytes): The escaped entry same type as the input.

    Example:

        ```python

        results = escape("This is the first line.\\n\\nThis is the last line!")
        # results = "This is the first line.\\\\n\\\\nThis is the last line!"

        ```
    """
    assert isinstance(
        entry, (str, bytes)
    ), "The input should be a valid string or bytes."
    if isinstance(entry, str):
        return entry.encode(encoding="unicode-escape", errors=errors).decode(
            errors=errors, encoding=encoding
        )
    return entry.decode(errors=errors, encoding=encoding).encode(
        encoding="unicode-escape", errors=errors
    )


def extract_fs_keywords(f_string: str):
    # Regular expression to match placeholders in f-strings
    pattern = r"{(.*?)}"
    return re.findall(pattern, f_string)


def fragment_text(
    text: Union[str, List[str]],
    prob: float = 0.3,
    sizes: List[int] = [2, 3, 4, 5],
    seed: Optional[int] = None,
):
    """Break a word into small fragments with some probability."""
    import random

    if isinstance(text, str):
        results = [text]
    if len(text) <= min(sizes):
        return results
    # simple split: half
    mid = len(text) // 2
    results.append(text[:mid])
    results.append(text[mid:])

    # n-grams
    if seed is not None:
        random.seed(seed)
    for n in sizes:
        if n >= mid:
            break
        if len(text) >= n:
            for i in range(len(text) - n + 1):
                if random.random() < prob:
                    results.append(text[i : i + n])
    return list(set(results))


def get_encoding_aliases(entry: Optional[str] = None):
    from encodings.aliases import aliases

    if entry is None:
        return [(k, v) for k, v in aliases.items()]
    return [(k, v) for k, v in aliases.items() if entry in k or entry in v]


def get_unicode_hex(char: str, prefix: bool = True) -> str:
    """
    Return the Unicode code point of a given character in hexadecimal.

    Args:
        char (str): A single character.
        prefix (bool): Whether to include the '0x' prefix in the result. Defaults to True.

    Returns:
        str: The hexadecimal representation of the character's Unicode code point.

    Example:
        >>> get_unicode_hex("฀")
        '0x0e00'
        >>> get_unicode_hex("฀", prefix=False)
        '0e00'
    """
    if len(char) != 1:
        raise ValueError("Input must be a single character.")
    return hex(ord(char)) if prefix else format(ord(char), "04x")


def get_unicode_chars(start_hex: str, end_hex: str, base: int = 16):
    """
    # Example:
    ```
        my_character_set = get_unicode_chars('0E00', '0E7F', 16)
        print("".join(my_character_set))
    ```
    """
    return [chr(code) for code in range(int(start_hex, base), int(end_hex, base) + 1)]


def get_mapped_unicode_chars(
    selected_keys: Union[List[str], str],
    unicode_map: Optional[Dict[str, List[Tuple[str, str]]]] = None,
):
    import unicodedata

    if isinstance(selected_keys, str):
        selected_keys = [selected_keys]
    if not unicode_map:
        unicode_map = get_unicode_map()
    chars = []
    for key in selected_keys:
        for start, end in unicode_map.get(key, {}):
            for code in range(int(start, 16), int(end, 16) + 1):
                ch = chr(code)
                cat = unicodedata.category(ch)
                if cat.startswith("C"):  # skip controls/unassigned
                    continue
                chars.append(ch)
    return chars


def format_num_to_str(
    item: Union[int, float],
    round_decimals: Optional[int] = None,
):
    assert isinstance(
        item, (int, float)
    ), f"item must be a valid number but received '{item}'"
    if isinstance(item, int) or int(item) == item:
        return format(item, ",").replace(",", ".")

    if round_decimals:
        item = round(item, round_decimals)
    return format(item, ",").replace(".", "_").replace(",", ".").replace("_", ",")


def spacer(
    text: str,
    direction: Literal["right", "left", "center"] = "right",
    width: int = 2,
    fill_char=" ",
):
    assert direction in [
        "left",
        "right",
        "center",
    ], (
        f'Invalid direction "{direction}", use one of following directions: "'
        + '", "'.join(["left", "right", "center"])
        + '".'
    )
    results = []
    match direction:
        case "left":
            fn = lambda x: str(x).ljust(len(x) + width, fill_char)
        case "right":
            fn = lambda x: str(x).rjust(len(x) + width, fill_char)
        case "center":
            fn = lambda x: str(x).center(len(x) + width, fill_char)

    for txt in text.splitlines():
        if not txt.strip():
            results.append(txt)
            continue
        results.append(fn(txt))
    return "\n".join(results)


def clean_text(
    text: str,
    *,
    dots_to_ellipsis: bool = False,
    brackets_removal: bool = True,
    brackets_content_removal: bool = False,
    replace_bullet: bool = False,
    unescape_html: bool = False,
    replace_bullet_mode: Literal["a", "b"] = "a",
    dash_for_space: bool = True,
    preserve_empty_lines: bool = False,
    use_symbol_replacements: bool = True,
    symbol_replacements: Optional[Dict[str, str]] = None,
    **kwargs,
):
    from lt_utils._internal.texts.clean_up import (
        BRACKET_PATTERNS,
        SYMBOL_REPLACEMENTS,
        BULLET_REPLACEMENTS_A,
        BULLET_REPLACEMENTS_B,
    )

    if unescape_html:
        # HTML entity decode (&amp; → &, etc.)
        import html

        text = html.unescape(text)

    # Remove bracketed content
    if brackets_removal:
        if brackets_content_removal:
            for pattern in BRACKET_PATTERNS:
                text = re.sub(pattern, " ", text)

        for ch in ["(", ")", "[", "]", "{", "}", "⟨", "⟩"]:
            text = text.replace(ch, " ")

    if use_symbol_replacements:
        if not symbol_replacements:
            symbol_replacements = SYMBOL_REPLACEMENTS.copy()
        for sym, rep in symbol_replacements.items():
            text = text.replace(sym, rep)

    # Bullet replacements
    if replace_bullet:
        re_mode = (
            BULLET_REPLACEMENTS_A.copy()
            if replace_bullet_mode == "a"
            else BULLET_REPLACEMENTS_B.copy()
        )
        for sym, rep in re_mode.items():
            text = text.replace(sym, rep)

        text = re.sub(r"[\-]+", "-", text)

    if dash_for_space:
        text = re.sub(r"[\_]+", " ", text)

    # Ellipsis normalization
    if dots_to_ellipsis:
        text = re.sub(r"\.\s*\.\s*\.", "…", text)
        text = re.sub(r"\.{3,}", "…", text)

    # Number passes: decimals first
    text = replace_numbers(text)

    # Remove decorative symbols
    text = remove_symbols(text)

    # Collapse whitespace
    eval_fn = lambda x: (preserve_empty_lines or bool(x.strip()))
    return "\n".join([clear_empty(x) for x in text.splitlines() if eval_fn(x)])


class SplitText:
    def __init__(self):
        self.rv = []
        self.split_pos = []
        self.pos = -1
        self.current = ""
        self.in_quote = False

    def seek(self, delta):
        is_neg = delta < 0
        for _ in range(abs(delta)):
            if is_neg:
                self.pos -= 1
                self.current = self.current[:-1]
            else:
                self.pos += 1
                self.current += self.text[self.pos]
            if self.text[self.pos] in '"“”':
                self.in_quote = not self.in_quote
        return self.text[self.pos]

    def peek(self, delta):
        p = self.pos + delta
        return self.text[p] if p < self.end_pos and p >= 0 else ""

    def commit(self):
        self.rv.append(self.current)
        self.current = ""
        self.split_pos = []

    def __call__(
        self,
        text: str,
        desired_length: int = 100,
        max_length: int = 200,
    ) -> list[str]:
        self.text = text
        self.end_pos = len(self.text) - 1
        self.max_length = max_length
        self.desired_length = desired_length
        while self.pos < self.end_pos:
            c = self.seek(1)
            if len(self.current) >= self.max_length:
                if len(self.split_pos) > 0 and len(self.current) > (
                    self.desired_length / 2
                ):
                    d = self.pos - self.split_pos[-1]
                    self.seek(-d)
                else:
                    while (
                        c not in "!?.\n "
                        and self.pos > 0
                        and len(self.current) > self.desired_length
                    ):
                        c = self.seek(-1)
                self.commit()
            elif not self.in_quote and (
                c in "!?\n" or (c == "." and self.peek(1) in "\n ")
            ):
                while (
                    self.pos < len(self.text) - 1
                    and len(self.current) < self.max_length
                    and self.peek(1) in "!?."
                ):
                    c = self.seek(1)
                self.split_pos.append(self.pos)
                if len(self.current) >= self.desired_length:
                    self.commit()
            elif self.in_quote and self.peek(1) == '"“”' and self.peek(2) in "\n ":
                self.seek(2)
                self.split_pos.append(self.pos)
        self.rv.append(self.current)
        self.rv = [s.strip() for s in self.rv]
        self.rv = [
            s for s in self.rv if len(s) > 0 and not re.match(r"^[\s\.,;:!?]*$", s)
        ]

        return self.rv


class SplitTextV2:
    def __init__(
        self,
        honorifics: List[str] = [
            "mr.",
            "mrs.",
            "miss.",
            "ms.",
            "sr.",
            "dr.",
            "cap.",
            "cpt.",
        ],
    ):
        self.honorifics = tuple(honorifics)
        self.reset()

    def reset(
        self,
        text: str = "",
        desired_length: int = 100,
    ):
        from lt_utils.text_ops import simplify_quotes

        self.pos = -1
        self.in_quote = False
        self.text = simplify_quotes(text)

        self.end_pos = len(self.text) - 1
        self.desired_length = desired_length

    def seek(self):
        checked = ""
        while self.pos < self.end_pos:
            self.pos += 1
            current = self.text[self.pos]
            checked += current
            if current == '"':
                self.in_quote = not self.in_quote
            elif not self.in_quote:
                if current in ["?", "!", "."]:
                    next_val = self.peek(1)
                    if not next_val and self.pos >= self.end_pos:
                        return checked
                    passible = next_val in [" ", "\n", "\t", "\f"]
                    if not passible:
                        continue

                    if current in ["!", "?"]:
                        return checked
                    else:
                        if self.honorifics and checked.lower().endswith(
                            self.honorifics
                        ):
                            print("Honofic found? ", checked[-5:])
                            continue
                        return checked

        return checked

    def peek(self, dist: int):
        p = self.pos + dist

        if p < 0 or p > self.end_pos:
            return ""
        return self.text[p]

    def __call__(
        self,
        text: str,
        desired_length: int = 100,
        safe_ceil: Optional[int] = None,
    ) -> List[str]:

        self.reset(text, desired_length)

        results: List[str] = []
        last_size: int = 0
        if safe_ceil is None:
            safe_ceil = desired_length * 2
        else:
            safe_ceil = max(int(safe_ceil), desired_length + 1)
        while self.pos < self.end_pos:
            h = self.seek()
            if not h.strip():
                continue
            if (
                last_size > 0
                and last_size < desired_length
                and (last_size + len(h)) <= safe_ceil
            ):
                results[-1] += h
            else:
                results.append(h)
            last_size = len(results[-1])
        return [x.strip() for x in results]
