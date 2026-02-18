FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files first to leverage cache
COPY pyproject.toml uv.lock ./

# Install dependencies using the lockfile
# --frozen: strict lockfile usage
# --no-install-project: we just want dependencies, not the project itself (since it's a script)
RUN uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY main.py .

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]