import asyncio

from httpx import AsyncClient, Response


async def download_files(session: AsyncClient, urls: list[str]) -> list[Response]:
    """Downloads multiple files asynchronously.

    Args:
        session: The aiohttp client session.
        urls: A list of URLs to download.

    Returns:
        list[Response]: A list of Response objects for each URL.
    """
    tasks = []
    for url in urls:
        task = asyncio.create_task(download_file(session, url))
        tasks.append(task)

    return await asyncio.gather(*tasks)


async def download_file(session: AsyncClient, url: str) -> Response:
    """Downloads a single file asynchronously.

    Args:
        session: The aiohttp client session.
        url: The URL to download.

    Returns:
        Response: The response object containing the result of the request.
    """
    return await session.get(url)
