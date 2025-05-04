from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from typing import List


class SummarizerAgent():
    '''
    The main agent implemented as an MCP client. Uses PydanticAI.
    '''
    def __init__(
        self,
        server_urls: List[str],
        model_name: str,
        system_prompt: str
        ):
        self.servers = [MCPServerHTTP(x) for x in server_urls]
        self.agent = Agent(
            model_name,
            mcp_servers=self.servers,
            system_prompt=system_prompt
        )