# SocialPreText

A simple, lightweight Python utility for preprocessing and cleaning social media text.

`socialpretext` cleans raw text by expanding slang, expanding contractions, removing emojis, URLs, hashtags, and more, making it ready for NLP models and analysis.

## Features

* Expand common slang (e.g., `idk` -> `I do not know`)
* Expand English contractions (e.g., `don't` -> `do not`)
* Remove or "demojize" emojis (e.g., `😊` -> `:smiling_face:`)
* Remove URLs
* Remove user mentions (`@mentions`)
* Remove hashtags (`#hashtags`)
* Normalize whitespace

## Installation

```bash
pip install socialpretext
