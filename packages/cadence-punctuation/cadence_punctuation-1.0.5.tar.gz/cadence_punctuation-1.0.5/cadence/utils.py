"""
Utility functions and constants for punctuation processing
"""

import re
import functools
from typing import Dict, Set, List

# Punctuation mapping
punctuation_map = {
    "O": 0, ".": 1, ",": 2, "?": 3, "-": 4, ";": 5, "_": 6, "!": 7, "'": 8,
    "...": 9, "\"": 10, "।": 11, "(": 12, ")": 13, ":": 14,
    "٬": 15, # Arabic comma
    "۔": 16, # Urdu full stop
    "؟": 17, # Urdu question mark
    ".\"": 18, # Full stop followed by quotes
    ").": 19,
    "),": 20,
    "\",": 21,  # Quotes followed by comma
    "\".": 22, # Quotes followed by fullstop
    "?\"": 23, # Question mark followed by quotes
    "\"?": 24, # Quotes followed by question mark
    "।\"": 25, # Hindi Danda followed by quotes
    "\"।": 26, # Quotes followed by Danda
    "،": 27,  # Another arabic comma
    "᱾": 28, # Santali
    "॥": 29, # For sanskrit
    "᱾।": 30, # Santali Paragraph ender
}

id_to_punctuation = {v: k for k, v in punctuation_map.items()}

# Abbreviations and capitalization control
ABBREVIATIONS_COMPLETE = {
    "dr.", "prof.", "mr.", "mrs.", "ms.", "rev.", "hon.", "st.",
    "etc.", "vs.", "viz.", "cf.", "ca.", "approx.",
    "e.g.", "i.e.", "u.s.", "u.k.",
    "no.", "vol.", "pp.", "fig.", "op.", "cit.", "art.", "sec.",
    "lt.", "col.", "sgt.", "capt.", "gen.", "adm.",
    "inc.", "ltd.", "co.", "corp."
}

# Sentence ending punctuation lookup
SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP: Dict[str, str] = {}
BASE_SENTENCE_ENDERS = {".", "?", "!", "...", "।", "۔", "؟"}

for p in BASE_SENTENCE_ENDERS:
    for punct_str, _ in punctuation_map.items():
        if punct_str == p:
            SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP[p] = p
            break

COMBINED_ENDERS_MAP = {
    ".\"": ".", "\".": ".", ").": ".",
    "?\"": "?", "\"?": "?",
    "!\"": "!", "\"!": "!",
    "।\"": "।", "\"।": "।",
    "۔\"": "۔", "\"۔": "۔",
    "؟\"": "؟", "\"؟": "؟",
}

for combined_punct_str, base_ender_char in COMBINED_ENDERS_MAP.items():
    if combined_punct_str in punctuation_map:
        SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP[combined_punct_str] = base_ender_char

for _, pred_str in id_to_punctuation.items():
    if pred_str not in SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP:
        for base_ender in BASE_SENTENCE_ENDERS:
            if base_ender in pred_str:
                SENTENCE_ENDING_PUNCT_LOOKUP_FOR_CAP[pred_str] = base_ender
                break

# Script detection
LATIN_RANGES = [(0x0041, 0x005A), (0x0061, 0x007A), (0x00C0, 0x00FF), (0x0100, 0x017F), (0x0180, 0x024F)]
DEVANAGARI_RANGES = [(0x0900, 0x097F), (0x0980, 0x09FF), (0x0A00, 0x0A7F), (0x0A80, 0x0AFF)]
ARABIC_RANGES = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF)]
OL_CHIKI_RANGES = [(0x1C50, 0x1C7F)]

@functools.lru_cache(maxsize=2048)
def get_char_script(char: str) -> str:
    """Get script type of a character."""
    cp = ord(char)
    for start, end in LATIN_RANGES:
        if start <= cp <= end:
            return "LATIN"
    for start, end in DEVANAGARI_RANGES:
        if start <= cp <= end:
            return "DEVANAGARI"
    for start, end in ARABIC_RANGES:
        if start <= cp <= end:
            return "ARABIC"
    for start, end in OL_CHIKI_RANGES:
        if start <= cp <= end:
            return "OL_CHIKI"
    return "OTHER"

