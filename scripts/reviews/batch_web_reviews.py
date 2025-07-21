import os, sys, json, time, logfire
from pathlib import Path
from typing import List
import logging

# logging.basicConfig(level=logging.DEBUG)

# Add content-agent/ to sys.path
project_root = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(project_root)

import asyncio
from dotenv import load_dotenv
from writer_agent import WriterAgent
from schemas import MCPServerConfig, InputText, OutputText

load_dotenv()

LOGFIRE_TOKEN = os.getenv('LOGFIRE_TOKEN')
logfire.configure(token=LOGFIRE_TOKEN)
logfire.instrument_pydantic_ai()
logfire.instrument_httpx(capture_all=True)

output_text_schema = json.dumps({
    "type": "array",
    "items": OutputText.model_json_schema()
}, indent=2)

# Always resolve input/output paths relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
INPUT_FILE = SCRIPT_DIR / 'product_titles.txt'  # One product title per line
OUTPUTS_DIR = SCRIPT_DIR / 'outputs'  # Output directory for review files

# Custom system prompt for review extraction
system_prompt = f'''
Your job is to do a web search with firecrawl, visit a given number of search results, scrape the content and parse it into the specified output format.

## 1. GENERAL RULES
- Always use the Firecrawl MCP server and its tools to do a web search matching the user request.
- For the output texts always use the language specified in the user prompt even if the web search results are in a different language. If the content is in a different language, translate it.

## 2. FORMATS
- You will receive input in the form of a simple string written by the user specifying the maximum number of search results to retrieve and the subject to search for as well as other important information.
'''
# - You must always deliver output in the following format:
# {output_text_schema}

load_dotenv()
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')
FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

MCP_CONFIGS = [
    MCPServerConfig(transport='http', connection=FIRECRAWL_URL)
]

async def process_product(product_title, agent):
    # prompt = f'Suche online nach maximal 3 Reviews zu folgendem Produkt: {product_title}. Lies jedes Review, übersetze den Inhalt auf Deutsch und formatiere ihn im angegebenen Format.'
    # prompt = f'Suche online nach maximal 3 deutschsprachigen Reviews oder Erfahrungsberichten zu folgendem Produkt: {product_title}. Stelle sicher, dass es sich um unabhängige Reviews handelt und nicht um Produktbeschreibungen von Händlern oder vom Hersteller. Besuche die Reviews und scrape den Inhalt. Formatiere ihn anschließend im angegebenen Format.'
    prompt = f'Suche online nach maximal 3 deutschsprachigen Reviews oder Erfahrungsberichten zu folgendem Produkt: {product_title}. Stelle sicher, dass es sich um unabhängige Reviews handelt und nicht um Produktbeschreibungen von Händlern oder vom Hersteller. Besuche die Reviews, scrape den Inhalt und fasse ihn für mich zusammen.'
    try:


# server = MCPServerSSE(url=FIRECRAWL_URL)
# print(server)
# agent = Agent('openai:gpt-4o-mini', mcp_servers=[server], output_type=OutputText)

# async def main():
#     async with agent.run_mcp_servers():
#         result = await agent.run('do a web search for product reviews on the lego set with number 10329 named tiny plants. visit exactly 3 reviews, read them and use the information to write a new review.')
#     print(result.output)

# if __name__ == '__main__':
#     asyncio.run(main()) 

        result = await agent.run(prompt)
        reviews = result.output  # Should be a list of InputText
        safe_title = product_title.replace(' ', '_').replace('/', '_')
        product_dir = OUTPUTS_DIR / safe_title
        os.makedirs(product_dir, exist_ok=True)
        for i, review in enumerate(reviews, 1):
            output_path = product_dir / f'review_{i}.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(review.model_dump_json(indent=2))
        print(f'[OK] {product_title}: {len(reviews)} reviews saved to {product_dir}')
    except Exception as e:
        print(f'[ERROR] {product_title}: {e}')

async def main():
    # Read product titles
    if not INPUT_FILE.exists():
        print(f'Input file {INPUT_FILE} not found.')
        return
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        products = [line.strip() for line in f if line.strip()]
    print(f'Loaded {len(products)} product titles.')

    # Set up the agent to output List[InputText] objects
    agent = WriterAgent(
        server_configs=MCP_CONFIGS,
        model_name='openai:gpt-4o-mini',
        system_prompt=system_prompt,
        output_type=None
        # output_type=List[InputText]
    )

    # Process each product sequentially
    for idx, product in enumerate(products, 1):
        print(f'Processing {idx}/{len(products)}: {product}')
        await process_product(product, agent)
        time.sleep(60)

if __name__ == '__main__':
    asyncio.run(main()) 