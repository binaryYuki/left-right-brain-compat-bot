import json
from typing import Optional
import httpx
import os
import dotenv
import datetime

dotenv.load_dotenv()


async def search_tweets_by_keyword(
        keyword: str,
        api_key: Optional[str] = None,
        start_date: Optional[str] = None,  # Should be in YYYY-MM-DD format
        end_date: Optional[str] = None,  # Should be in YYYY-MM-DD format
        lang: Optional[str] = "en",
        verified: Optional[bool] = None,
        blue_verified: Optional[bool] = None,
        is_quote: Optional[bool] = None,
        is_video: Optional[bool] = False,
        is_image: Optional[bool] = None,
        min_retweets: Optional[int] = None,
        min_replies: Optional[int] = None,
        min_likes: Optional[int] = None
):
    # Define the request URL for the Datura API
    url = "https://apis.datura.ai/twitter"

    if start_date is None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
    if end_date is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Construct the payload based on provided argument
    payload = {
        # "query": f"in_reply_to_tweet_id: 1650626669873618945",
        "query": f"cryptoTrends lang:en -filter:links since:{start_date} until:{end_date}",
        # "query": "from:elonmusk #AI since:2023-01-01 until:2023-12-31",
        # seven dats ago
        "start_date": (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
        "end_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "lang": "en",
        "verified": verified,
        "blue_verified": blue_verified,
        # "is_quote": is_quote,
        # "is_video": False,
        # "is_image": False,
        "min_retweets": 5000,
        "sort": "Top",
        "min_replies": 5000,
        "replies": True,
        "min_likes": 5000,
    }
    print(payload["start_date"])
    print(payload["end_date"])
    # Filter out keys with None values
    payload = {k: v for k, v in payload.items() if v is not None}
    print(payload)

    # Prepare the headers, including authentication
    api_key = api_key if api_key else os.getenv("DATURA_API_KEY")  # Ensure API key is provided or fetched from env
    if not api_key:
        raise ValueError(
            "API key is required either as a function parameter or in the environment as 'DATURA_API_KEY'.")
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    # Send the request using requests
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    # Raise an HTTPError if response status is not 200
    response.raise_for_status()
    print(response.json())

    # Return the JSON response
    return response.json()


if __name__ == "__main__":
    import asyncio

    tweet_ID = "1888167536572690553"
    try:
        # Example usage
        results = asyncio.run(search_tweets_by_keyword(
            keyword=f"(#cryptoTrends OR #CryptoNews OR #Cryptocurrency OR #Bitcoin OR #CryptoNews) min_replies:10 min_faves:20 min_retweets:20 lang:en until:2025-02-09 since:2025-02-03 -filter:links ",
            api_key=os.getenv("DATURA_API_KEY"),  # Provide your API key or source it from .env
        ))
        # Output the results
        print(json.dumps(results, indent=4))
        with open("results.json", "w") as file:
            file.write(json.dumps(results, indent=4))
    except Exception as e:
        print(f"Error: {e}")
