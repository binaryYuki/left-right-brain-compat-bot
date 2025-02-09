import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import polars as pl

def preprocess_text(text: str) -> str:
    """Clean tweet text for TF-IDF analysis"""
    if not text:
        return ""
    
    # Basic text cleaning
    text = text.lower()
    text = re.sub(r"http\S+|www\S+|@\w+|#", "", text)  # Remove URLs, mentions, hashtags
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text.strip()

def calculate_importance_scores(df: pl.DataFrame) -> pl.DataFrame:
    """Calculate Issue Importance Scores using TF-IDF and engagement"""
    # Convert to pandas for sklearn compatibility
    pandas_df = df.to_pandas()
    
    # Preprocess text
    pandas_df["cleaned_text"] = pandas_df["tweet_text"].apply(preprocess_text)
    
    # Calculate TF-IDF scores
    tfidf = TfidfVectorizer(max_features=1000, stop_words="english")
    tfidf_matrix = tfidf.fit_transform(pandas_df["cleaned_text"])
    
    # Get sum of TF-IDF scores per tweet
    tfidf_sums = np.asarray(tfidf_matrix.sum(axis=1)).flatten()
    pandas_df["tfidf_score"] = tfidf_sums
    
    # Normalize engagement metrics
    engagement_metrics = ["tweet_like_count", "tweet_retweet_count", 
                         "tweet_reply_count", "tweet_quote_count"]
    
    for metric in engagement_metrics:
        pandas_df[f"norm_{metric}"] = (
            pandas_df[metric] - pandas_df[metric].min()
        ) / (pandas_df[metric].max() - pandas_df[metric].min() + 1e-8)
    
    # Create composite scores
    pandas_df["engagement_score"] = pandas_df[[f"norm_{m}" for m in engagement_metrics]].sum(axis=1)
    pandas_df["importance_score"] = pandas_df["tfidf_score"] * pandas_df["engagement_score"]
    
    # Normalize to 0-100 scale
    max_score = pandas_df["importance_score"].max()
    if max_score > 0:
        pandas_df["importance_score"] = 100 * pandas_df["importance_score"] / max_score
    
    # Convert back to Polars and merge with original DataFrame
    importance_scores_pl = pl.from_pandas(pandas_df[["importance_score"]])
    
    return df.with_columns(importance_scores_pl["importance_score"])
