"""Utilities for handling A2A SDK agent cards and connections."""

import asyncio

import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.server.agent_execution import RequestContext
from a2a.types import AgentCard, PushNotificationConfig
from a2a.utils import AGENT_CARD_WELL_KNOWN_PATH, PREV_AGENT_CARD_WELL_KNOWN_PATH

from aixtools.a2a.google_sdk.remote_agent_connection import RemoteAgentConnection
from aixtools.context import (
    DEFAULT_SESSION_ID,
    DEFAULT_USER_ID,
    HTTP_SESSION_ID_HEADER,
    HTTP_USER_ID_HEADER,
    SessionIdTuple,
)
from aixtools.logging.logging_config import get_logger
from aixtools.server.utils import create_session_headers

logger = get_logger(__name__)

DEFAULT_A2A_TIMEOUT = 60.0


class AgentCardLoadFailedError(Exception):
    pass


async def get_agent_card(client: httpx.AsyncClient, address: str) -> AgentCard:
    """Retrieve the agent card from the given agent address."""
    warnings = []
    for card_path in [AGENT_CARD_WELL_KNOWN_PATH, PREV_AGENT_CARD_WELL_KNOWN_PATH]:
        try:
            card_resolver = A2ACardResolver(client, address, card_path)
            card = await card_resolver.get_agent_card()
            card.url = address
            return card
        except Exception as e:
            warnings.append(f"Error retrieving agent card from {address} at path {card_path}: {e}")

    for warning in warnings:
        logger.warning(warning)
    raise AgentCardLoadFailedError(f"Failed to load agent card from {address}")


class _AgentCardResolver:
    """Helper class to resolve and manage agent cards and their connections."""

    def __init__(
        self, client: httpx.AsyncClient, push_notification_configs: list[PushNotificationConfig] | None = None
    ):
        self._httpx_client = client
        self._a2a_client_factory = ClientFactory(
            ClientConfig(
                httpx_client=self._httpx_client, polling=True, push_notification_configs=push_notification_configs or []
            )
        )
        self.clients: dict[str, RemoteAgentConnection] = {}

    def register_agent_card(self, card: AgentCard):
        remote_connection = RemoteAgentConnection(card, self._a2a_client_factory.create(card))
        self.clients[card.name] = remote_connection

    async def retrieve_card(self, address: str):
        try:
            card = await get_agent_card(self._httpx_client, address)
            self.register_agent_card(card)
            return
        except Exception as e:
            logger.error(f"Error retrieving agent card from {address}: {e}")
            return

    async def get_a2a_clients(self, agent_hosts: list[str]) -> dict[str, RemoteAgentConnection]:
        async with asyncio.TaskGroup() as task_group:
            for address in agent_hosts:
                task_group.create_task(self.retrieve_card(address))

        return self.clients


async def get_a2a_clients(
    agent_hosts: list[str],
    session_id_tuple: SessionIdTuple,
    auth_token: str = None,
    push_notification_config_url: str | None = None,
    *,
    timeout: float = DEFAULT_A2A_TIMEOUT,
) -> dict[str, RemoteAgentConnection]:
    """Get A2A clients for all agents defined in the configuration."""
    push_notification_configs = (
        [PushNotificationConfig(url=push_notification_config_url)] if push_notification_config_url else None
    )

    headers = create_session_headers(session_id_tuple, auth_token)
    httpx_client = httpx.AsyncClient(headers=headers, timeout=timeout, follow_redirects=True)
    clients = await _AgentCardResolver(
        httpx_client, push_notification_configs=push_notification_configs
    ).get_a2a_clients(agent_hosts)
    for client in clients.values():
        logger.info("Using A2A server at: %s", client.get_agent_card().url)
    return clients


def card2description(card: AgentCard) -> str:
    """Convert agent card to a description string."""
    descr = f"{card.name}: {card.description}\n"
    for skill in card.skills:
        descr += f"\t - {skill.name}: {skill.description}\n"
    return descr


def get_session_id_tuple(context: RequestContext) -> SessionIdTuple:
    """Get the user_id, session_id tuple from the request context."""
    headers = context.call_context.state.get("headers", {})
    return headers.get(HTTP_USER_ID_HEADER, DEFAULT_USER_ID), headers.get(HTTP_SESSION_ID_HEADER, DEFAULT_SESSION_ID)


def get_auth_token(context: RequestContext) -> str | None:
    """Get the Authorization bearer token from the request context."""
    headers = context.call_context.state.get("headers", {})
    auth_header = headers.get("Authorization") or headers.get("authorization")
    auth_token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        auth_token = auth_header.split(" ", 1)[1].strip()
    else:
        logger.warning("Cannot find bearer token in Authorization header: %s", auth_header)
    return auth_token
