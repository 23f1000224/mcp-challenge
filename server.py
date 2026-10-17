
import contextvars
import hashlib
import os

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "23f1000224@ds.study.iitm.ac.in"

# Stores the challenge for the current HTTP request.
current_challenge = contextvars.ContextVar(
    "current_challenge", default=None
)

mcp = FastMCP("Exam Challenge Server")


@mcp.tool()
def solve_challenge() -> str:
    """Return the required hash for this request's challenge."""
    challenge = current_challenge.get()

    if challenge is None:
        raise ValueError("Challenge header is missing")

    if len(challenge) != 32 or any(
        c not in "0123456789abcdef" for c in challenge
    ):
        raise ValueError("Invalid challenge")

    message = f"{challenge}:{EMAIL}"
    return hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]


class ChallengeHeaderMiddleware:
    """Capture the challenge header for each HTTP request."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }

        challenge = headers.get("x-exam-challenge")
        token = current_challenge.set(challenge)

        try:
            await self.app(scope, receive, send)
        finally:
            current_challenge.reset(token)


if __name__ == "__main__":
    app = ChallengeHeaderMiddleware(mcp.streamable_http_app())

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )

