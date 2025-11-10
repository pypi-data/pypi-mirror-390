import re
import string
import emoji  # This will be our only dependency!

# Use relative imports to get data from within the package
from ._data.contractions import CONTRACTION_MAP
from ._data.slang import SLANG_MAP

# Compile regex patterns for efficiency
# We use re.IGNORECASE for slang since it can be "IDK" or "idk"
contractions_re = re.compile('(%s)' % '|'.join(CONTRACTION_MAP.keys()))
slang_re = re.compile(r'\b(%s)\b' % '|'.join(SLANG_MAP.keys()), re.IGNORECASE)

# Regex patterns for other tokens
url_pattern = re.compile(r'https?://\S+|www\.\S+')
mention_pattern = re.compile(r'@\w+')
hashtag_pattern = re.compile(r'#\w+')
whitespace_pattern = re.compile(r'\s+')

def expand_contractions(text: str) -> str:
    """Expands common English contractions (e.g., "don't" -> "do not")."""
    def replace(match):
        return CONTRACTION_MAP[match.group(0)]
    return contractions_re.sub(replace, text)

def expand_slang(text: str) -> str:
    """Expands common slang (e.g., "idk" -> "I do not know")."""
    def replace(match):
        # Use .lower() to match keys in the SLANG_MAP
        return SLANG_MAP[match.group(0).lower()]
    return slang_re.sub(replace, text)

def remove_urls(text: str) -> str:
    """Removes http/https URLs and www. links."""
    return url_pattern.sub('', text)

def remove_mentions(text: str) -> str:
    """Removes @mentions."""
    return mention_pattern.sub('', text)

def remove_hashtags(text: str) -> str:
    """Removes #hashtags."""
    return hashtag_pattern.sub('', text)

def demojize(text: str) -> str:
    """Converts emojis to their text representation (e.g., 😊 -> :smiling_face:)."""
    return emoji.demojize(text)

def remove_emojis(text: str) -> str:
    """Removes all emoji characters from the text."""
    return emoji.replace_emoji(text, replace='')

def remove_punctuation(text: str) -> str:
    """Removes all standard punctuation."""
    return text.translate(str.maketrans('', '', string.punctuation))

def normalize_whitespace(text: str) -> str:
    """Replaces all whitespace (tabs, newlines, multiple spaces) with a single space."""
    return whitespace_pattern.sub(' ', text).strip()

def clean_all(text: str, pipeline_steps: list = None) -> str:
    """
    Runs text through a complete, default cleaning pipeline.
    
    Default pipeline:
    1. Lowercase
    2. Expand Contractions
    3. Expand Slang
    4. Remove URLs
    5. Remove Mentions
    6. Remove Emojis
    7. Remove Punctuation
    8. Normalize Whitespace
    """
    
    if pipeline_steps is None:
        pipeline_steps = [
            'lowercase', 'expand_contractions', 'expand_slang', 'remove_urls',
            'remove_mentions', 'remove_emojis', 'remove_punctuation', 'normalize_whitespace'
        ]
        
    cleaned_text = text
    
    if 'lowercase' in pipeline_steps:
        cleaned_text = cleaned_text.lower()
    if 'expand_contractions' in pipeline_steps:
        cleaned_text = expand_contractions(cleaned_text)
    if 'expand_slang' in pipeline_steps:
        cleaned_text = expand_slang(cleaned_text)
    if 'remove_urls' in pipeline_steps:
        cleaned_text = remove_urls(cleaned_text)
    if 'remove_mentions' in pipeline_steps:
        cleaned_text = remove_mentions(cleaned_text)
    if 'remove_emojis' in pipeline_steps:
        cleaned_text = remove_emojis(cleaned_text)
    if 'demojize' in pipeline_steps: # Note: 'demojize' and 'remove_emojis' are separate
        cleaned_text = demojize(cleaned_text)
    if 'remove_punctuation' in pipeline_steps:
        cleaned_text = remove_punctuation(cleaned_text)
    if 'normalize_whitespace' in pipeline_steps:
        cleaned_text = normalize_whitespace(cleaned_text)
        
    return cleaned_text
