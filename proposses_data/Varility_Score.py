import polars as pl
import numpy as np
from datetime import datetime, date
from typing import List, Dict

def convert_tweet_date(date_value) -> datetime.date:
    """
    Converts a date string like 'Feb 07' into a proper datetime.date object.
    Assumes the current year if the year is missing.
    """
    if isinstance(date_value, datetime):  
        return date_value.date()  # Already a datetime object

    if isinstance(date_value, date):  
        return date_value  # Already a date object

    if isinstance(date_value, str):  
        try:
            # Append current year if only month and day are present
            return datetime.strptime(date_value + f" {datetime.now().year}", "%b %d %Y").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {date_value}")

    raise ValueError(f"Unsupported date format: {date_value}")



def parse_twitter_date(date_str: str) -> datetime:
    """Parse Twitter's 'created_at' string into a datetime object"""
    return datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')

def time_decay_factor(tweet_date: date, decay_rate: float = 0.85) -> float:
    """Apply exponential time decay based on post age"""
    if not isinstance(tweet_date, date):
        raise ValueError(f"Invalid date format: {tweet_date}")
    
    current_date = datetime.now().date()  # Get today's date
    age_in_years = (current_date - tweet_date).days / 365.0
    return decay_rate ** age_in_years

def calculate_engagement(post: Dict) -> int:
    """Calculate total engagement for a single post"""
    return (
        post.get('tweet_reply_count', 0) +
        post.get('tweet_retweet_count', 0) +
        post.get('tweet_like_count', 0) +
        post.get('tweet_quote_count', 0) +
        post.get('tweet_bookmark_count', 0)
    )

def user_influence_factor(post: Dict, max_followers: int) -> float:
    """Compute influence factor based on followers (log-scaled)"""
    followers = post.get('user_followers_count', 1)  # Use 'user_followers_count' (corrected key)
    return np.log1p(followers) / np.log1p(max_followers)

def cap_outliers(values, percentile=95):
    """Caps values at the given percentile to prevent extreme outliers"""
    cap_value = np.percentile(values, percentile)
    return np.clip(values, 0, cap_value)  # Clip values to prevent outliers

def calculate_virality(posts: List[Dict], epsilon: float = 1e-8) -> List[float]:
    """
    Calculate Virality Score (V) for a series of posts.

    Args:
        posts: List of post dictionaries with engagement metrics and 'tweet_date'
        epsilon: Small value to prevent division by zero

    Returns:
        List of virality scores (one per post)
    """
    if len(posts) < 2:
        return [0.0] * len(posts)  # Not enough data, return zeros

    # Ensure all tweet_date values are converted to datetime.date
    for post in posts:
        post["tweet_date"] = convert_tweet_date(post["tweet_date"])  # Convert date string to datetime.date

    # Sort posts chronologically based on 'tweet_date'
    sorted_posts = sorted(posts, key=lambda x: x["tweet_date"])

    # Compute engagements and handle outliers
    engagements = np.array([calculate_engagement(post) for post in sorted_posts])
    engagements = cap_outliers(engagements)

    # Compute max followers for normalization
    max_followers = max(post.get('user_followers_count', 1) for post in posts)

    virality_scores = []
    total_growth = 0.0
    valid_periods = 0

    # Calculate relative growth between consecutive engagements
    for i in range(len(engagements)):  # Process each post separately
        if i == 0:
            virality_scores.append(0.0)  # First post has no previous comparison
            continue

        prev = engagements[i - 1]
        current = engagements[i]

        if prev + epsilon == 0:
            virality_scores.append(0.0)  # No valid comparison, append zero
            continue

        growth_rate = (current - prev) / (prev + epsilon)

        # Apply time decay using tweet_date
        growth_rate *= time_decay_factor(sorted_posts[i]["tweet_date"])

        # Apply user influence factor
        growth_rate *= user_influence_factor(sorted_posts[i], max_followers)

        virality_scores.append(growth_rate)
        total_growth += growth_rate
        valid_periods += 1

    return virality_scores  # Return a list of per-post virality scores


def calculate_virality_scores(df: pl.DataFrame) -> pl.DataFrame:
    """
    Adds virality scores to a Polars DataFrame.

    Args:
        df: Polars DataFrame containing post and user data.

    Returns:
        Updated DataFrame with 'virality_score' column (one score per row).
    """
    if "tweet_date" not in df.columns:
        raise ValueError(f"Column 'tweet_date' not found. Available columns: {df.columns}")

    # Convert date string to date type
    df = df.with_columns(
        pl.col("tweet_date").str.strptime(pl.Date, "%b %d", strict=False)
    )

    # Convert DataFrame to list of dictionaries for processing
    posts = df.to_dicts()

    # Compute virality scores
    virality_scores = calculate_virality(posts)

    # Add virality scores as a column
    return df.with_columns(pl.Series("virality_score", virality_scores))
