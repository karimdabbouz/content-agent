import os
import json
from dotenv import load_dotenv
import httpx
import sseclient

load_dotenv()
FIRECRAWL_API_KEY = os.getenv('FIRECRAWL_API_KEY')
if not FIRECRAWL_API_KEY:
    raise ValueError('FIRECRAWL_API_KEY not found in .env')

FIRECRAWL_URL = f'https://mcp.firecrawl.dev/{FIRECRAWL_API_KEY}/sse'

# Minimal JSON-RPC request for firecrawl_search tool
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
    # Open SSE connection and send the request
    with httpx.Client() as client:
        # Initiate the SSE stream
        with client.stream("POST", FIRECRAWL_URL, json=payload, headers=headers, timeout=60) as response:
            client_sse = sseclient.SSEClient(response)
            print(f"Status code: {response.status_code}")
            print("SSE Events:")
            for event in client_sse.events():
                print(f"event: {event.event}")
                print(f"data: {event.data}") 