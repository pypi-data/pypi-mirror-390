# src/my_nlp_package/__init__.py

import nltk

# --- STEP 1: DOWNLOAD THE MODEL ---
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading NLTK's 'vader_lexicon' for sentiment analysis...")
    nltk.download('vader_lexicon')

# --- STEP 2: NOW IMPORT OUR FUNCTION ---
from .sentiment import analyze_sentiment