FROM python:3.12-slim

WORKDIR /app

# Install OS deps needed by some Python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directory for fresh per-run review files (also created at runtime,
# but pre-creating avoids a first-request permission surprise)
RUN mkdir -p /app/runs

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
