import asyncio
from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models import FilterGroup, MinusKeyword


class FilterCache:
    def __init__(self):
        self._cache: dict[str, list[str]] | None = None
        self._minus_cache: list | None = None
        self._lock = asyncio.Lock()

    async def get(self, db: AsyncSession) -> dict[str, list[str]]:
        async with self._lock:
            if self._cache is not None:
                return self._cache

            result = defaultdict(list)

            stmt = (
                select(FilterGroup)
                .where(FilterGroup.is_active.is_(True))
                .options(
                    selectinload(FilterGroup.keywords)
                )
            )

            groups = (await db.execute(stmt)).scalars().all()
            for group in groups:
                for kw in group.keywords:
                    result[group.name].append(kw.value.lower().strip())

            self._cache = result
            return self._cache

    async def get_minus_kw(self, db: AsyncSession) -> list:
        async with self._lock:
            if self._minus_cache is not None:
                return self._minus_cache

            result = []

            minus_stmt = select(MinusKeyword)
            minus_kws = (await db.execute(minus_stmt)).scalars().all()
            for kw in minus_kws:
                result.append(kw.value.lower().strip())

            self._minus_cache = result
            return result

    async def invalidate(self):
        async with self._lock:
            self._cache = None
            self._minus_cache = None

    @staticmethod
    def message_matches(
            text: str,
            filters: dict[str, list[str]],
            minus_kw: list
    ) -> bool:
        lowered = text.lower()
        if any(kw in lowered for kw in minus_kw):
            return False
        for group_keywords in filters.values():
            if not any(kw in lowered for kw in group_keywords):
                return False
        return True

    @staticmethod
    def extract_matched_keywords(
            text: str,
            filters: dict[str, list[str]],
    ) -> dict[str, list[str]]:
        lowered = text.lower()
        result = {}

        for group, words in filters.items():
            matched = [kw for kw in words if kw in lowered]
            if matched:
                result[group] = matched

        return result

filter_cache = FilterCache()
