import json
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
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
        system_prompt: str
    ):
        if server_configs is not None:
            self.agent = Agent(
                model_name,
                mcp_servers=lambda: [MCPServerHTTP(x.connection) if x.transport == 'http' else MCPServerStdio(x.connection[0], x.connection[1]) for x in server_configs],
                system_prompt=system_prompt,
                output_type=OutputText
            )
        else:
            self.agent = Agent(
                model_name,
                system_prompt=system_prompt,
                output_type=OutputText
            )


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


    def run(self, full_user_prompt: Union[FullUserPromptInputTexts, FullUserPromptOutline]) -> OutputText:
        '''
        Runs the agent with either input texts or an outline. Returns the summarized text.
        '''
        return self.agent.run_sync(json.dumps(full_user_prompt.model_dump(), indent=2, default=str))