from summarizer import SummarizerAgent
from schemas import InputText, MCPServerConfig, OutputText
import argparse, json, os, datetime
from system_prompts import summarize_system_prompt


def write_to_markdown(output: OutputText):
    '''
    Only used in cli at this moment.
    Takes the OutputText object and writes it to an markdown file in the output directory.
    '''
    output_file = f'./outputs/{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.md'
    lines = []
    if output.headline:
        lines.append(f'# {output.headline}\n')
    if output.teaser:
        lines.append(f'*{output.teaser}*\n')
    for paragraph in output.body:
        if paragraph.subheadline:
            lines.append(f'## {paragraph.subheadline}\n')
        lines.append(f'{paragraph.text}\n')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['summarize'], help='Action to perform')
    parser.add_argument('--model-name', default='openai:gpt-4o-mini', help='Model name') # in the webserver this will be set at startup
    parser.add_argument('--mcp-servers', help='MCP servers as a list')
    parser.add_argument('--write-to-file', default=False, help='True if you want to write the output to a file')
    args = parser.parse_args()

    if args.action == 'summarize':
        # --mcp-servers '{"transport": "http", "server_urls": ["http://localhost:8000"]}'
        # --mcp-servers '{"transport": "stdio", "stdio_commands": [["/usr/bin/mycmd", ["--arg1", "foo"]]]}'
        if args.mcp_servers:
            mcp_configs = MCPServerConfig(**json.loads(args.mcp_configs))
            agent = SummarizerAgent(
                server_configs=mcp_configs,
                model_name=args.model_name,
                system_prompt=summarize_system_prompt
            )
        else:
            agent = SummarizerAgent(
                server_configs=None,
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
                if args.write_to_file:
                    write_to_markdown(response.output)
                else:
                    print(response.output)
