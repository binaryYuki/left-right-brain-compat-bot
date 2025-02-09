import requests
import emoji
import unicodedata
import json

def is_valid_name(name: str) -> bool:
    """
    Check if the name is a non-empty string without emojis or pictographs.
    
    Uses both the `emoji` library and Unicode category filtering.
    """
    if not isinstance(name, str) or not name.strip():
        return False  # Not a valid string or empty

    # Check for emojis using the emoji module
    if emoji.is_emoji(name):
        return False  # Name contains emoji

    # Check for pictographs and special symbols using Unicode categories
    if any(unicodedata.category(char).startswith(('So', 'Sk')) for char in name):
        return False  # Name contains symbols, pictographs, or currency signs

    return True  # Name is valid

# Fetch CoinGecko market data (sorted by market cap)
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",  # Get prices in USD
    "order": "market_cap_desc",  # Sort by market cap (descending)
    "per_page": 100,  # Fetch top 100 for filtering
    "page": 1,
    "sparkline": False  # No additional graph data
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    coins = response.json()

    # Select top 100 by market cap with valid names
    top_cryptos = [
        coin["name"] for coin in coins if is_valid_name(coin["name"])
    ][:100]  # Take only the top 100 valid names

    # Save as JSON file
    json_filename = "top_cryptos.json"
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(top_cryptos, json_file, indent=4)

    print(f"✅ Successfully saved top 100 cryptocurrency names to {json_filename}")

except requests.exceptions.RequestException as e:
    print(f"❌ An error occurred: {e}")
