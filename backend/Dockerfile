FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (if not already strictly covered by the base image for specific browsers needed, but the base image usually has them or we run `playwright install`)
# The base image `mcr.microsoft.com/playwright/python` comes with browsers installed.

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
