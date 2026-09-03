# Placeholder — built out for real in the Week 7/8 labs (Docker install + containerizing a model).
# This file exists from day one so the repo structure matches what students see in Week 1,
# even though Docker Desktop isn't installed until the Week 7 lab.

FROM python:3.11-slim

WORKDIR /app

COPY environment/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "-m", "src.main"]
