import nltk
import re
import polars as pl
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json

# Force download of necessary resources
nltk.download('punkt_tab')

# Initialize global resources to avoid reloading them on every function call
analyzer = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))
# Adjust these parameters
dampening_factor = 0.8  # Reduced dampening to retain more sentiment
neutral_threshold = 0.1  # Lower threshold to allow more non-zero scores
keyword_strength = 0.2  # Increased keyword impact

# Example domain-specific keywords (customize based on your use case)
positive_keywords = {"bullish", "growth", "innovation", "adopt"}
negative_keywords = {"scam", "crash", "fraud", "risk"}
json_filename = "top_cryptos.json"
try:
    with open(json_filename, "r", encoding="utf-8") as json_file:
        topic_keywords = set(json.load(json_file))  # Convert list to set for faster lookup

except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"❌ Error loading topic keywords: {e}")
    topic_keywords = set()  # Fallback to an empty set if loading fails

def preprocess_text(text: str) -> list:
    """Preprocess tweet text for tokenization."""
    text = re.sub(r'[^\w\s]', '', text.lower())
    tokens = word_tokenize(text)
    return [word for word in tokens if word not in stop_words]

def is_topic_related(tokens: list) -> bool:
    """Check if the tweet is relevant to the specified topic."""
    return any(word in topic_keywords for word in tokens)

def calculate_stance(text: str) -> float:
    tokens = preprocess_text(text)
    
    if not is_topic_related(tokens):
        return 0.0
    
    # Adjusted: Use raw sentiment score with less dampening
    sentiment_score = analyzer.polarity_scores(" ".join(tokens))['compound']
    stance_score = sentiment_score * dampening_factor
    
    # Adjusted: Apply keyword adjustments BEFORE neutral check
    keyword_adjustment = sum(
        keyword_strength if word in positive_keywords 
        else -keyword_strength if word in negative_keywords 
        else 0 
        for word in tokens
    )
    stance_score += keyword_adjustment
    
    # Adjusted: Only apply neutral threshold after keyword adjustments
    if abs(stance_score) < neutral_threshold:
        stance_score = 0.0
    
    # Clamp to [-1.0, 1.0] for more variance
    return round(max(min(stance_score, 1.0), -1.0), 2)

def calculate_stance_scores(df: pl.DataFrame, text_column: str) -> pl.DataFrame:
    """
    Adds stance scores to a Polars DataFrame without modifying existing columns.

    Args:
        df (pl.DataFrame): Input DataFrame containing text data.
        text_column (str): Name of the column containing text to analyze.

    Returns:
        pl.DataFrame: DataFrame with added 'stance_score' column.
    """
    stance_scores = df.with_columns(
        pl.col(text_column).map_elements(
            lambda x: calculate_stance(x),
            return_dtype=pl.Float64
        ).alias("stance_score")
    )

    return df.with_columns(stance_scores["stance_score"])