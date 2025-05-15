# utils/dedup.py
from pathlib import Path

record_file = Path("processed_items.txt")
if not record_file.exists():
    record_file.touch()  # 创建空文件
    records = []
else:
    records = record_file.read_text().splitlines()


def search(entry_id: str) -> bool:
    return entry_id.strip() in records


def mark(entry_id: str):
    records.append(entry_id.strip())


def sync():
    with open(record_file, 'a') as f:
        for r in records:
            f.write(f"{r}\n")
