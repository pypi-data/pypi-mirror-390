"""OpenAPI MCP Server."""

import contextlib
import logging
from enum import Enum
from typing import AsyncIterator, List

import anyio
import uvicorn
from axmp_openapi_helper import (
    APIServerConfig,
    AuthConfig,
    AuthenticationType,
    MultiOpenAPIHelper,
)
from httpx import BasicAuth
from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import FileUrl, GetPromptResult, Prompt, Resource, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

logger = logging.getLogger(__name__)

MCP_SERVER_SEPARATOR = "---"
"""Separator for the MCP server's authentication header

  The client should set the authentication header with the following format:
  For the APIKey authentication:
      openapi_server_name---api_key_name=api_key_value
  For the Bearer authentication:
      openapi_server_name---bearer_token=bearer_token
  For the Basic authentication:
      openapi_server_name---username=username
      openapi_server_name---password=password
"""

MCP_PROFILE_PREFIX = "mcp_profile_"
BACKEND_SERVER_PREFIX = "backend_server_"


class TransportType(str, Enum):
    """Transport type for MCP and Gateway."""

    SSE = "sse"
    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"


class AuthHeaderKey(str, Enum):
    """Auth header key for the MCP server."""

    BEARER_TOKEN = "bearer_token"
    USERNAME = "username"
    PASSWORD = "password"


def get_http_request() -> Request:
    """Get the HTTP request from the context."""
    from mcp.server.lowlevel.server import request_ctx

    request = None
    with contextlib.suppress(LookupError):
        request = request_ctx.get().request

    if request is None:
        raise RuntimeError("No active HTTP request found.")
    return request


def get_http_headers(include_all: bool = False) -> dict[str, str]:
    """Extract headers from the current HTTP request if available.

    Never raises an exception, even if there is no active HTTP request (in which case
    an empty dict is returned).

    By default, strips problematic headers like `content-length` that cause issues if forwarded to downstream clients.
    If `include_all` is True, all headers are returned.
    """
    if include_all:
        exclude_headers = set()
    else:
        exclude_headers = {
            "host",
            "content-length",
            "connection",
            "transfer-encoding",
            "upgrade",
            "te",
            "keep-alive",
            "expect",
            "accept",
            # Proxy-related headers
            "proxy-authenticate",
            "proxy-authorization",
            "proxy-connection",
            # MCP-related headers
            "mcp-session-id",
        }
        # (just in case)
        if not all(h.lower() == h for h in exclude_headers):
            raise ValueError("Excluded headers must be lowercase")
    headers = {}

    try:
        request = get_http_request()
        for name, value in request.headers.items():
            lower_name = name.lower()
            if lower_name not in exclude_headers:
                headers[lower_name] = str(value)
        return headers
    except RuntimeError:
        return {}


