import json
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from typing import List
from schemas import InputText, OutputText, MCPServerConfigs
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / '.env')


class SummarizerAgent():
    '''
    The main agent implemented as an MCP client. Uses PydanticAI.
    '''
    def __init__(
        self,
        server_configs: MCPServerConfigs,
        model_name: str,
        system_prompt: str
        ):
        self.agent = Agent(
            model_name,
            # mcp_servers=lambda: [MCPServerHTTP(x) for x in server_configs.server_urls] if server_configs.transport == 'http' else [MCPServerStdio(x[0], x[1]) for x in server_configs.stdio_commands],
            system_prompt=system_prompt,
            output_type=OutputText
        )


    def get_system_prompt(self):
        '''
        Returns the current system prompt.
        '''
        return self.system_prompt

    
    def _construct_prompt(self, input_texts: List[InputText], user_prompt: str):
        '''
        hier muss der wahrscheinlich die InputText und den User-Prompt zusammenfügen?
        Nimmt mir PydanticAI hier nicht Dinge ab eigentlich?
            -> nur system-prompt/instructions und output-type
        '''
        user_prompt = {
            'user_prompt': user_prompt,
            'input_texts': [x.model_dump() for x in input_texts]
        }
        return json.dumps(user_prompt, indent=2, default=str)


    def run(self, user_prompt: str): # add output type later
        '''
        Runs the agent with a list of input texts. Returns the summarized text.

        Args:
            - user_prompt: The user prompt (instructions plus input texts)
        '''
        return self.agent.run_sync(user_prompt)