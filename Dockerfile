FROM trion/ng-cli:8.3.25 AS arbolcursobuilder
USER root
ARG NGENV=
ENV NGENV=${NGENV}
# npm install
COPY frontend/arbol-curso/package.json /npminstall/
COPY frontend/arbol-curso/package-lock.json /npminstall/
WORKDIR "/npminstall"
RUN npm install

# Build arbol-curso
COPY frontend/arbol-curso /app/arbol-curso
RUN mv /npminstall/node_modules /app/arbol-curso/node_modules
WORKDIR "/app/arbol-curso"
RUN npm run build:elements-ng8

FROM trion/ng-cli:8.3.25 AS adminencuestabuilder
USER root
ARG NGENV=
ENV NGENV=${NGENV}
# npm install
COPY frontend/admin-encuesta/package.json /npminstall/
COPY frontend/admin-encuesta/package-lock.json /npminstall/
WORKDIR "/npminstall"
RUN npm install

# Build admin-encuestas
COPY frontend/admin-encuesta /app/admin-encuesta
RUN mv /npminstall/node_modules /app/admin-encuesta/node_modules
WORKDIR "/app/admin-encuesta"
RUN npm install
RUN npm run build:elements-ng8

# Build django y sus dependencias
FROM python:3.7-alpine
ENV PYTHONUNBUFFERED 1
ARG http_proxy=
ENV http_proxy=${http_proxy}
COPY lib/pycharm-debug-py3k.egg /pycharm-debug-py3k.egg

RUN apk add --no-cache \
    bash \
    curl \
    gettext \
    libcurl \
    libjpeg \
    libmemcached \
    libsass \
    npm \
    postgresql-client \
    postgresql-dev \
    supervisor

# Needed for pycurl
ENV PYCURL_SSL_LIBRARY=openssl

RUN apk add --no-cache --virtual build-dependencies \
        build-base \
        curl-dev \
        freetype \
        git \
        jpeg-dev \
        libffi-dev \
        libmemcached-dev \
        linux-headers \
        zlib-dev \
        openldap-dev \
        rust
COPY build/requirements_pinned.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
RUN apk del build-dependencies
RUN rm -rf /root/.cache


COPY build/init.sh /
COPY build/wait-for-postgres.py /
COPY build/wait-for-it.sh /
COPY build/uwsgi.ini /
COPY build/supervisord_common.conf /etc/
COPY build/supervisord.conf /etc/
COPY build/supervisord_dev.conf /etc/

COPY app /app

RUN rm -r /app/static/elements/arbol-curso
COPY --from=arbolcursobuilder /app/arbol-curso/dist /app/static/elements/arbol-curso

RUN rm -r /app/static/elements/admin-encuesta
COPY --from=adminencuestabuilder /app/admin-encuesta/dist /app/static/elements/admin-encuesta

WORKDIR "/app/"
RUN npm install