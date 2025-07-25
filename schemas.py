from pydantic import BaseModel, model_validator
from typing import Optional, List, Tuple, Literal, Union
import datetime


class MCPServerConfig(BaseModel):
    '''
    Configurations for MCP servers with either HTTP, Stdio or SSE transport.
    '''
    transport: Literal['stdio', 'http', 'sse']
    connection: Union[Tuple[str, List[str]], str]
    env: Optional[dict] = None

    @model_validator(mode='after')
    def check_connection_type(self):
        if self.transport == 'http':
            if not isinstance(self.connection, str):
                raise ValueError('For http transport, connection must be a string (server URL)')
        elif self.transport == 'stdio':
            if not (isinstance(self.connection, tuple) and
                    len(self.connection) == 2 and
                    isinstance(self.connection[0], str) and
                    isinstance(self.connection[1], list)):
                raise ValueError('For stdio transport, connection must be a tuple (str, list[str])')
        elif self.transport == 'sse':
            if not isinstance(self.connection, str):
                raise ValueError('For sse transport, connection must be a string (server URL)')
        return self


class InputTextMetadata(BaseModel):
    created_at: Optional[datetime.datetime] = None
    num_words: Optional[int] = None
    source: Optional[str] = None


class Paragraph(BaseModel):
    subheadline: Optional[str] = None
    text: str


class Outline(BaseModel):
    paragraphs: List[Paragraph]


class InputText(BaseModel):
    metadata: InputTextMetadata
    headline: Optional[str] = None
    teaser: Optional[str] = None
    body: List[Paragraph]


class OutputText(BaseModel):
    headline: Optional[str] = None
    teaser: Optional[str] = None
    body: List[Paragraph]


class FullUserPromptInputTexts(BaseModel):
    input_texts: List[InputText]
    user_prompt: str


class FullUserPromptOutline(BaseModel):
    outline: Outline
    user_prompt: str


# API request schemas | Important: they will most likely be extended in the future so no duplicates of FullUserPrompt types

class FromFileRequest(BaseModel):
    input_texts: List[InputText]
    user_prompt: str


class FromFileWithOutlineRequest(BaseModel):
    input_texts: List[InputText]
    outline_prompt: str
    content_prompt: str


class CreateOutlineOnlyRequest(BaseModel):
    input_texts: List[InputText]
    user_prompt: str


class FromWebRequest(BaseModel):
    search_terms: str
    user_prompt: str