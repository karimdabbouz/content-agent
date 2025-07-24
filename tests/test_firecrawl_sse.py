import sys
import os
import logfire
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE, MCPServerHTTP, MCPServerStreamableHTTP, MCPServerStdio
import asyncio
from dotenv import load_dotenv
from schemas import OutputText

load_dotenv()

LOGFIRE_TOKEN = os.getenv('LOGFIRE_TOKEN')
logfire.configure(token=LOGFIRE_TOKEN)
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)

FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')
FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

# server = MCPServerSSE(url=FIRECRAWL_URL)
# server = MCPServerStreamableHTTP(FIRECRAWL_URL)
# server = MCPServerHTTP(FIRECRAWL_URL)
server = MCPServerStdio(  
    'npx',
    args=[
        '-y',
        'firecrawl-mcp'
    ]
)
agent = Agent('openai:gpt-4o-mini', toolsets=[server], output_type=OutputText)

async def main():
    async with agent:
        result = await agent.run('get the content of the wikipedia article on paderborn and summarize it in maximum five sentences.')
    print(result.output)

if __name__ == '__main__':
    asyncio.run(main()) 