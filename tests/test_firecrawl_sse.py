import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
import asyncio
from dotenv import load_dotenv
from schemas import OutputText

load_dotenv()
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')
FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

server = MCPServerSSE(url=FIRECRAWL_URL)
print(server)
agent = Agent('openai:gpt-4o-mini', mcp_servers=[server], output_type=OutputText)

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('do a web search for product reviews on the lego set with number 10329 named tiny plants. visit exactly 3 reviews, read them and use the information to write a new review.')
    print(result.output)

if __name__ == '__main__':
    asyncio.run(main()) 