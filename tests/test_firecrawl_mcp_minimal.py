import os
import json
from dotenv import load_dotenv
import httpx

load_dotenv()
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')

FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tool_call",
    "params": {
        "tool": "firecrawl_search",
        "args": {
            "query": "lego 10265 ford mustang Review Erfahrungsbericht",
            "limit": 1,
            "lang": "de",
            "scrapeOptions": {
                "formats": ["markdown"],
                "onlyMainContent": True
            }
        }
    }
}

headers = {"Content-Type": "application/json"}

if __name__ == "__main__":
    with httpx.Client() as client:
        with client.stream("POST", FIRECRAWL_URL, json=payload, headers=headers, timeout=60) as response:
            print(f"Status code: {response.status_code}")
            print("Raw SSE stream:")
            for line in response.iter_lines():
                if line:
                    print(line.decode()) 