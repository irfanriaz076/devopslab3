# Use Python 3.9 slim image as base for smaller footprint
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Create input and output directories
RUN mkdir -p /input/logs /output

# Copy requirements first (leverages Docker layer caching)
COPY requirements.txt . 

# Install dependencies using pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY model.pkl . 

COPY inference.py . 

# Set permissions for output directory
RUN chmod -R 777 /output

CMD ["python", "inference.py"]
