from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio, MCPServerSSE
from typing import List, Optional
from schemas import Outline, MCPServerConfig, FullUserPromptInputTexts, InputText
from dotenv import load_dotenv
from pathlib import Path
import json


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
            mcp_servers = self._build_mcp_servers(server_configs)
            self.agent = Agent(
                model_name,
                mcp_servers=mcp_servers,
                system_prompt=system_prompt,
                output_type=Outline
            )
        else:
            self.agent = Agent(
                model_name,
                system_prompt=system_prompt,
                output_type=Outline
            )


    def _build_mcp_servers(self, server_configs: List[MCPServerConfig]):
        '''
        Builds MCP servers from a list of server configurations.
        '''
        return [MCPServerHTTP(x.connection) if x.transport == 'http' else MCPServerStdio(x.connection[0], x.connection[1]) if x.transport == 'stdio' else MCPServerSSE(url=x.connection) for x in server_configs]
    

    def get_system_prompt(self):
        '''
        Returns the current system prompt.
        '''
        return self.agent.system_prompt
    

    def _construct_user_prompt(self, input_texts: List[InputText], user_prompt: str) -> FullUserPromptInputTexts:
        '''
        Combines an individual user prompt with a list of input texts to pass in as a user prompt to the LLM.
        '''
        return FullUserPromptInputTexts(
            user_prompt=user_prompt,
            input_texts=[x.model_dump() for x in input_texts]
        )
    

    async def run(self, full_user_prompt: FullUserPromptInputTexts) -> AgentRunResult:
        '''
        Runs the agent with a list of input texts. Returns the outline (async).
        '''
        return await self.agent.run(json.dumps(full_user_prompt.model_dump(), indent=2, default=str))