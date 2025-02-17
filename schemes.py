from pydantic import BaseModel


class NoteModel(BaseModel):
    title: str
    body: str


class NoteModelResponse(BaseModel):
    id: int
    title: str
    body: str
    user_id: int


class SuccessOK(BaseModel):
    success: str = 'ok'
