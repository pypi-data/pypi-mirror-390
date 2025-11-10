"""
autoINcorrect: A package to intentionally introduce human-like errors into text.
"""

# Import the main public-facing functions from the pipeline.py file
# This "promotes" them to the top level of the package
from .pipeline import auto_incorrect
from .pipeline import word_error
from .pipeline import corrupt_format
from .pipeline import download_nltk_data

# Define what functions are exported when a user types `from auto_incorrect import *`
__all__ = [
    'auto_incorrect',
    'word_error',
    'corrupt_format',
    'download_nltk_data'
]

# You can also set the package version here
__version__ = "0.0.2"
