"Auth module managing user authentication for A2A server"

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from aixtools.auth.auth import AccessTokenAuthProvider, AuthTokenError
from aixtools.logging.logging_config import get_logger
from aixtools.utils import config

logger = get_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):  # pylint: disable=too-few-public-methods
    """
    Middleware that enforces access token authentication for A2A route.
    """

    AGENT_CARD_PATH_SUFFIXES = [".well-known/agent.json", ".well-known/agent-card.json"]
    APP_DEFAULT_SCOPE = config.APP_DEFAULT_SCOPE

    def __init__(self, app, provider: AccessTokenAuthProvider):
        super().__init__(app)
        self.provider = provider

    async def dispatch(self, request: Request, call_next):
        """
        Auth middleware function that checks whether the request has a valid access token.

        :param request: The incoming http request
        :param call_next: The next function in the chain
        :raises HTTPException: If an access token isn't valid or missing
        """

        path = request.url.path

        # allow agent cards to pass
        if any(path.endswith(suffix) for suffix in self.AGENT_CARD_PATH_SUFFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        try:
            await self.provider.verify_auth_header(auth_header)
            return await call_next(request)
        except AuthTokenError as e:
            raise e.to_http_exception(self.APP_DEFAULT_SCOPE)
