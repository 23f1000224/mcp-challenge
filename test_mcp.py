
import asyncio
import hashlib

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

URL = "http://127.0.0.1:8000/mcp"
EMAIL = "23f1000224@ds.study.iitm.ac.in"


async def main():
    challenges = [
        "0123456789abcdef0123456789abcdef",
        "abcdef0123456789abcdef0123456789",
    ]

    for challenge in challenges:
        headers = {"X-Exam-Challenge": challenge}

        async with streamablehttp_client(
            URL, headers=headers
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = [tool.name for tool in tools.tools]
                print("Tools:", names)

                result = await session.call_tool("solve_challenge", {})
                actual = result.content[0].text
                expected = hashlib.sha256(
                    f"{challenge}:{EMAIL}".encode("utf-8")
                ).hexdigest()[:16]

                print("Actual:  ", actual)
                print("Expected:", expected)
                print("PASS" if actual == expected else "FAIL")


asyncio.run(main())