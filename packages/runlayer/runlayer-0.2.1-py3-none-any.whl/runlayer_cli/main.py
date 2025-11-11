import anyio
import sys
from uuid import UUID
import typer
import structlog
import datetime
from typing import Union
from fastmcp import FastMCP
from fastmcp.client.transports import (
    SSETransport,
    StdioTransport,
    StreamableHttpTransport,
)
from fastmcp.server.proxy import ProxyClient
from fastmcp.server.proxy import FastMCPProxy
from runlayer_cli.models import LocalCapabilities

from runlayer_cli.middleware import RunlayerMiddleware
from runlayer_cli.oauth import OAuth
from runlayer_cli.api import RunlayerClient, USER_AGENT
from runlayer_cli import __version__


structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("cli")


def version_callback(value: bool):
    """Show version information."""
    if value:
        typer.echo(f"runlayer version {__version__}")
        raise typer.Exit()


app = typer.Typer(help="Run MCP servers via HTTP transport")


@app.callback()
def main(
    version: bool | None = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
):
    """Runlayer CLI - Run MCP servers via HTTP transport."""


async def sync_local_capabilities(
    runlayer_api_client: RunlayerClient,
    proxy: FastMCPProxy,
    server_id: str,
) -> None:
    tools = await proxy.get_tools()
    resources = await proxy.get_resources()
    prompts = await proxy.get_prompts()

    local_capabilities = LocalCapabilities(
        tools={
            name: t.to_mcp_tool(include_fastmcp_meta=False) for name, t in tools.items()
        },
        resources={
            name: r.to_mcp_resource(include_fastmcp_meta=False)
            for name, r in resources.items()
        },
        prompts={
            name: p.to_mcp_prompt(include_fastmcp_meta=False)
            for name, p in prompts.items()
        },
        synced_at=datetime.datetime.now(datetime.timezone.utc),
    )

    runlayer_api_client.update_capabilities(server_id, local_capabilities)


@app.command(name="run", help="Run an MCP server via HTTP transport")
def run(
    server_uuid: str = typer.Argument(..., help="UUID of the MCP server to run"),
    secret: str = typer.Option(
        ..., "--secret", "-s", help="API secret for authentication"
    ),
    host: str = typer.Option(
        "http://localhost:3000", "--host", "-H", help="Runlayer API host URL"
    ),
):
    runlayer_api_client = RunlayerClient(hostname=host, secret=secret)

    server_details = runlayer_api_client.get_server_details(server_uuid)
    server_name = server_details.name

    headers_dict = {}
    headers_dict["User-Agent"] = USER_AGENT

    transport: Union[SSETransport, StdioTransport, StreamableHttpTransport]
    match server_details.transport_type:
        case "sse":
            transport = SSETransport(
                url=server_details.url,
                headers=headers_dict,
                auth=OAuth(mcp_url=server_details.url, client_name=USER_AGENT),
            )
        case "stdio":
            transport = StdioTransport(
                command=server_details.url,
                args=server_details.transport_config.get("args", []),
                env=server_details.transport_config.get("env", {}),
            )
        case "streaming-http":
            transport = StreamableHttpTransport(
                url=server_details.url,
                headers=headers_dict,
                auth=OAuth(mcp_url=server_details.url, client_name=USER_AGENT),
            )
        case _:
            raise ValueError(f"Unknown transport type: {server_details.transport_type}")

    proxy_client = ProxyClient(transport)
    proxy = FastMCP.as_proxy(proxy_client, name=server_name)

    proxy.add_middleware(
        RunlayerMiddleware(
            runlayer_api_client=runlayer_api_client,
            proxy=proxy,
            server=server_details,
        )
    )

    typer.echo(f"Starting Runlayer CLI with: {server_name} ({server_uuid})")

    try:

        async def tasks():
            if server_details.sync_required:
                await sync_local_capabilities(runlayer_api_client, proxy, server_uuid)
            await proxy.run_stdio_async(
                show_banner=False,
            )

        anyio.run(tasks)
    except KeyboardInterrupt:
        typer.echo("\nShutting down MCP server...")
        logger.info("MCP server shutdown requested by user")
    except Exception as e:
        typer.echo(f"Error running MCP server: {e}", err=True)
        logger.error(
            "Error running MCP server", error=str(e), error_type=type(e).__name__
        )
        raise typer.Exit(1)


def _ensure_backwards_compatibility():
    """Ensure backwards compatibility with the initial CLI release.

    The first version allowed: runlayer <uuid> --secret <key>
    The current version requires: runlayer run <uuid> --secret <key>

    This function detects when a UUID is passed as the first argument
    and automatically inserts the "run" subcommand for backwards compatibility.
    """

    if len(sys.argv) < 2:
        return

    current_command = sys.argv[1]
    commands = app.registered_commands

    if current_command in commands:
        return

    try:
        UUID(current_command)
        sys.argv.insert(1, "run")
    except ValueError:
        pass


def cli():
    _ensure_backwards_compatibility()
    app()


if __name__ == "__main__":
    cli()
