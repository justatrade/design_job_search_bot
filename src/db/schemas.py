from typing import List

from pydantic import BaseModel, Field


class FilterGroupBase(BaseModel):
    name: str = Field(..., min_length=1)
    is_active: bool = True


class FilterGroupCreate(FilterGroupBase):
    pass


class FilterGroupOut(FilterGroupBase):
    id: int
    class Config:
        orm_mode = True


class FilterKeywordBase(BaseModel):
    value: str = Field(..., min_length=1)


class FilterKeywordCreate(FilterKeywordBase):
    group_id: int


class FilterKeywordOut(FilterKeywordBase):
    id: int
    group_id: int
    class Config:
        orm_mode = True


class FilterGroupFull(FilterGroupOut):
    keywords: List[FilterKeywordOut]


class FilterKeywordBulkCreate(BaseModel):
    group_id: int
    values: list[str]


class FilterKeywordMinusCreate(FilterKeywordBase):
    pass


class FilterKeywordMinusBulkCreate(BaseModel):
    values: list[FilterKeywordMinusCreate]
