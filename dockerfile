# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the contents of the current directory into the container at /app
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN pip install Flask

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=moodifytunes/spotify_api.py

# Run the Flask script when the container launches
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
