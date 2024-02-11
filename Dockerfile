FROM python:3.12-slim-bullseye
WORKDIR /app
RUN useradd --create-home appuser

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV POETRY_VIRTUALENVS_CREATE 0

RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root
RUN chown appuser:appuser /app/

USER appuser

COPY --chown=appuser:appuser . /app/
RUN SECRET_KEY=static python manage.py collectstatic --no-input
CMD ["gunicorn", "-b", "0.0.0.0:8000", "flase.wsgi"]
