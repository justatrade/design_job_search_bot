def get_chat_display_name(chat) -> str:
    if hasattr(chat, "title") and chat.title:
        return chat.title
    elif hasattr(chat, "first_name") or hasattr(chat, "last_name"):
        first = getattr(chat, "first_name", "")
        last = getattr(chat, "last_name", "")
        return f"{first} {last}".strip()
    elif hasattr(chat, "username") and chat.username:
        return f"@{chat.username}"
    else:
        return f"Chat {chat.id}"

def get_chat_reference(chat) -> str:
    if getattr(chat, "username", None):
        return f"https://t.me/{chat.username}"
    return get_chat_display_name(chat)