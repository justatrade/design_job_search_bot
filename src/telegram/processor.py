import logging

from sqlalchemy.ext.asyncio import AsyncSession
from telethon import events

from src.core.settings import settings
from src.db.session import AsyncSessionLocal
from src.services.filters import filter_cache
from src.telegram.instance import tg
from src.telegram.utils import get_chat_display_name, get_chat_reference

log = logging.getLogger(__name__)


async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        return session

async def message_handler(event: events.NewMessage.Event):
    if not tg.toggle_filtering:
        return

    message = event.message
    if not message or not message.message:
        log.debug("📭 Пропущено: пустое сообщение")
        return

    chat = await event.get_chat()
    chat_id = getattr(chat, "id", None)
    if not chat_id:
        log.debug("🚫 Пропущено: нет chat.id")
        return

    if chat_id == settings.telegram.target_channel_id:
        log.debug("🔁 Пропущено: сообщение из целевого канала")
        return

    db = await get_db_session()
    filters = await filter_cache.get(db)

    matched = filter_cache.extract_matched_keywords(message.message, filters)
    if len(matched) < len(filters):
        log.debug(f"🔍 Не все группы сработали: {matched}")
        return

    chat_name = get_chat_display_name(chat)
    chat_link = get_chat_reference(chat)
    preview = message.message[:60].replace("\n", " ").strip()

    hashtags = " ".join(
        f"#{kw.replace(' ', '_')}" for group in matched.values() for kw in group
    )

    comment = f"💬 Сообщение из: {chat_link}\n{hashtags}".strip()

    log.info(f"🔍 Прошло фильтр: {chat_name} → {preview}")
    log.debug(f"🧷 Хэштеги: {hashtags}")

    try:
        await tg.send_message(settings.telegram.target_channel_id, comment)
        await message.forward_to(settings.telegram.target_channel_id)
        log.info(f"✅ Переслано в {settings.telegram.target_channel_id}")
    except Exception as e:
        log.warning(f"❌ Ошибка пересылки: {e}")
