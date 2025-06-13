from fastapi import FastAPI
from schemas import MCPServerConfig, SummarizeRequest
app = FastAPI()


@app.get('/')
def read_root():
    return {'message': 'Summarizer Agent API'}


@app.get('/summarize')
def summarize(request: SummarizeRequest):
    # assumes that agent with given system prompt and optional tools is already running
    return {'message': 'hello from summarize endpoint'}