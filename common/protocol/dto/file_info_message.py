from datetime import datetime

from pydantic import BaseModel


class FileInfoMessage(BaseModel):
    name: str
    path: str
    last_mod: datetime
