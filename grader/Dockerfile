# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the application code to the container
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt

# Expose the application port
EXPOSE 80

# Command to run the application
CMD ["python", "app.py"]