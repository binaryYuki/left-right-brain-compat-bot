import polars as pl
from datetime import datetime

def calculate_conflict_intensity(df: pl.DataFrame) -> pl.DataFrame:
    """
    Computes conflict intensity score and adds ONLY the final column to the original DataFrame.
    Intermediate numerical columns are not retained.
    """
    current_year = datetime.now().year

    # Step 1: Compute temporary conflict ratio separately
    df = df.with_columns(
        ((pl.col("tweet_reply_count") + pl.col("tweet_quote_count")) /
         (pl.col("tweet_like_count") + pl.col("tweet_retweet_count") + 1))
        .alias("__temp_conflict_ratio")
    )

    # Step 2: Compute aggregates separately
    agg_result = (
        df.lazy()
        .select(
            # Aggregates for tweet_reply_count
            q95_reply=pl.col("tweet_reply_count").quantile(0.95),
            min_reply=pl.col("tweet_reply_count").min(),

            # Aggregates for tweet_quote_count
            q95_quote=pl.col("tweet_quote_count").quantile(0.95),
            min_quote=pl.col("tweet_quote_count").min(),

            # Aggregates for conflict_ratio (now exists as __temp_conflict_ratio)
            q95_ratio=pl.col("__temp_conflict_ratio").quantile(0.95),
            min_ratio=pl.col("__temp_conflict_ratio").min(),

            # Max for user influence normalization
            user_influence_max=pl.col("user_followers_count").log1p().max(),
        )
        .collect()
    )

    # Extract scalar values from aggregates
    q95_reply = agg_result["q95_reply"][0]
    min_reply = agg_result["min_reply"][0]
    q95_quote = agg_result["q95_quote"][0]
    min_quote = agg_result["min_quote"][0]
    q95_ratio = agg_result["q95_ratio"][0]
    min_ratio = agg_result["min_ratio"][0]
    user_influence_max = agg_result["user_influence_max"][0]

    # Step 3: Compute final conflict intensity score
    conflict_ratio = (pl.col("tweet_reply_count") + pl.col("tweet_quote_count")) \
                     / (pl.col("tweet_like_count") + pl.col("tweet_retweet_count") + 1)

    norm_reply = (pl.col("tweet_reply_count").clip(0, q95_reply) - min_reply) \
                 / (q95_reply - min_reply + 1e-8)
    norm_quote = (pl.col("tweet_quote_count").clip(0, q95_quote) - min_quote) \
                 / (q95_quote - min_quote + 1e-8)
    norm_ratio = (conflict_ratio.clip(0, q95_ratio) - min_ratio) \
                 / (q95_ratio - min_ratio + 1e-8)

    base_intensity = 0.5 * norm_reply + 0.3 * norm_quote + 0.2 * norm_ratio
    temporal_decay = 0.85 ** (current_year - pl.col("tweet_year").cast(pl.Int32))
    user_influence = pl.col("user_followers_count").log1p() / user_influence_max

    conflict_intensity = (100 * base_intensity * temporal_decay * user_influence).clip(0, 100)

    # Step 4: Add only the final column to the original DataFrame
    return df.drop("__temp_conflict_ratio").with_columns(conflict_intensity=conflict_intensity)