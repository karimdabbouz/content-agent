from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from typing import List, Optional
from schemas import Outline, MCPServerConfig, FullUserPrompt, InputText
from dotenv import load_dotenv
from pathlib import Path
import json
from system_prompts import outline_system_prompt


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
    

    def get_system_prompt(self):
        '''
        Returns the current system prompt.
        '''
        return self.agent.system_prompt
    

    def _construct_user_prompt(self, input_texts: List[InputText], user_prompt: str) -> FullUserPrompt:
        '''
        Combines an individual user prompt with a list of input texts to pass in as a user prompt to the LLM.
        '''
        return FullUserPrompt(
            user_prompt=user_prompt,
            input_texts=[x.model_dump() for x in input_texts]
        )
    

    def run(self, full_user_prompt: FullUserPrompt)-> Outline:
        '''
        Runs the agent with a list of input texts. Returns the outline.
        '''
        return self.agent.run_sync(json.dumps(full_user_prompt.model_dump(), indent=2, default=str))