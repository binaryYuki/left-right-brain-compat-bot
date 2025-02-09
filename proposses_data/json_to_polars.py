import json
import polars as pl
import datetime
import tkinter as tk
from tkinter import ttk
from importance_calculator import calculate_importance_scores
from conflict_analysis import calculate_conflict_intensity
from StanceCalculation import calculate_stance_scores
from Varility_Score import calculate_virality_scores

def parse_created_at(created_at):
    """
    Extracts the date, time, and year from the 'created_at' field.
    Example Input: 'Fri Sep 01 20:37:55 +0000 2023'
    Output: ('Sep 01', '20:37:55', '2023')
    """
    if created_at:
        try:
            dt = datetime.datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
            return dt.strftime("%b %d"), dt.strftime("%H:%M:%S"), dt.strftime("%Y")
        except ValueError:
            print(f"Warning: Incorrect date format in {created_at}")
            return None, None, None
    return None, None, None

def flatten_json_to_dataframe(json_data, user_keys, post_keys):
    """
    Flattens user and tweet data into a single-row per record structure for Polars DataFrame.
    """
    records = []
    for days in json_data:
        for tweet in days:
            if "user" not in tweet or not isinstance(tweet["user"], dict):
                print(f"Warning: Missing 'user' key in tweet {tweet.get('id', 'Unknown ID')}")
                continue  # Skip this tweet if "user" is missing

            # Extract user attributes safely
            user_data = {f"user_{key}": tweet["user"].get(key, None) for key in user_keys}

            # Extract tweet attributes safely
            tweet_data = {f"tweet_{key}": tweet.get(key, None) for key in post_keys}

            # Extract date, time, and year from "created_at"
            tweet_date, tweet_time, tweet_year = parse_created_at(tweet_data.pop("tweet_created_at", None))

            # Add extracted date components
            tweet_data["tweet_date"] = tweet_date
            tweet_data["tweet_time"] = tweet_time
            tweet_data["tweet_year"] = tweet_year

            # Merge both user and tweet data into a single flat record
            record = {**user_data, **tweet_data}
            records.append(record)

    return pl.DataFrame(records) if records else pl.DataFrame()  # Return empty DF if no data

def load_json(file_path):
    """
    Loads a JSON file and ensures it's formatted correctly.
    If it's a single object, converts it into a list.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        try:
            json_data = json.load(file)  # Load JSON file
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")

    # Ensure JSON is a list
    if isinstance(json_data, dict):
        json_data = [json_data]

    return json_data

def display_dataframe_gui(df):
    """Displays the Polars DataFrame in a scrollable Tkinter table"""
    root = tk.Tk()
    root.title("Twitter Data Analysis")
    root.geometry("1200x600")

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb = ttk.Scrollbar(root, orient="horizontal", command=tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)

    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree["columns"] = df.columns
    tree["show"] = "headings"

    for col in df.columns:
        clean_name = col.replace("_", " ").title()
        tree.heading(col, text=clean_name)
        tree.column(col, width=150, anchor=tk.W)

    for row in df.iter_rows(named=True):
        values = [str(row[col]) for col in df.columns]
        tree.insert("", tk.END, values=values)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                   background="white",
                   foreground="black",
                   rowheight=25,
                   fieldbackground="white")
    style.map('Treeview', background=[('selected', '#347083')])

    root.mainloop()

# Modify the main block to include conflict calculation
if __name__ == "__main__":
    json_file_path = "results(4).json"

    # Define keys to extract
    user_keys = ["id", "username", "favourites_count", "followers_count", "listed_count", 
                 "media_count", "statuses_count", "verified", "is_blue_verified"]
    post_keys = ["id", "text", "reply_count", "retweet_count", "like_count", 
                 "quote_count", "bookmark_count", "is_quote_tweet", "is_retweet", "created_at"]

    # Load and process data
    json_data = load_json(json_file_path)
    df = flatten_json_to_dataframe(json_data, user_keys, post_keys)
    
    df = calculate_importance_scores(df)
    df = calculate_conflict_intensity(df)
    df = calculate_stance_scores(df, "tweet_text")
    df = calculate_virality_scores(df)
    df = df.with_columns(
    (pl.col("importance_score") +
     pl.col("conflict_intensity") +
     pl.col("stance_score") +
     pl.col("virality_score")).round(2).alias("final_score")
    )
    # Add conflict intensity calculation

    display_dataframe_gui(df)