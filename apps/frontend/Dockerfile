FROM python:3.11-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy source code
COPY app.py .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 2001

# Run the application
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=2001", "--server.address=0.0.0.0"]
