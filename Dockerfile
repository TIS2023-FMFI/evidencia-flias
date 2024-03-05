FROM python:3.12-slim-bullseye
WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY_VIRTUALENVS_CREATE 0

RUN export DEBIAN_FRONTEND=noninteractive \
    && apt update \
    && apt -y upgrade \
    && apt -y install python3-opencv curl \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/tmp/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH=$POETRY_HOME/bin:$PATH
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root
RUN chown appuser:appuser /app/

USER appuser

COPY --chown=appuser:appuser . /app/
RUN SECRET_KEY=static python manage.py collectstatic --no-input
CMD ["gunicorn", "-b", "0.0.0.0:8000", "flase.wsgi"]
