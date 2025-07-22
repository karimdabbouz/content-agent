import sys
import os
import logfire
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerSSE
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

server = MCPServerSSE(url=FIRECRAWL_URL)
agent = Agent('openai:gpt-4o-mini', toolsets=[server])

async def main():
    async with agent:
        result = await agent.run('do a web search for product reviews on the amazon fire phone. visit exactly 2 reviews and summarize its content.')
    print(result.output)


# server = MCPServerSSE(url='http://localhost:3001/sse')  
# agent = Agent('openai:gpt-4o-mini', toolsets=[server], output_type=OutputText)  


# async def main():
#     async with agent:
#         result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
#     print(result.output)

if __name__ == '__main__':
    asyncio.run(main()) 