FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application using fastapi standard library's CLI
CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]