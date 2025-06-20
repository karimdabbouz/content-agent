from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from typing import List, Optional
from schemas import Outline, MCPServerConfig
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(dotenv_path=Path(__file__).parent / '.env')


class OutlineAgent():
    '''
    An agent that takes a list of one or more InputText objects and returns an outline for repurposed content.
    '''
    def __init__(
        self,
        server_configs: Optional[List[MCPServerConfig]],
        model_name: str,
        system_prompt: str
    ):
        if server_configs is not None:
            self.agent = Agent(
                model_name,
                mcp_servers=lambda: [MCPServerHTTP(x.connection) if x.transport == 'http' else MCPServerStdio(x.connection[0], x.connection[1]) for x in server_configs],
                system_prompt=system_prompt,
                output_type=Outline
            )
        else:
            self.agent = Agent(
                model_name,
                system_prompt=system_prompt,
                output_type=Outline
            )


    