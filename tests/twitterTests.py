import pytest
import httpx
from adapters.twitter import get_tweets_by_keyword


@pytest.mark.asyncio
async def returns_tweets_for_valid_keyword():
    """
    Test that the function returns tweets for a valid keyword
    :return:
    """
    keyword = "python"
    api_key = "valid_api_key"
    response_data = {"data": [{"id": "1", "text": "Tweet about python"}]}

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                """
                Mock the raise_for_status method
                """
                pass

            def json(self):
                """
                Mock the json method
                :return:
                """
                return response_data

        return MockResponse()

    httpx.AsyncClient.get = mock_get
    result = await get_tweets_by_keyword(keyword, api_key)
    assert result == response_data


@pytest.mark.asyncio
async def handles_missing_api_key():
    keyword = "python"
    response_data = {"data": [{"id": "1", "text": "Tweet about python"}]}

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return response_data

        return MockResponse()

    httpx.AsyncClient.get = mock_get
    result = await get_tweets_by_keyword(keyword)
    assert result == response_data


@pytest.mark.asyncio
async def handles_no_results():
    keyword = "nonexistentkeyword"
    api_key = "valid_api_key"
    response_data = {"data": []}

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return response_data

        return MockResponse()

    httpx.AsyncClient.get = mock_get
    result = await get_tweets_by_keyword(keyword, api_key)
    assert result == response_data


@pytest.mark.asyncio
async def handles_invalid_api_key():
    keyword = "python"
    api_key = "invalid_api_key"

    async def mock_get(*args, **kwargs):
        class MockResponse:
            def raise_for_status(self):
                raise httpx.HTTPStatusError("Unauthorized", request=None, response=None)

        return MockResponse()

    httpx.AsyncClient.get = mock_get
    with pytest.raises(httpx.HTTPStatusError):
        await get_tweets_by_keyword(keyword, api_key)
