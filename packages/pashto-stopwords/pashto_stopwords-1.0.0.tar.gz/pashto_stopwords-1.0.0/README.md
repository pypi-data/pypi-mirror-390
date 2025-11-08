# پښتو بند-کلمې

```bash
pip install pashto-stopwords
# ۱. فولډر پاک کړئ او بیا جوړ کړئ
rm -rf pashto_stopwords
mkdir -p pashto_stopwords

# ۲. پاک فایل کاپي کړئ
cp stopwords/pashto-stopwords.txt pashto_stopwords/

# ۳. __init__.py سم کړئ (د وروستي سطر فکس!)
cat > pashto_stopwords/__init__.py << 'EOF'
"""
پښتو بند-کلمې v1.0
د پښتو NLP لپاره لومړنی معیاري کارپس
جوړونکی: IPashto AI Team
"""

from pathlib import Path
from typing import Set

__version__ = "1.0.0"
__all__ = ["STOPWORDS", "remove_stopwords"]

# لوستل
STOPWORDS_PATH = Path(__file__).parent / "pashto-stopwords.txt"
STOPWORDS: Set[str] = {
    line.strip() 
    for line in STOPWORDS_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
}

def remove_stopwords(text: str) -> str:
    """د پښتو متن څخه بند-کلمې لیرې کوي"""
    return " ".join(word for word in text.split() if word not in STOPWORDS)

# د ازموینې لپاره
if __name__ == "__main__":
    print(f"پښتو بند-کلمې v{__version__} فعالې شوې!")
    print(f"ټولټال: {len(STOPWORDS)} کلمې")
    print(remove_stopwords("دا یو مثال دی چې آیا دا کار کوي"))
