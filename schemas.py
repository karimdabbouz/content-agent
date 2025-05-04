from pydantic import BaseModel
from typing import Optional, List
import datetime


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