# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Create user with UID 1000 as required by HF Spaces
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first for caching
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the current directory contents into the container at /app
COPY --chown=user . /app

# Expose the port the app runs on (HF Spaces standard is 7860)
EXPOSE 7860

# Command to run the application
# We use uvicorn to serve the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
