import asyncio
import logging

from telethon import events, TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

from src.core.settings import settings

log = logging.getLogger(__name__)

class Telegram(TelegramClient):
    def __init__(self):
        session_path = (
            f"{settings.telegram.session_dir}/{settings.telegram.login}"
        )
        super().__init__(
            session=session_path,
            api_id=settings.telegram.api_id,
            api_hash=settings.telegram.api_hash,
        )
        self.phone_code_hash: str | None = None
        self.toggle_filtering: bool = True

    async def start_client(self):
        if not self.is_connected():
            await self.connect()

    async def send_code(self) -> None:
        await self.start_client()
        result = await self.send_code_request(settings.telegram.login)
        self.phone_code_hash = result.phone_code_hash

    async def confirm_code(self, code: str) -> None:
        await self.start_client()

        if not self.phone_code_hash:
            raise ValueError(
                "No phone_code_hash available. Did you call /auth/start first?"
            )

        try:
            await self.sign_in(
                phone=settings.telegram.login,
                code=code,
                phone_code_hash=self.phone_code_hash,
            )
            self.phone_code_hash = None
        except PhoneCodeInvalidError:
            raise ValueError("Invalid code.")
        except SessionPasswordNeededError:
            raise NotImplementedError(
                "2FA is enabled. Password auth not implemented yet."
            )

    async def get_chats(self) -> list[dict]:
        await self.start_client()
        chats = []

        async for dialog in self.iter_dialogs():
            entity = dialog.entity
            chats.append({
                "id": dialog.id,
                "title": dialog.name,
                "type": type(entity).__name__,
                "username": getattr(entity, "username", None),
                "megagroup": getattr(entity, "megagroup", None),
            })

        return chats

    async def run_listener(self):
        from src.telegram.processor import message_handler
        await self.start_client()

        @self.on(events.NewMessage())
        async def handler(event):
            await message_handler(event)

        log.info("🔁 Telegram listener started.")
        await self.run_until_disconnected()

    def start_background_listener(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.run_listener())