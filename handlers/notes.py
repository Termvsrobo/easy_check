from http import HTTPStatus
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import false, select

from models import Note, User
from schemes import NoteModel, NoteModelResponse, SuccessOK
from utils import SessionDep, get_current_user

notes_router = APIRouter(prefix='/notes', tags=['Note'])


@notes_router.get('/', response_model=List[NoteModelResponse])
async def get_all_notes(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    note_user_id: Optional[int] = None
) -> List[NoteModel]:
    if current_user.is_admin:
        notes_query = select(Note)
        if note_user_id:
            notes_query = notes_query.filter(Note.user_id == note_user_id)
    else:
        notes_query = select(Note).filter(
            Note.user_id == current_user.id,
            Note.is_deleted == false()
        )
    result = session.exec(notes_query)
    return result.all()


@notes_router.get('/{note_id}', response_model=NoteModelResponse)
async def get_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
) -> List[NoteModel]:
    if current_user.is_admin:
        notes_query = select(Note).filter(Note.id == note_id)
    else:
        notes_query = select(Note).filter(
            Note.id == note_id,
            Note.user_id == current_user.id,
            Note.is_deleted == false()
        )
    result = session.exec(notes_query)
    note = result.one_or_none()
    if not note:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Note not found'
        )
    return note


@notes_router.post('/', response_model=NoteModelResponse)
async def create_note(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    new_note: NoteModel = Form(),
) -> List[NoteModel]:
    note = Note(user_id=current_user.id, **new_note.model_dump())
    session.add(note)
    session.commit()
    return note


@notes_router.put('/{note_id}', response_model=NoteModelResponse)
async def update_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
    new_note: NoteModel = Form(),
) -> List[NoteModel]:
    if current_user.is_admin:
        notes_query = select(Note).filter(Note.id == note_id)
    else:
        notes_query = select(Note).filter(
            Note.id == note_id,
            Note.user_id == current_user.id,
            Note.is_deleted == false()
        )
    result = session.exec(notes_query)
    note = result.one_or_none()
    if not note:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Note not found'
        )
    if note.title != new_note.title:
        note.title = new_note.title
    if note.body != new_note.body:
        note.body = new_note.body
    session.commit()
    session.refresh(note)
    return note


@notes_router.delete('/{note_id}', response_model=SuccessOK)
async def delete_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
) -> List[NoteModel]:
    if current_user.is_admin:
        notes_query = select(Note).filter(Note.id == note_id)
    else:
        notes_query = select(Note).filter(
            Note.id == note_id,
            Note.user_id == current_user.id,
            Note.is_deleted == false()
        )
    result = session.exec(notes_query)
    note = result.one_or_none()
    if not note:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Note not found'
        )
    note.is_deleted = True
    session.commit()
    session.refresh(note)
    return SuccessOK()


@notes_router.post('/{note_id}/restore', response_model=NoteModelResponse)
async def restore_note(
    note_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep
) -> List[NoteModel]:
    if current_user.is_admin:
        notes_query = select(Note).filter(Note.id == note_id)
        result = session.exec(notes_query)
        note = result.one_or_none()
        if not note:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Note not found'
            )
        if note.is_deleted:
            note.is_deleted = False
            session.commit()
            session.refresh(note)
    else:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            HTTPStatus.FORBIDDEN.description
        )
    return note
