# src/my_nlp_package/sentiment.py

from nltk.sentiment import SentimentIntensityAnalyzer

_sia = SentimentIntensityAnalyzer()

# MAKE SURE THIS LINE IS SPELLED EXACTLY RIGHT
def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text string.
    """
    if not isinstance(text, str):
        return {"error": "Input must be a string."}
    
    return _sia.polarity_scores(text)