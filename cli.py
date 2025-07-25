from writer_agent import WriterAgent
from outline_agent import OutlineAgent
from schemas import MCPServerConfig, OutputText, Outline
import argparse, json, os, datetime, asyncio
from system_prompts import from_file_system_prompt, from_file_with_outline_system_prompt, outline_system_prompt, from_web_system_prompt
from input_parser import InputParser
from typing import Union


def write_to_markdown(output: Union[OutputText, Outline]):
    '''
    Only used in cli at this moment.
    Takes the OutputText object and writes it to an markdown file in the output directory.
    '''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(script_dir, 'outputs')
    os.makedirs(outputs_dir, exist_ok=True)
    output_file = os.path.join(outputs_dir, f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.md')
    lines = []
    if isinstance(output, OutputText):
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
    elif isinstance(output, Outline):
        for paragraph in output.paragraphs:
            if paragraph.subheadline:
                lines.append(f'## {paragraph.subheadline}\n')
            lines.append(f'{paragraph.text}\n')
        with open(output_file, 'w', encoding='utf-8') as file:
            file.writelines(lines)

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-name', default='openai:gpt-4o-mini', help='Model name. Default is 4o-mini')
    parser.add_argument('--write-to-file', action='store_true', help='Write outputs to md files. If not set, output will be printed to console.')
    parser.add_argument('--mcp-servers', default=None, help='A list of mcp server configurations (see docs)')
    
    subparsers = parser.add_subparsers(dest='action', required=True)

    # from-file
    from_file_parser = subparsers.add_parser('from-file', help='Work with text from one or more files')
    from_file_parser.add_argument('--file-path', required=True, help='Path to the input file or directory')
    from_file_parser.add_argument('--with-outline', action='store_true', help='Create an outline first, then generate content from the outline')

    # create-outline-only
    create_outline_only_parser = subparsers.add_parser('create-outline-only', help='Create an outline from input texts without writing the actual content')
    create_outline_only_parser.add_argument('--file-path', required=True, help='Path to the input file or directory')

    # from-web
    from_web_parser = subparsers.add_parser('from-web', help='Work with text gathered from a web search')
    from_web_parser.add_argument('--with-outline', action='store_true', help='Create an outline first, then generate content from the outline (dummy for now)')

    args = parser.parse_args()

    if args.action == 'from-file':
        input_parser = InputParser()
        input_data = input_parser.parse(args.file_path)
        if args.mcp_servers:
            servers_list = json.loads(args.mcp_servers)
            mcp_configs = [MCPServerConfig(**server) for server in servers_list]
        else:
            mcp_configs = None
        if args.with_outline:
            # Outline + writer workflow
            outline_agent = OutlineAgent(
                server_configs=mcp_configs,
                model_name=args.model_name,
                system_prompt=outline_system_prompt
            )
            writer_agent = WriterAgent(
                server_configs=mcp_configs,
                model_name=args.model_name,
                system_prompt=from_file_with_outline_system_prompt
            )
            while True:
                user_prompt_outline = input('How would you like me to create the outline? ')
                if user_prompt_outline.strip().lower() == 'exit':
                    break
                user_prompt_outline_full = outline_agent._construct_user_prompt(input_data, user_prompt_outline)
                response_outline = await outline_agent.run(user_prompt_outline_full)
                user_prompt_writer = input('How would you like me to write the content? ')
                if user_prompt_writer.strip().lower() == 'exit':
                    break
                user_prompt_writer_full = writer_agent._construct_user_prompt_from_outline(response_outline.output, user_prompt_writer)
                response_from_writer = await writer_agent.run(user_prompt_writer_full)
                if args.write_to_file:
                    write_to_markdown(response_from_writer.output)
                else:
                    print(response_from_writer.output)
        else:
            # Writer only workflow
            agent = WriterAgent(
                server_configs=mcp_configs,
                model_name=args.model_name,
                system_prompt=from_file_system_prompt
            )
            while True:
                user_prompt = input('What would you like me to do? ')
                if user_prompt.strip().lower() == 'exit':
                    break
                user_prompt_full = agent._construct_user_prompt_from_input_texts(input_data, user_prompt)
                response = await agent.run(user_prompt_full)
                if args.write_to_file:
                    write_to_markdown(response.output)
                else:
                    print(response.output)
    elif args.action == 'from-web':
        if not args.mcp_servers:
            raise ValueError('A connection to the Firecrawl MCP server is required for from-web')
        else:
            servers_list = json.loads(args.mcp_servers)
            mcp_configs = [MCPServerConfig(**server) for server in servers_list]
        if args.with_outline:
            print('from-web with --with-outline is not yet implemented. This is a placeholder.')
            # Placeholder for future implementation
        else:
            agent = WriterAgent(
                server_configs=mcp_configs,
                model_name=args.model_name,
                system_prompt=from_web_system_prompt
            )
            while True:
                user_prompt = input('What would you like me to do? ')
                if user_prompt.strip().lower() == 'exit':
                    break
                response = await agent.run(user_prompt)
                if args.write_to_file:
                    write_to_markdown(response.output)
                else:
                    print(response.output)
    elif args.action == 'create-outline-only':
        input_parser = InputParser()
        input_data = input_parser.parse(args.file_path)
        if args.mcp_servers:
            servers_list = json.loads(args.mcp_servers)
            mcp_configs = [MCPServerConfig(**server) for server in servers_list]
        else:
            mcp_configs = None
        agent = OutlineAgent(
            server_configs=mcp_configs,
            model_name=args.model_name,
            system_prompt=outline_system_prompt
        )
        while True:
            user_prompt = input('What would you like me to do? ')
            if user_prompt.strip().lower() == 'exit':
                break
            user_prompt_full = agent._construct_user_prompt(input_data, user_prompt)
            response = await agent.run(user_prompt_full)
            if args.write_to_file:
                write_to_markdown(response.output)
            else:
                print(response.output)

if __name__ == '__main__':
    asyncio.run(main())