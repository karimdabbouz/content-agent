from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from typing import List
from schemas import InputText, OutputText


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

    
    def run(self, input_texts: List[InputText]) -> OutputText:
        '''
        Runs the agent with a list of input texts. Returns the summarized text.

        Args:
            - input_texts: A list of InputText objects
        '''
        pass