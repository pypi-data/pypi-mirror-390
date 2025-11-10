import asyncio
from .common import logger, mcp

async def main():
    
    # Log server startup
    logger.info("Starting INE MCP server...")
    
    # Import tools and resources
    from . import tools
    
    # Run the mcp server
    logger.info("Running MCP server...")
    await mcp.run_stdio_async()

if __name__ == "__main__":
    # Direct script execution entry point
    asyncio.run(main())
