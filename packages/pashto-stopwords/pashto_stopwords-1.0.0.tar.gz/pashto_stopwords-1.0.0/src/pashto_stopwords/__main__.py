# src/pashto_stopwords/__main__.py
import pandas as pd
import sys
from pathlib import Path
import re # Now correctly imported for robust cleaning

INPUT_FILE = Path("data") / "pashto-stopwords.txt"
OUTPUT_DIR = Path("stopwords")

def clean_line(line: str) -> str | None:
    """په بشپړه توګه پاکوي: ټول خالي ځایونه، ټیب، نبض، او خالي سطرونه"""
    
    # 1. Zero-width & BOM removal
    line = line.replace('\u200b', '').replace('\ufeff', '')
    
    # 2. CRITICAL FIX: Normalize ALL whitespace (tabs, multiple spaces, etc.) to a single space, then strip.
    line = re.sub(r'\s+', ' ', line).strip()
    
    # 3. Skip comments & old header
    if not line or line.startswith('#') or line.lower() == 'word':
        return None
        
    return line

def main():
    print("پښتو بند-کلمې — د ډاټا بشپړ پاکول")
    print("=" * 55)

    if not INPUT_FILE.exists():
        print(f"فایل نه موندل شو: {INPUT_FILE}")
        print("   → 'data/pashto-stopwords.txt' جوړ کړئ")
        sys.exit(1)

    print(f"د فایل لوستل: {INPUT_FILE}")
    raw_lines = INPUT_FILE.read_text(encoding='utf-8').splitlines()
    
    clean_words = []
    rejected_count = 0
    
    for i, line in enumerate(raw_lines, 1):
        cleaned = clean_line(line)
        if cleaned:
            clean_words.append(cleaned)
        elif line.strip() and not cleaned:
            # Counts lines rejected due to being comments or the old 'word' header
            rejected_count += 1 

    # د تکرار لرې کول او ترتیب کول
    # Converting to list(set()) ensures unique entries
    clean_words = sorted(list(set(clean_words))) 
    
    df = pd.DataFrame(clean_words, columns=['word'])
    print(f"پاکې شوې کلمې: {len(df):,} (تکرار لرې شو، {rejected_count} کرښې رد شوې)")

    # احصائیه
    if not df.empty:
        lengths = df['word'].str.len()
        print(f"\nاحصائیه:")
        print(f"   اوږده کلمه → '{df.loc[lengths.idxmax(), 'word']}' ({lengths.max()} توري)")
        print(f"   لنډه کلمه  → '{df.loc[lengths.idxmin(), 'word']}' ({lengths.min()} توري)")

    # ذخیره کول
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_DIR / "pashto-stopwords.csv", index=False, encoding='utf-8')
    df.to_json(OUTPUT_DIR / "pashto-stopwords.json", orient='records', indent=2, force_ascii=False)
    df.to_pickle(OUTPUT_DIR / "pashto-stopwords.pkl")
    
    try:
        # Requires the 'openpyxl' dependency defined in pyproject.toml
        df.to_excel(OUTPUT_DIR / "pashto-stopwords.xlsx", index=False, engine='openpyxl')
        print("Excel ذخیره شو")
    except Exception:
        print("Excel لپاره: pip install openpyxl")

    # تازه TXT (د PyPI لپاره - دا هغه فایل دی چې ستاسو __init__.py به یې ولولي)
    (OUTPUT_DIR / "pashto-stopwords.txt").write_text("\n".join(clean_words), encoding='utf-8')

    print(f"\nبشپړ شو! پاک فایلونه دلته دي: {OUTPUT_DIR.resolve()}")
    print("\nد پاکولو ازموینه:")
    test_text = "دا یو مثال دی چې آیا دا کار کوي"
    
    # For testing, we load the newly generated clean list
    try:
        from pashto_stopwords import STOPWORDS
    except ImportError:
        # Fallback if running outside of package context
        STOPWORDS = set(clean_words)
        
    def remove_stopwords(text, sw_set):
        return " ".join(word for word in text.split() if word not in sw_set)

    print(f"   → '{test_text}'")
    print(f"   → د پاکولو پایله: '{remove_stopwords(test_text, STOPWORDS)}'")

if __name__ == "__main__":
    main()