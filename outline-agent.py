from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from typing import List, Optional
from schemas import InputText, MCPServerConfig
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
        pass