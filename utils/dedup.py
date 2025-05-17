# utils/dedup.py
from pathlib import Path

record_file = Path("processed_items.txt")
if not record_file.exists():
    record_file.touch()  # 创建空文件
    records = []
else:
    records = record_file.read_text().splitlines()


def search(entry) -> bool:
    return entry.id.strip() in records


def mark(entry):
    records.append(entry.id.strip())


def sync():
    with open(record_file, 'w') as f:
        for r in records:
            f.write(f"{r}\n")
