from pydantic import BaseModel, model_validator
from typing import Optional, List, Tuple, Literal, Union
import datetime


# class MCPServerConfigs(BaseModel):
#     '''
#     Configurations for MCP servers that can be either used for HTTP or Stdio transport.
#     '''
#     transport: Literal['stdio', 'http']
#     server_urls: Optional[List[str]] = None
#     stdio_commands: Optional[List[Tuple[str, List[str]]]] = None

#     @model_validator(mode='after')
#     def check_transport_mode(self):
#         if self.transport == 'http':
#             if not self.server_urls:
#                 raise ValueError('server_urls must be provided if transport is http')
#         elif self.transport == 'stdio':
#             if not self.stdio_commands:
#                 raise ValueError('stdio_commands must be provided if transport is stdio')
#         else:
#             raise ValueError('transport must be either http or stdio')
#         return self


class MCPServerConfig(BaseModel):
    '''
    Configurations for MCP servers with either HTTP or Stdio transport.
    '''
    transport: Literal['stdio', 'http']
    connection: Union[Tuple[str, List[str]], str]

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
        return self


class InputTextMetadata(BaseModel):
    created_at: Optional[datetime.datetime] = None
    num_words: Optional[int] = None


class Paragraph(BaseModel):
    subheadline: Optional[str] = None
    text: str


class InputText(BaseModel):
    metadata: InputTextMetadata
    headline: Optional[str] = None
    teaser: Optional[str] = None
    body: List[Paragraph]


class OutputText(BaseModel):
    headline: Optional[str] = None
    teaser: Optional[str] = None
    body: List[Paragraph]