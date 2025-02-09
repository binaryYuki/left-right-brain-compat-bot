import datetime
import json
from typing import Optional
import httpx
import os
import dotenv
import logging

logging.getLogger().setLevel(logging.INFO)

dotenv.load_dotenv()


async def search_tweets_by_user(start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    search_tweets_by_keyword
    :param start_date:
    :param end_date:
    :return:
    """
    url = "https://apis.datura.ai/twitter"

    # parse whiteListedUsers
    with open(os.path.join(os.path.dirname(__file__), "whiteLists.txt")) as file:
        queryUser = "("
        # each line is a user name, we need to add "from:" before each user name
        whiteNamedUsers = file.readlines()
        for user in whiteNamedUsers:
            queryUser += f"from:{user} OR "
    # remove the last "OR" and add ")"
    queryUser = queryUser[:-14] + ")"
    queryUser = queryUser.replace("\n", "")
    resultLists = []
    for i in range(7):
        current_date = datetime.datetime.now() - datetime.timedelta(days=i)
        date = current_date.strftime("%Y-%m-%d")
        payload = {
            "query": f"{queryUser} until:{date} since:{date}",
        }
        logging.info(f"payload: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=30)
            try:
                response = response.json()
            except json.JSONDecodeError:
                continue
            resultLists.append(response)
    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as file:
        file.write(json.dumps(resultLists))
    return resultLists


async def search_replies_by_post(post_id: str):
    """
    search_replies_by_post
    :return:
    """
    url = "https://apis.datura.ai/twitter"
    payload = {
        "query": f"conversation_id:1887885750043046215",
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30)
        with open(os.path.join(os.path.dirname(__file__), "results_reply.json"), "w") as file:
            file.write(json.dumps(response.json()))
        return response.json()


async def getTwitterSelected():
    """
    getTwitterSelected
    :return:
    """
    return await search_tweets_by_user()


if __name__ == "__main__":
    import asyncio

    data = asyncio.run(search_tweets_by_user())
    with open(os.path.join(os.path.dirname(__file__), "results.json")) as file:
        data = json.loads(file.read())
    for i in data:
        for j in i:
            id = j["user"]["id"]
            logging.info(f"j: {j}")
            logging.info(f"id: {id}")
            print(asyncio.run(search_replies_by_post("1887885750043046215")))
            exit()  # only search for one post
