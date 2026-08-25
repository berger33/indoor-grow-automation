FROM node:24-bookworm-slim AS panel
WORKDIR /source/web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GROWHUB_WEB_DIST=/app/web/dist
WORKDIR /app
RUN addgroup --system growhub && adduser --system --ingroup growhub growhub
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --requirement requirements.txt
COPY alembic.ini ./
COPY hub/ ./hub/
COPY --from=panel /source/web/dist ./web/dist/
COPY deploy/start-hub.sh /usr/local/bin/start-hub
RUN chmod 0555 /usr/local/bin/start-hub && chown -R growhub:growhub /app
USER growhub
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/start-hub"]
