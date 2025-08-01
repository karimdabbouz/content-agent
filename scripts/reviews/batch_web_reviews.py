import os, sys, json, time, logfire
from pathlib import Path
from typing import List

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
Your job is to do a web search for product reviews by independent sources. It is your responsibility to assess whether a source is independent or not. You will then get the content of this product review and return it in the structured format specified below.

## 1. GENERAL RULES
- Always use the Firecrawl MCP server and its tools to do a web search matching the user request.
- For the output texts always use the language specified in the user prompt even if the product review is in a different language. If the review is in a different language, translate it into the language requested by the user.

## 2. FORMATS
- You will receive input in the form of a simple string written by the user specifying the maximum number of search results to retrieve and the product to search for as well as other important information.
- You must always deliver output in the following format:
{output_text_schema}
'''

load_dotenv()
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')
FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

MCP_CONFIGS = [
    MCPServerConfig(
        transport='stdio',
        connection=('npx', ['-y', 'firecrawl-mcp']),
        env={'FIRECRAWL_API_KEY': FIRECRAWL_API_KEY}
    )
]

async def process_product(product_title, agent):
    prompt = f'Suche online nach Reviews oder Erfahrungsberichten zu folgendem Produkt: {product_title}. Wähle genau 3 Reviews aus und stelle sicher, dass es sich um unabhängige Reviews handelt und nicht um Produktbeschreibungen von Händlern oder vom Hersteller. Formatiere die Reviews im angegebenen Format.'
    try:
        result = await agent.run(prompt)
        reviews = result.output
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
        output_type=List[InputText]
    )

    # Process each product sequentially
    for idx, product in enumerate(products, 1):
        print(f'Processing {idx}/{len(products)}: {product}')
        await process_product(product, agent)
        time.sleep(60)

if __name__ == '__main__':
    asyncio.run(main()) 