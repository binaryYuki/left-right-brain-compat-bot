import logging
import os
import chromadb.utils.embedding_functions as embedding_functions
from langchain_community.document_loaders import TextLoader

model_name = "text-embedding-3-large"

logging.basicConfig(level=logging.INFO)


async def doEmbedding(txt_path: str):
    # with open(txt_path, "r") as f:
    data = """
        OSError: [Errno 63] File name too long: 'This repository contains code and resources for demonstrating the power of Chroma and LangChain for asking questions about your own data. The demo showcases how to pull data from the English Wikipedia using their API. The project also demonstrates how to vectorize data in chunks and get embeddings using OpenAI embeddings model.\n\nWe then use LangChain to ask questions based on our data which is vectorized using OpenAI embeddings model. I used Chroma a database for storing and querying vectorized data.\n\n'
        """
    loader = TextLoader(data)
    docs = loader.load()
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.environ["GITHUB_TOKEN"],
        api_base="https://models.inference.ai.azure.com",
        model_name="text-embedding-3-large"
    )

    embeddings = openai_ef.embed(docs)
    # save embeddings to chromaDB

    return embeddings


if __name__ == "__main__":
    import asyncio
    import dotenv

    dotenv.load_dotenv()
    x = asyncio.run(doEmbedding("data.txt"))
    for i in x:
        print(i)
