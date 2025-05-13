from summarizer import SummarizerAgent
from schemas import InputText
from dotenv import load_dotenv
import argparse, json

load_dotenv(dotenv_path='.env')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Summarize text')
    parser.add_argument('action', choices=['summarize'], help='Action to perform')
    parser.add_argument('model_name', default='openai:gpt-4o-mini', help='Model name')
    parser.add_argument('system_prompt', help='System prompt')
    parser.add_argument('input_file', help='Input file. For format: See schemas.')
    args = parser.parse_args()

    with open(args.input_file, 'r', encoding='utf-8') as file:
        input_data = json.load(file)
        input_data = InputText.model_validate(input_data)
        print(input_data)
    
    if args.action == 'summarize':
        print(f'summarize: {args}')
        # agent = SummarizerAgent(
        #     server_urls=['http://localhost:11434'],
        #     model_name='openai:gpt-4o-mini',
        #     system_prompt='You are a helpful assistant that summarizes text.'
        # )