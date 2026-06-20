# Root-level Dockerfile — RAG Chatbot Backend
#
# This is a thin pointer to the real backend Dockerfile, kept here for
# tooling that scans for a Dockerfile at the repository root. The actual
# multi-stage backend image is built from ./backend/Dockerfile, and the
# frontend image from ./frontend/Dockerfile.
#
# To build and run the full stack, use docker-compose.yml instead:
#   docker-compose up --build
#
# To build just the backend image directly from this root context:
#   docker build -f backend/Dockerfile -t rag-chatbot-backend ./backend

FROM python:3.11-slim AS backend

WORKDIR /app

RUN apt-get update -qq && apt-get install -y -qq \
    build-essential curl libpq-dev libmagic1 poppler-utils tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
