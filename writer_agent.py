import json
from pydantic_ai import Agent
from pydantic_ai.agent import AgentRunResult
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio, MCPServerSSE
from pydantic import BaseModel
from typing import List, Optional, Union
from schemas import InputText, OutputText, MCPServerConfig, FullUserPromptInputTexts, FullUserPromptOutline, Outline
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(dotenv_path=Path(__file__).parent / '.env')


class WriterAgent():
    '''
    The main agent implemented as an MCP client. Uses PydanticAI.
    '''
    def __init__(
        self,
        server_configs: Optional[List[MCPServerConfig]],
        model_name: str,
        system_prompt: str,
        output_type: type = OutputText
    ):
        self.server_configs = server_configs
        self.output_type = output_type
        if server_configs is not None:
            mcp_servers = self._build_mcp_servers(server_configs)
            self.agent = Agent(
                model_name,
                mcp_servers=mcp_servers,
                system_prompt=system_prompt,
                output_type=output_type
            )
        else:
            self.agent = Agent(
                model_name,
                system_prompt=system_prompt,
                output_type=output_type
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
        return self.system_prompt

    
    def _construct_user_prompt_from_input_texts(self, input_texts: List[InputText], user_prompt: str) -> FullUserPromptInputTexts:
        '''
        Combines an individual user prompt with a list of input texts to pass in as a user prompt to the LLM.
        '''
        return FullUserPromptInputTexts(
            user_prompt=user_prompt,
            input_texts=[x.model_dump() for x in input_texts]
        )


    def _construct_user_prompt_from_outline(self, outline: Outline, user_prompt: str) -> FullUserPromptOutline:
        '''
        Combines an individual user prompt with an outline to pass in as a user prompt to the LLM.
        '''
        return FullUserPromptOutline(
            user_prompt=user_prompt,
            outline=outline
        )


    async def run(self, full_user_prompt: Union[FullUserPromptInputTexts, FullUserPromptOutline, str]) -> AgentRunResult:
        '''
        Runs the agent with either input texts, an outline or a web search request (async).
        '''
        if self.server_configs:
            async with self.agent.run_mcp_servers():
                return await self.agent.run(full_user_prompt)
        else:
            if isinstance(full_user_prompt, str):
                return await self.agent.run(full_user_prompt)
            else:
                return await self.agent.run(json.dumps(full_user_prompt.model_dump(), indent=2, default=str))