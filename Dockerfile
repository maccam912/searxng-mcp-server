# Use a standard Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV SEARXNG_URL=https://searxng.example.com

# Copy necessary files
COPY pyproject.toml /app/
COPY server.py /app/

# Install dependencies
RUN pip install --no-cache-dir -e .

# Set the entry point
ENTRYPOINT ["sh", "-c", "python /app/server.py --url ${SEARXNG_URL}"]
