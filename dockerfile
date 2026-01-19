FROM python:3.13-trixie

ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN pip install uv && \
    uv --version

WORKDIR /app

COPY pyproject.toml .

RUN uv sync

COPY . .

EXPOSE 8000

RUN chmod +x prestart.sh

ENTRYPOINT [ "/app/prestart.sh" ]