from pydantic import BaseModel, ConfigDict, Field

class CharacterBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    actor: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    status: str = Field(min_length=1, max_length=7)
    first_season: int = Field(ge=1, le=6, strict=True)
    last_season: int = Field(ge=1, le=6, strict=True)



class CharacterCreate(CharacterBase):
    """Body of a POST request. No `id`: the database assigns it."""


class CharacterUpdate(CharacterBase):
    """Body of a PUT request. An update replaces every field."""


class CharacterResponse(CharacterBase):
    id: int
    model_config = ConfigDict(from_attributes=True)