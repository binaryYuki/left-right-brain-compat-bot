import json
import os
from utils.sentiment import adBlockers


async def run():
    """
    Run the function
    """
    with open(os.path.join(os.path.dirname(__file__), "results.json")) as file:
        data = json.loads(file.read())
        ls = []
        for i in data:
            ls.append(i["user"]["description"])
        ls = list(set(ls))
        f = await adBlockers(ls)
        print(f)


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
