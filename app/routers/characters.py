from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Character
from app.schemas import CharacterCreate, CharacterResponse, CharacterUpdate

router = APIRouter(prefix="/characters", tags=["characters"])

NOT_FOUND_DETAIL = "Character not found"
CONFLICT_DETAIL = "A character with that name and actor already exists"

NOT_FOUND: dict[int | str, dict[str, Any]] = {404: {"description": NOT_FOUND_DETAIL}}
CONFLICT: dict[int | str, dict[str, Any]] = {409: {"description": CONFLICT_DETAIL}}


def get_character_or_404(character_id: int, db: Session) -> Character:
    character = db.query(Character).filter(Character.id == character_id).first()
    if character is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL
        )
    return character


def check_for_duplicate(
    name: str, actor: str, db: Session, ignore_id: int | None = None
) -> None:
    """Raise a 409 if another character already has this name and actor (ignoring case)."""
    query = db.query(Character).filter(
        func.lower(Character.name) == name.lower(),
        func.lower(Character.actor) == actor.lower(),
    )
    if ignore_id is not None:
        query = query.filter(Character.id != ignore_id)
    if query.first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=CONFLICT_DETAIL
        )


@router.get("/", response_model=list[CharacterResponse])
def read_characters(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=0, le=100, description="Maximum number of records to return (0-100)"
    ),
    name: str | None = Query(
        None,
        description="Only return characters whose name contains this text (not case-sensitive)",
    ),
    db: Session = Depends(get_db),
):
    """
    Return a list of characters, ordered by ID.

    - **skip**: number of records to skip (for pagination)
    - **limit**: maximum number of records to return (default 10, max 100)
    - **name**: optional filter, e.g. `?name=tony`
    """
    query = db.query(Character)
    if name:
        query = query.filter(Character.name.ilike(f"%{name}%"))
    return query.order_by(Character.id).offset(skip).limit(limit).all()


@router.get("/{character_id}", response_model=CharacterResponse, responses=NOT_FOUND)
def read_character(character_id: int, db: Session = Depends(get_db)):
    """Return one character by its ID. Returns 404 if no character has that ID."""
    return get_character_or_404(character_id, db)


@router.post(
    "/",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    responses=CONFLICT,
)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """
    Create a new character and return it with its new ID.

    Returns 409 if a character with the same name and actor already exists
    (not case-sensitive).
    """
    check_for_duplicate(character.name, character.actor, db)
    db_character = Character(**character.model_dump())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.put(
    "/{character_id}",
    response_model=CharacterResponse,
    responses={**NOT_FOUND, **CONFLICT},
)
def update_character(
    character_id: int, character: CharacterUpdate, db: Session = Depends(get_db)
):
    """
    Replace every field of an existing character.

    Returns 404 if no character has that ID, and 409 if the new name and actor
    match a *different* character.
    """
    db_character = get_character_or_404(character_id, db)
    check_for_duplicate(character.name, character.actor, db, ignore_id=character_id)
    for field, value in character.model_dump().items():
        setattr(db_character, field, value)
    db.commit()
    db.refresh(db_character)
    return db_character


@router.delete(
    "/{character_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND
)
def delete_character(character_id: int, db: Session = Depends(get_db)):
    """Delete a character. Returns 204 with no body, or 404 if no character has that ID."""
    db_character = get_character_or_404(character_id, db)
    db.delete(db_character)
    db.commit()