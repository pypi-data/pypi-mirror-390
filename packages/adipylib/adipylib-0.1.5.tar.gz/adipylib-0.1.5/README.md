# adipylib

[![PyPI version](https://badge.fury.io/py/adipylib.svg)](https://badge.fury.io/py/adipylib)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple Python Study Toolkit for students, featuring NLP tools for text summarization and keyword extraction.

## Features

* **Extractive Text Summarization:** Quickly shorten long articles or study notes into a few key sentences.
* **Keyword Extraction:** Pulls out the most important keywords from any block of text using TF-IDF.
* **Lightweight & simple:** Easy to install and use with no complex setup.

## Installation

You can install `adipylib` directly from PyPI:

```bash
pip install adipylib
```

## Usage

```python
import adipylib

my_text = """
Python is a high-level, interpreted programming language. 
Its design philosophy emphasizes code readability with the 
use of significant indentation. Python is dynamically-typed 
and garbage-collected. It supports multiple programming 
paradigms, including structured, object-oriented, 
and functional programming.
"""

# 1. Get Keywords
keywords = adipylib.extract_keywords(my_text)
print(f"Keywords: {keywords}")

# 2. Get a Summary
summary = adipylib.extractive_summary(my_text, num_sentences=2)
print(f"Summary: {summary}")
```

## Bugs Reporting and Contributions

Found a bug or have a feature request? Feel free to check the [issues page](https://github.com/adityarana2610/adipylib/issues). Any contributions are welcome!
