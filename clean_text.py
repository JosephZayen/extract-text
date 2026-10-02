import re
from pathlib import Path

BASE_DIR = Path(__file__).parent 
p = BASE_DIR / "extract.txt"
p_out = BASE_DIR / "cleanText.txt"

with p.open("r", encoding='utf-8') as f:
    rtext = f.read()
    rtext = re.sub(r"\d+(?!\.)","",rtext)
    rtext = rtext.replace("\n\n", "\n")
    text = re.sub(r"(?<!\d)\.(?!\d)","",rtext)

with p_out.open("w", encoding='utf-8') as f:
    f.write(text)