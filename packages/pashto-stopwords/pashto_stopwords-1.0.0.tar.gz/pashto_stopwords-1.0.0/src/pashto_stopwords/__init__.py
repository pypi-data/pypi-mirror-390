"""
پښتو بند-کلمې v1.0
د پښتو NLP لپاره لومړنی معیاري کارپس
© ۲۰۲۵ IPashto.AI / Spinzar Enterprises
بنسټ: https://github.com/mohbadar/pashto-stopwords
"""
from pathlib import Path
from typing import Set
import re

__version__ = "1.0.0"
__all__ = ["STOPWORDS", "remove_stopwords"]

# د فایل لاره — اوس د پیکج دننه!
STOPWORDS_FILE = Path(__file__).with_name("pashto-stopwords.txt")

def _load_stopwords() -> Set[str]:
    if not STOPWORDS_FILE.exists():
        raise FileNotFoundError(f"فایل نه موندل شو: {STOPWORDS_FILE}")
    text = STOPWORDS_FILE.read_text(encoding="utf-8")
    words = []
    for line in text.splitlines():
        line = line.replace('\u200b', '').replace('\ufeff', '')
        line = re.sub(r'\s+', ' ', line).strip()
        if line and not line.startswith('#') and line.lower() != 'word':
            words.append(line)
    return set(words)

STOPWORDS: Set[str] = _load_stopwords()

def remove_stopwords(text: str) -> str:
    """د بند-کلمو لرې کول — د پښتو لپاره جوړ شوی"""
    words = text.split()
    return " ".join(w for w in words if w not in STOPWORDS)
