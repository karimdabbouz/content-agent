from summarizer import SummarizerAgent
from schemas import InputText, MCPServerConfigs
import argparse, json, os



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize text')
    parser.add_argument('action', choices=['summarize'], help='Action to perform')
    parser.add_argument('--model-name', default='openai:gpt-4o-mini', help='Model name')
    parser.add_argument('--system-prompt', required=True, help='System prompt')
    args = parser.parse_args()
    
    if args.action == 'summarize':
        print('To exit, enter "exit"')
        while True:
            file_path = input('Enter the path to the input file. It should be a JSON with a list of InputText objects: ')
            if file_path == 'exit':
                break
            elif not os.path.exists(file_path):
                print('File does not exist. Please try again.')
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    input_data = [InputText.model_validate(x) for x in json.load(file)]
                # agent = SummarizerAgent(
                #     server_configs=MCPServerConfigs(
                #         transport='http',
                #         server_urls=['http://localhost:11434']
                #     ),
                #     model_name=args.model_name,
                #     system_prompt=args.system_prompt
                # )
                agent = SummarizerAgent(
                    server_configs=MCPServerConfigs(
                        transport='stdio',
                        stdio_commands=[
                            ('python', ['-m', 'pydantic_ai.mcp.run', 'stdio', 'http://localhost:11434'])
                        ]
                    ),
                    model_name=args.model_name,
                    system_prompt=args.system_prompt
                )
                print(agent.agent)
                # agent.run(input_data)