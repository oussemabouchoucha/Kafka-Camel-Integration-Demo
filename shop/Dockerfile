# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# --- ZID HEDHA (FIX PRO) ---
# Install system dependencies required for confluent-kafka
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc-dev librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*
# ---------------------------

# Copy requirements
COPY requirements.txt .

# Install python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Expose port
EXPOSE 5000

# CMD: Nans7ek b 'python app.py' adhmon men 'flask run'
# Khater 'app.py' fih el 'if __name__ == "__main__"'
CMD ["python", "app.py"]