class OpenAPIMCPServer:
    """OpenAPI MCP Server."""

    def __init__(
        self,
        name: str = "axmp-openapi-mcp-server",
        transport_type: TransportType = TransportType.STREAMABLE_HTTP,
        port: int = 9999,
        multi_openapi_helper: MultiOpenAPIHelper = None,
    ):
        """Initialize the server."""
        self.name = name
        self.port = port
        self.transport_type = transport_type
        self.multi_openapi_helper = multi_openapi_helper
        self.app = Server(self.name)
        self._initialize_app()

        self.openapi_helper_clients_initialized = False

    def _initialize_app(self):
        """Initialize the app."""

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Call the tool with the given name and arguments from llm."""
            logger.debug("-" * 100)
            logger.debug(f"::: tool name: {name}")
            logger.debug("::: arguments:")
            for key, value in arguments.items():
                logger.debug(f"\t{key}: {value}")
            logger.debug("-" * 100)

            operation = next(
                (
                    op
                    for op in self.multi_openapi_helper.all_operations
                    if op.name == name
                ),
                None,
            )

            if operation is None:
                logger.error(f"MCP Server does not have the tool: {name}")
                return [TextContent(type="text", text=f"Error: Unknown tool: {name}")]

            if self.transport_type == TransportType.STREAMABLE_HTTP:
                headers = get_http_headers()
                logger.info(f"Tool request headers: {headers}")
                server_headers, basic_auth = (
                    self._get_header_and_basic_auth_from_request_headers(
                        server_name=operation.server_name,
                        headers=headers,
                    )
                )
            elif self.transport_type == TransportType.STDIO:
                server_name = operation.server_name
                auth_config = self.multi_openapi_helper.openapi_servers[
                    server_name
                ].auth_config
                server_headers, basic_auth = (
                    self._get_headers_and_basic_auth_from_auth_config(
                        server_name=server_name,
                        auth_config=auth_config,
                    )
                )
            else:
                logger.error(f"Unsupported transport type: {self.transport_type}")
                return [
                    TextContent(
                        type="text",
                        text=f"Error: Unsupported transport type: {self.transport_type}",
                    )
                ]

            logger.info(
                f"Server [{operation.server_name}] headers: {server_headers}, basic auth: {basic_auth}"
            )

            try:
                result = await self.multi_openapi_helper.run(
                    name=name,
                    args=arguments,
                    headers=server_headers,
                    auth=basic_auth,
                )

                return [TextContent(type="text", text=f"result: {result}")]
            except Exception as e:
                logger.error(f"Error: {e}")
                return [TextContent(type="text", text=f"Error: {e}")]

        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            """List all the tools available."""
            tools: List[Tool] = []
            for operation in self.multi_openapi_helper.all_operations:
                tool: Tool = Tool(
                    name=operation.name,
                    description=operation.description,
                    inputSchema=operation.args_schema.model_json_schema(),
                )
                tools.append(tool)

                logger.debug("-" * 100)
                logger.debug(f"::: tool: {tool.name}\n{tool.inputSchema}")

            return tools

        @self.app.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List all the prompts available."""
            prompts: List[Prompt] = []
            return prompts

        @self.app.get_prompt()
        async def get_prompt(
            name: str, arguments: dict[str, str] | None = None
        ) -> GetPromptResult:
            """Get the prompt with the given name and arguments."""
            return None

        @self.app.list_resources()
        async def list_resources() -> list[Resource]:
            """List all the resources available."""
            resources: List[Resource] = []
            return resources

        @self.app.read_resource()
        async def read_resource(uri: FileUrl) -> str | bytes:
            """Read the resource with the given URI."""
            return None

    def _get_headers_and_basic_auth_from_auth_config(
        self, *, server_name: str, auth_config: AuthConfig
    ) -> tuple[dict[str, str], BasicAuth | None]:
        """Get the headers and basic authentication from the authentication configuration."""
        headers: dict[str, str] = {}
        basic_auth: BasicAuth | None = None
        if auth_config.type == AuthenticationType.API_KEY:
            headers[auth_config.api_key_name.lower()] = auth_config.api_key_value
        elif auth_config.type == AuthenticationType.BEARER:
            headers["Authorization"] = f"Bearer {auth_config.bearer_token}"
        elif auth_config.type == AuthenticationType.BASIC:
            basic_auth = BasicAuth(auth_config.username, auth_config.password)

        logger.info(
            f"Server [{server_name}] headers: {headers}, basic auth: {basic_auth}"
        )
        return headers, basic_auth

    def _get_header_and_basic_auth_from_request_headers(
        self, *, server_name: str, headers: dict[str, str]
    ) -> tuple[dict[str, str], BasicAuth | None]:
        """Get the authentication headers and basic authentication from the request headers."""
        logger.info(
            f"Generating the authentication headers for the backend server [{server_name}] from the request headers: {headers}"
        )

        openapi_server: APIServerConfig = self.multi_openapi_helper.openapi_servers[
            server_name
        ]
        auth_config: AuthConfig = openapi_server.auth_config
        basic_auth_username: str | None = None
        basic_auth_password: str | None = None
        server_headers: dict[str, str] = {}

        for key, value in headers.items():
            logger.info(f"Header {key}: {value}")
            key_parts = key.split(MCP_SERVER_SEPARATOR)
            if len(key_parts) == 2 and key_parts[0].lower() == server_name.lower():
                # server_name = key_parts[0]
                key_name = key_parts[1]

                if auth_config.type == AuthenticationType.API_KEY:
                    if key_name.lower() == auth_config.api_key_name.lower():
                        server_headers[key_name] = value
                        logger.info(
                            f"Server [{server_name}] API Key [{key_name}] set to [{value}]"
                        )
                elif auth_config.type == AuthenticationType.BEARER:
                    if key_name.lower() == AuthHeaderKey.BEARER_TOKEN.value:
                        server_headers["Authorization"] = f"Bearer {value}"
                elif auth_config.type == AuthenticationType.BASIC:
                    if key_name.lower() == AuthHeaderKey.USERNAME.value:
                        basic_auth_username = value
                    elif key_name.lower() == AuthHeaderKey.PASSWORD.value:
                        basic_auth_password = value

        return (
            server_headers,
            BasicAuth(basic_auth_username, basic_auth_password)
            if basic_auth_username is not None and basic_auth_password is not None
            else None,
        )

    def run(self):
        """Run the server."""
        # NOTE: SSE has been deprecated in the MCP spec.
        # TODO: remove this after the MCP spec is updated.
        if self.transport_type == TransportType.SSE:
            sse = SseServerTransport("/messages/")

            async def handle_sse(request: Request):
                logger.info(f"::: SSE connection established - request: {request}")
                async with sse.connect_sse(
                    request.scope, request.receive, request._send
                ) as streams:
                    await self.app.run(
                        streams[0], streams[1], self.app.create_initialization_options()
                    )

            starlette_app = Starlette(
                debug=True,
                routes=[
                    Route("/sse", endpoint=handle_sse),
                    Mount("/messages/", app=sse.handle_post_message),
                ],
            )

            uvicorn.run(starlette_app, host="0.0.0.0", port=self.port)
        elif self.transport_type == TransportType.STREAMABLE_HTTP:
            # Create the session manager with true stateless mode
            session_manager = StreamableHTTPSessionManager(
                app=self.app,
                event_store=None,
                json_response=False,
                stateless=True,
            )

            async def handle_streamable_http(
                scope: Scope, receive: Receive, send: Send
            ) -> None:
                logger.info(f"Client request scope: {scope}")
                logger.info("-" * 100)
                headers: list[tuple[bytes, bytes]] = scope.get("headers")
                logger.info(f"Headers: {headers}")

                await session_manager.handle_request(scope, receive, send)

            @contextlib.asynccontextmanager
            async def lifespan(app: Starlette) -> AsyncIterator[None]:
                """Context manager for session manager."""
                async with session_manager.run():
                    logger.info(
                        "Application started with StreamableHTTP session manager!"
                    )
                    try:
                        yield
                    finally:
                        logger.info("Application shutting down...")
                        logger.info("Closing the clients...")
                        # close the clients for releasing the resources
                        await self.multi_openapi_helper.close()

            # Create an ASGI application using the transport
            starlette_app = Starlette(
                debug=True,
                routes=[
                    Mount("/mcp", app=handle_streamable_http),
                ],
                lifespan=lifespan,
            )

            uvicorn.run(starlette_app, host="0.0.0.0", port=self.port)
        else:

            async def arun():
                async with stdio_server() as streams:
                    await self.app.run(
                        streams[0], streams[1], self.app.create_initialization_options()
                    )

            anyio.run(arun)
