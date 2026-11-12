"""A deterministic canary router: the same order id always goes to the same model."""
import hashlib


def route(request_id, canary_share=0.10):
    # TODO 5 (Part 4):
    #  h = int(hashlib.sha256(request_id.encode()).hexdigest(), 16) % 10_000
    #  return "challenger" if h < canary_share * 10_000 else "champion"
    raise NotImplementedError("TODO 5: finish route() in src/router.py")
