from summarizer import SummarizerAgent
from schemas import InputText, MCPServerConfigs
import argparse, json, os
from system_prompts import summarize_system_prompt


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['summarize'], help='Action to perform')
    parser.add_argument('--model-name', default='openai:gpt-4o-mini', help='Model name') # in the webserver this will be set at startup
    parser.add_argument('--mcp-servers', help='MCP servers as a list')
    args = parser.parse_args()

    if args.action == 'summarize':
        mcp_configs = MCPServerConfigs(**json.loads(args.mcp_servers))
        # --mcp-servers '{"transport": "http", "server_urls": ["http://localhost:8000"]}'
        # --mcp-servers '{"transport": "stdio", "stdio_commands": [["/usr/bin/mycmd", ["--arg1", "foo"]]]}'
        agent = SummarizerAgent(
            server_configs=mcp_configs,
            model_name=args.model_name,
            system_prompt=summarize_system_prompt
        )
        while True:
            file_path = input('Enter the path to the input file. It should be a JSON with a list of InputText objects: ')
            if file_path == 'exit':
                break
            elif not os.path.exists(file_path):
                print('File does not exist. Please try again.')
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    input_data = [InputText.model_validate(x) for x in json.load(file)]
                user_prompt = input('What would you like me to do? ')
                user_prompt = agent._construct_prompt(input_data, user_prompt)
                response = agent.run(user_prompt)
                print(response)
                print(response.all_messages())