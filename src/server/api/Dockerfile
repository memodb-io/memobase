FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Set working directory
WORKDIR /app

# Copy dependency files
COPY ./pyproject.toml /app
COPY ./uv.lock /app

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev --no-cache-dir

# Copy the application code
COPY ./memobase_server /app/memobase_server
COPY ./api.py /app



# Expose port 8000 (FastAPI default)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the FastAPI server using uvicorn
CMD ["/app/.venv/bin/uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
