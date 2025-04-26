# Use the official python image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first (helps Docker cache this layer)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into the container
COPY . .

# Expose the port FastApi runs
EXPOSE 8000

# Run the application
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]