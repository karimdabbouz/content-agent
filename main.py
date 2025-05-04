from summarizer import SummarizerAgent
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env')


if __name__ == '__main__':
    agent = SummarizerAgent(
        server_urls=['http://localhost:11434'],
        model_name='openai:gpt-4o-mini',
        system_prompt='You are a helpful assistant that summarizes text.'
    )

    print(agent)