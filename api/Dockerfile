FROM python:3.12.2

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install uvicorn and requirements
RUN pip install uvicorn && pip install -r requirements.txt

# Expose port 8000 to the outside world
EXPOSE 8000

# Run uvicorn when the container launches
CMD ["bash", "-c", "uvicorn api:app --reload --host 0.0.0.0 --port 8000"]