@functools.lru_cache(maxsize=8192)
def get_token_script(token_str: str) -> str:
    """Get script type of a token."""
    if not token_str or token_str.isspace():
        return "OTHER"
    
    scripts_found = {"LATIN": 0, "DEVANAGARI": 0, "ARABIC": 0, "OL_CHIKI": 0, "OTHER": 0}
    cleaned_token_str = ''.join(filter(str.isalpha, token_str.strip()))
    
    if not cleaned_token_str:
        for char_original in token_str.strip():
            if char_original.isalpha():
                scripts_found[get_char_script(char_original)] += 1
    else:
        for char_cleaned in cleaned_token_str:
            scripts_found[get_char_script(char_cleaned)] += 1
    
    if scripts_found["DEVANAGARI"] > 0:
        return "DEVANAGARI"
    if scripts_found["ARABIC"] > 0:
        return "ARABIC"
    if scripts_found["LATIN"] > 0:
        return "LATIN"
    if scripts_found["OL_CHIKI"] > 0:
        return "OL_CHIKI"
    return "OTHER"

# Text processing functions
_RE_SPACE_PLUS = re.compile(r'\s+')
_RE_SPACE_BEFORE_PUNCT_GENERAL = re.compile(r'\s+([,.?!;:।۔؟،٬])(?!\s*")')
_RE_SPACE_BEFORE_PUNCT_END = re.compile(r'\s+([,.?!;:।۔؟،٬])$')
_RE_CONTRACTIONS = {
    suffix: re.compile(rf"\s{re.escape(suffix)}")
    for suffix in ["'s", "'t", "'re", "'ve", "'m", "'ll", "'d"]
}

def _final_spacing_cleanup(text: str) -> str:
    """Final spacing cleanup for text."""
    processed_text = _RE_SPACE_PLUS.sub(' ', text).strip()
    processed_text = _RE_SPACE_BEFORE_PUNCT_GENERAL.sub(r'\1', processed_text)
    processed_text = _RE_SPACE_BEFORE_PUNCT_END.sub(r'\1', processed_text)
    
    for contraction_suffix in ["'s", "'t", "'re", "'ve", "'m", "'ll", "'d"]:
        processed_text = _RE_CONTRACTIONS[contraction_suffix].sub(contraction_suffix, processed_text)
    
    return _RE_SPACE_PLUS.sub(' ', processed_text).strip()

def post_process_cleaned_text(text: str) -> str:
    if not text: return ""
    indices_to_remove: Set[int] = set()
    paren_stack: List[int] = []
    for i_s1, char_s1 in enumerate(text):
        if char_s1 == '(': paren_stack.append(i_s1)
        elif char_s1 == ')':
            if paren_stack: paren_stack.pop()
            else: indices_to_remove.add(i_s1)
    indices_to_remove.update(paren_stack)
    quote_stack: List[int] = []
    for i_s1, char_s1 in enumerate(text):
        if char_s1 == '"':
            if quote_stack: quote_stack.pop()
            else: quote_stack.append(i_s1)
    indices_to_remove.update(quote_stack)
    text_v1_chars: List[str] = [char for i, char in enumerate(text) if i not in indices_to_remove]
    text_v1 = "".join(text_v1_chars)
    if not text_v1: return ""

    output_chars: List[str] = []
    is_inside_quote = False
    # For quotes: ". " or "? " or "। " etc. before an opening quote
    trigger_chars_before_open_quote = {'.', '?', '!', '।', '۔', '؟', '...', ";", ":"} 
    punct_after_closing_quote_no_space = {'.', ',', '?', '!', ';', ':', ')', ']', '}', '۔', '؟', '،', '٬', '।'}
    text_v1_len = len(text_v1)

    for i, current_char in enumerate(text_v1):
        if current_char == '"':
            if not is_inside_quote: # Opening quote
                if output_chars and output_chars[-1] in trigger_chars_before_open_quote:
                    # Ensure there isn't already a space if the trigger char itself implies a space after
                    if output_chars[-1] != ' ': output_chars.append(' ')
                elif output_chars and output_chars[-1].isalnum(): # If previous char is alphanumeric, add space
                     output_chars.append(' ')
                output_chars.append(current_char)
                is_inside_quote = True
            else: # Closing quote
                output_chars.append(current_char)
                is_inside_quote = False
                if (i + 1) < text_v1_len:
                    next_char = text_v1[i+1]
                    # Add space after closing quote if next char is not space/punct (unless it's an opening paren/quote)
                    if not next_char.isspace() and \
                       next_char not in punct_after_closing_quote_no_space and \
                       next_char not in ['(', '[', '{', '"']:
                        output_chars.append(' ')
        else:
            # Handle non-quote characters
            if current_char == '(':
                # If current char is '(', and the last appended char was not a space or another '(', add a space.
                if output_chars and output_chars[-1] != ' ':
                    output_chars.append(' ')
                output_chars.append(current_char)
            elif current_char == ' ' and output_chars and output_chars[-1] == '(':
                # If current char is a space, and the last appended char was '(', skip this space.
                pass
            else:
                # Otherwise, append the character.
                output_chars.append(current_char)
    return "".join(output_chars)

