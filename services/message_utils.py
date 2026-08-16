"""Helpers for sending messages that may exceed Telegram's length limit."""

# Telegram caps a single message at 4096 UTF-16 code units. Astral characters
# (most emoji, some symbols) take 2 code units, so slicing by Python character
# count can still overflow. Split by code units instead.
_TELEGRAM_LIMIT = 4096


def _code_units(ch: str) -> int:
    return 2 if ord(ch) > 0xFFFF else 1


def split_message(text: str, limit: int = 4000) -> list[str]:
    """Split text into chunks of at most `limit` UTF-16 code units.

    Uses 4000 (not 4096) as headroom so a chunk never trips Telegram's limit.
    """
    if not text:
        return [""]
    chunks: list[str] = []
    current = ""
    units = 0
    for ch in text:
        cu = _code_units(ch)
        if units + cu > limit:
            chunks.append(current)
            current = ch
            units = cu
        else:
            current += ch
            units += cu
    if current:
        chunks.append(current)
    return chunks
