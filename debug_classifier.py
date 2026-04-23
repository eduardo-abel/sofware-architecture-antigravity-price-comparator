import json

with open('amazon_classified.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for cat, items in data.items():
    print(f"\n--- {cat} ---")
    for p in items[:10]:
        print(f"[{p.get('price')}] {p.get('title')}")
