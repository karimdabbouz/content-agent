from summarizer import SummarizerAgent
from schemas import InputText
import argparse, json



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize text')
    parser.add_argument('action', choices=['summarize'], help='Action to perform')
    parser.add_argument('--model-name', default='openai:gpt-4o-mini', help='Model name')
    parser.add_argument('--system-prompt', required=True, help='System prompt')
    parser.add_argument('--input-file', required=True, help='Input file. For format: See schemas.')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as file:
        input_data = [InputText.model_validate(x) for x in json.load(file)]
    
    if args.action == 'summarize':
        agent = SummarizerAgent(
            server_urls=['http://localhost:11434'],
            model_name=args.model_name,
            system_prompt=args.system_prompt
        )
        agent.run(input_data)