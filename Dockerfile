FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir ".[api]"
COPY configs ./configs
COPY datasets ./datasets
RUN mkdir -p /data && chown 65532:65532 /data

USER 65532:65532
EXPOSE 8000
CMD ["uvicorn", "llm_guardian.api:app", "--host", "0.0.0.0", "--port", "8000"]
