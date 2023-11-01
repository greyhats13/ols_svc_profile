# Use multi-stage builds for a slimmer and safer image
FROM python:3.11.6-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Stage 2: Run
FROM python:3.11.6-slim-bookworm AS runner

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application from builder
COPY --from=builder /app /app

# Set working directory
WORKDIR /app

# Use a non-root user to run the application, which is safer
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
USER appuser

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["python3", "main.py"]
