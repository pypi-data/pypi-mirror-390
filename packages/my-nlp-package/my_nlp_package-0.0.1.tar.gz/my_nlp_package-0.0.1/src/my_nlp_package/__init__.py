# src/my_nlp_package/__init__.py

import nltk

# --- THIS IS THE LINE THAT FIXES YOUR ERROR ---
from .sentiment import analyze_sentiment

# --- Handle NLTK download ---
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading NLTK's 'vader_lexicon' for sentiment analysis...")
    nltk.download('vader_lexicon')