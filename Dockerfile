FROM python:3.11-alpine
LABEL authors="eugeny.kuz@gmail.com"

RUN pip install poetry
RUN apk update
RUN apk add ffmpeg

WORKDIR /drf-ffmpeg
COPY ./ /drf-ffmpeg/
RUN touch /drf-ffmpeg/deploy/logs/gunicorn/access.log
RUN touch /drf-ffmpeg/deploy/logs/gunicorn/error.log
VOLUME ["/drf-ffmpeg/db.sqlite3", "/drf-ffmpeg/static", "/drf-ffmpeg/media"]

RUN poetry install --with production

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

CMD ["poetry", "run", "gunicorn", "-c", "deploy/config/gunicorn_config.py"]
