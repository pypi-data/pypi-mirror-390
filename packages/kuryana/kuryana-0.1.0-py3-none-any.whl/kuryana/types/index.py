from pydantic import BaseModel


class ApiGet(BaseModel):
    message: str
