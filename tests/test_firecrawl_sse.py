from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')
FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

server = MCPServerSSE(url=FIRECRAWL_URL)
agent = Agent('openai:gpt-4o-mini', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('get the first paragraph of the wikipedia article on bread')
    print(result.output)

if __name__ == '__main__':
    asyncio.run(main()) 