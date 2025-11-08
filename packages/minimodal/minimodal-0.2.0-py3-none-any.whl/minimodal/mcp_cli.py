"""Command-line interface for the minimodal MCP server."""

import click
import asyncio
from .mcp_server import run_stdio_server, run_sse_server


@click.command()
@click.option(
    "--port",
    default=8000,
    help="Port to listen on for SSE transport",
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type (stdio or sse)",
)
def main(port: int, transport: str) -> int:
    """Start the minimodal MCP server.
    
    This server exposes CUDA compilation and execution capabilities through the
    Model Context Protocol, enabling AI agents to compile and run CUDA kernels
    on local GPUs or Modal cloud infrastructure.
    
    Examples:
        
        minimodal-mcp                           # Start with stdio transport
        
        minimodal-mcp --transport sse           # Start with SSE transport
        
        minimodal-mcp --transport sse --port 9000  # Start with SSE on custom port
    """
    
    if transport == "sse":
        click.echo(f"Starting minimodal MCP server with SSE transport on port {port}")
        asyncio.run(run_sse_server(port))
    else:
        click.echo("Starting minimodal MCP server with stdio transport")
        asyncio.run(run_stdio_server())
    
    return 0


if __name__ == "__main__":
    main()
