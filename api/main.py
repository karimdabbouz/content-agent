from fastapi import FastAPI
from schemas import (
    MCPServerConfig, InputText, Outline, OutputText, FullUserPromptInputTexts, FullUserPromptOutline,
    FromFileRequest, FromFileWithOutlineRequest, CreateOutlineOnlyRequest, FromWebRequest
)

app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Summarizer Agent API'}

@app.post('/from-file')
def from_file(request: FromFileRequest):
    return {
        'message': 'from-file endpoint called',
        'input_texts': [x.model_dump() for x in request.input_texts],
        'user_prompt': request.user_prompt,
        'model_name': request.model_name,
        'mcp_servers': request.mcp_servers
    }

@app.post('/from-file-with-outline')
def from_file_with_outline(request: FromFileWithOutlineRequest):
    return {
        'message': 'from-file-with-outline endpoint called',
        'input_texts': [x.model_dump() for x in request.input_texts],
        'outline_prompt': request.outline_prompt,
        'content_prompt': request.content_prompt,
        'model_name': request.model_name,
        'mcp_servers': request.mcp_servers
    }

@app.post('/create-outline-only')
def create_outline_only(request: CreateOutlineOnlyRequest):
    return {
        'message': 'create-outline-only endpoint called',
        'input_texts': [x.model_dump() for x in request.input_texts],
        'user_prompt': request.user_prompt,
        'model_name': request.model_name,
        'mcp_servers': request.mcp_servers
    }

@app.post('/from-web')
def from_web(request: FromWebRequest):
    return {
        'message': 'from-web endpoint called',
        'search_terms': request.search_terms,
        'user_prompt': request.user_prompt,
        'model_name': request.model_name,
        'mcp_servers': request.mcp_servers
    }