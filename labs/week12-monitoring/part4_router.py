"""Part 4: a stable canary. Run:  python labs/week12-monitoring/part4_router.py"""
from collections import Counter
from src.router import route

print("order-6  ->", route("order-6"), "| again ->", route("order-6"))
print("order-7  ->", route("order-7"))
ids = [f"order-{i}" for i in range(20000)]
share = sum(route(i) == "challenger" for i in ids) / len(ids)
print(f"challenger share over 20,000 ids: {share:.3f}")
print("with canary_share=0.25:", Counter(route(i, 0.25) for i in ids))
