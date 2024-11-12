FROM python:3.11
ENV PYTHONUNBUFFERED=1

RUN pip install poetry
WORKDIR /app/
COPY poetry.lock pyproject.toml /app/
RUN apt-get update && apt-get install -y ffmpeg

RUN poetry config virtualenvs.create false && poetry install
COPY ./backend /app/
COPY .env /app/backend/
