FROM python:3.11-slim-bookworm

# Install ChromaDB
RUN pip install chromadb

# Set working directory
WORKDIR /chroma

# Expose port
EXPOSE 1989

# Run ChromaDB
CMD ["chroma", "run", "--host", "0.0.0.0", "--port", "1989", "--path", "/chroma/data"]
