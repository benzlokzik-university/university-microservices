FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --no-group test --frozen

FROM alpine:3.23

WORKDIR /app

RUN apk add --no-cache libstdc++

COPY --from=builder /usr/local /usr/local
COPY --from=builder /app/.venv /app/.venv
COPY . .

RUN ln -sf /usr/local/bin/python3.12 /app/.venv/bin/python && \
    ln -sf /usr/local/bin/python3.12 /app/.venv/bin/python3 && \
    ln -sf /usr/local/bin/python3.12 /app/.venv/bin/python3.12 && \
    find /app/.venv/bin -type f -executable -exec sed -i '1s|^#!.*|#!/app/.venv/bin/python|' {} \;

EXPOSE 8006

CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"]
