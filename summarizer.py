from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP, MCPServerStdio
from typing import List
from schemas import InputText, OutputText, MCPServerConfigs
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv(dotenv_path=Path(__file__).parent / '.env')


class SummarizerAgent():
    '''
    The main agent implemented as an MCP client. Uses PydanticAI.
    '''
    def __init__(
        self,
        server_configs: MCPServerConfigs,
        model_name: str,
        input_text_schema: str = json.dumps(InputText.model_json_schema(), indent=2),
        output_text_schema: str = json.dumps(OutputText.model_json_schema(), indent=2)
        ):
        self.system_prompt = '''Your job is to repurpose text into a new text depending on the user's request and a list of one or more input texts. Here are the rules:

        1. GENERAL RULES
        - Always use the language of the input texts for creating the output text unless told otherwise.
        - 

        2. FORMATS
        - You will receive input as a list of InputText objects in the following format:
        {input_text_schema}
        - OUTPUT TYPE IS SET AS AN ARGUMENT IN THE AGENT BY PYDANTIC
        '''
        self.agent = Agent(
            model_name,
            mcp_servers=lambda: [MCPServerHTTP(x) for x in server_configs.server_urls] if server_configs.transport == 'http' else [MCPServerStdio(x[0], x[1]) for x in server_configs.stdio_commands],
            system_prompt=self.system_prompt
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
        inputs_json = json.dumps(InputText.model_json_schema(), indent=2)
        user_prompt = {
            'user_prompt': user_prompt
        }


    def run(self, input_texts: List[InputText]) -> OutputText:
        '''
        Runs the agent with a list of input texts. Returns the summarized text.

        Args:
            - input_texts: A list of InputText objects
        '''
        test_input = 'Who are you in one sentence?'
        print(self.agent.run(test_input))