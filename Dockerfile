FROM python:3.11.7-alpine as build

RUN pip install poetry==1.4.2

RUN poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main

COPY src ./

FROM build as app

CMD ["python3", "-m", "kwork_notifier"]