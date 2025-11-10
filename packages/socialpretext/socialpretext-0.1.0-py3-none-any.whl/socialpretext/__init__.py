# This makes your functions easy to import
# e.g., from socialpretext import clean_all, demojize

from .pipeline import (
    clean_all,
    expand_contractions,
    expand_slang,
    remove_urls,
    remove_mentions,
    remove_hashtags,
    demojize,
    remove_emojis,
    remove_punctuation,
    normalize_whitespace
)

# This is the single source of truth for your package version
__version__ = "0.1.0"
