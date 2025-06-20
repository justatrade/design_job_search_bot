from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.session import get_db
from src.db import models
from src.db import schemas
from src.services.filters import filter_cache


router = APIRouter(prefix="/filters", tags=["Filters"])

@router.post("/groups", response_model=schemas.FilterGroupOut)
async def create_group(data: schemas.FilterGroupCreate, db: AsyncSession = Depends(get_db)):
    group = models.FilterGroup(name=data.name, is_active=data.is_active)
    db.add(group)
    try:
        await db.commit()
        await db.refresh(group)
        await filter_cache.invalidate()
        return group
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Group with this name already exists")

@router.get("/groups", response_model=list[schemas.FilterGroupFull])
async def list_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.FilterGroup).options(selectinload(models.FilterGroup.keywords)))
    return result.scalars().all()

@router.delete("/groups/{group_id}", status_code=204)
async def delete_group(group_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(models.FilterGroup).filter_by(id=group_id))
    await db.commit()
    await filter_cache.invalidate()

@router.post("/keywords", response_model=schemas.FilterKeywordOut)
async def add_keyword(data: schemas.FilterKeywordCreate, db: AsyncSession = Depends(get_db)):
    keyword = models.FilterKeyword(value=data.value.strip(), group_id=data.group_id)
    db.add(keyword)
    await db.commit()
    await db.refresh(keyword)
    await filter_cache.invalidate()
    return keyword

@router.delete("/keywords/{keyword_id}", status_code=204)
async def delete_keyword(keyword_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(models.FilterKeyword).filter_by(id=keyword_id))
    await db.commit()
    await filter_cache.invalidate()

@router.post("/keywords/bulk", status_code=201)
async def add_keywords_bulk(
    data: schemas.FilterKeywordBulkCreate,
    db: AsyncSession = Depends(get_db),
):
    keywords = [
        models.FilterKeyword(value=value.strip(), group_id=data.group_id)
        for value in data.values if value.strip()
    ]
    db.add_all(keywords)
    await db.commit()
    await filter_cache.invalidate()
    return {"inserted": len(keywords)}
