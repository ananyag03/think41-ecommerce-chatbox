# Use an official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the rest of the code
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your app
CMD ["python", "load_data.py"]
