from writer_agent import WriterAgent
from schemas import InputText, MCPServerConfig, OutputText
import argparse, json, os, datetime
from system_prompts import from_file_system_prompt
from input_parser import InputParser


def write_to_markdown(output: OutputText):
    '''
    Only used in cli at this moment.
    Takes the OutputText object and writes it to an markdown file in the output directory.
    '''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    
    output_file = os.path.join(outputs_dir, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.md')
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
    parser.add_argument('--model-name', default='openai:gpt-4o-mini', help='Model name. Default is 4o-mini')
    parser.add_argument('--write-to-file', action='store_true', help='Write outputs to md files. If not set, output will be printed to console.')
    parser.add_argument('--mcp-servers', default=None, help='A list of mcp server configurations (see docs)')
    
    subparsers = parser.add_subparsers(dest='action', required=True)

    # from-file
    from_file_parser = subparsers.add_parser('from-file', help='Work with text from one or more files')
    from_file_parser.add_argument('--file-path', required=True, help='Path to the input file or directory')

    # from-web
    from_web_parser = subparsers.add_parser('from-web', help='Work with text gathered from a web search')

    args = parser.parse_args()

    if args.action == 'from-file':
        # --mcp-servers '{"transport": "http", "server_urls": ["http://localhost:8000"]}'
        # --mcp-servers '[{"transport": "http", "connection": "http://localhost:8000"}, {"transport": "stdio", "connection": ["/usr/bin/firecrawl", ["--arg1", "foo"]]}]'
        # --mcp-servers '{"transport": "stdio", "stdio_commands": [["/usr/bin/mycmd", ["--arg1", "foo"]]]}'
        input_parser = InputParser()
        input_data = input_parser.parse(args.file_path)
        if args.mcp_servers:
            servers_list = json.loads(args.mcp_servers)
            mcp_configs = [MCPServerConfig(**server) for server in servers_list]
            agent = WriterAgent(
                server_configs=mcp_configs,
                model_name=args.model_name,
                system_prompt=from_file_system_prompt
            )
        else:
            agent = WriterAgent(
                server_configs=None,
                model_name=args.model_name,
                system_prompt=from_file_system_prompt
            )
        while True:
            user_prompt = input('What would you like me to do? ')
            if user_prompt.strip().lower() == 'exit':
                break
            user_prompt_full = agent._construct_prompt(input_data, user_prompt)
            response = agent.run(user_prompt_full)
            if args.write_to_file:
                write_to_markdown(response.output)
            else:
                print(response.output)
    elif args.action == 'from-web':
        pass