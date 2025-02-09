import datetime
import json

import httpx
import os
import logging

logging.basicConfig(level=logging.INFO)


async def search_with_keyword(keyword: str) -> str:
    """
    search_with_keyword
    :param keyword:
    :return:
    """
    after = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    before = datetime.datetime.now().strftime("%Y-%m-%d")
    keyword = f"{keyword} since:{after} until:{before}"
    url = f"https://www.googleapis.com/customsearch/v1?key={os.environ.get('GOOGLE_CUSTOME_SEARCH_API_KEY')}&q={keyword}&cx={os.environ.get('GOOGLE_CX')}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        logging.info("Attempting to search on Google, keyword:" + keyword)
        response.raise_for_status()
        data = response.json()
        # to string
        return json.dumps(data) # return json data


if __name__ == "__main__":
    import asyncio
    import dotenv
    dotenv.load_dotenv()
    x = asyncio.run(search_with_keyword("bitcoin status"))
    print(x)