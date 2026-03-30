# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install project dependencies
RUN pip install --no-cache-dir \
    fastapi \
    pydantic \
    uvicorn \
    openai \
    python-multipart \
    pyyaml

# Expose the port the app runs on
EXPOSE 7860

# Command to run the application
# For HF Spaces, ensure host is 0.0.0.0 and port matches exposed port
CMD ["python", "app.py"]
