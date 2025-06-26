from fastapi import FastAPI
from schemas import (
    InputText, Outline, OutputText, FullUserPromptInputTexts, FullUserPromptOutline,
    FromFileRequest, FromFileWithOutlineRequest, CreateOutlineOnlyRequest, FromWebRequest
)
from writer_agent import WriterAgent
from outline_agent import OutlineAgent
from system_prompts import from_file_system_prompt, from_file_with_outline_system_prompt, outline_system_prompt
from typing import List

# Fixed configuration for all agents
MODEL_NAME = 'openai:gpt-4o-mini'
MCP_SERVERS = None  # or provide a list of MCPServerConfig if you want to use MCP servers

app = FastAPI()

# Create agents on startup with fixed config
writer_agent = WriterAgent(
    server_configs=MCP_SERVERS,
    model_name=MODEL_NAME,
    system_prompt=from_file_system_prompt
)
outline_agent = OutlineAgent(
    server_configs=MCP_SERVERS,
    model_name=MODEL_NAME,
    system_prompt=outline_system_prompt
)
writer_agent_with_outline = WriterAgent(
    server_configs=MCP_SERVERS,
    model_name=MODEL_NAME,
    system_prompt=from_file_with_outline_system_prompt
)

@app.get('/')
def read_root():
    return {'message': 'Summarizer Agent API'}

@app.post('/from-file')
def from_file(request: FromFileRequest):
    # Placeholder: use writer_agent
    return {
        'message': 'from-file endpoint called',
        'input_texts': [x.model_dump() for x in request.input_texts],
        'user_prompt': request.user_prompt
    }

@app.post('/from-file-with-outline')
def from_file_with_outline(request: FromFileWithOutlineRequest):
    # Placeholder: use outline_agent and writer_agent_with_outline
    return {
        'message': 'from-file-with-outline endpoint called',
        'input_texts': [x.model_dump() for x in request.input_texts],
        'outline_prompt': request.outline_prompt,
        'content_prompt': request.content_prompt
    }

@app.post('/create-outline-only')
def create_outline_only(request: CreateOutlineOnlyRequest):
    # Placeholder: use outline_agent
    return {
        'message': 'create-outline-only endpoint called',
        'input_texts': [x.model_dump() for x in request.input_texts],
        'user_prompt': request.user_prompt
    }

@app.post('/from-web')
def from_web(request: FromWebRequest):
    # Placeholder for future web agent
    return {
        'message': 'from-web endpoint called',
        'search_terms': request.search_terms,
        'user_prompt': request.user_prompt
    }