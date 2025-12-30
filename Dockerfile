FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY .streamlit/ /app/.streamlit/

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/logs /app/data/cache

# Create empty .gitkeep files
RUN touch /app/data/uploads/.gitkeep /app/data/logs/.gitkeep /app/data/cache/.gitkeep

# Expose Streamlit port
EXPOSE 8501

# Set environment
ENV PYTHONUNBUFFERED=1

# Run Streamlit
CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
