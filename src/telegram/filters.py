def passes_keyword_filter(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(kw.strip().lower() in lowered for kw in keywords)

def get_triggered_keywords(text: str, keywords: list[str]) -> list[str]:
    lowered = text.lower()
    return [kw.strip() for kw in keywords if kw.strip().lower() in lowered]