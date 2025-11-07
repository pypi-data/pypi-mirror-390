# build stage: build wheel + extract dependencies
FROM python:3.13 as build

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY . ./

# install git for versioning
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git && \
	rm -rf /var/lib/apt /var/lib/dpkg /var/lib/cache /var/lib/log

RUN pip install --upgrade pip
RUN pip install hatch

RUN hatch build --clean

# install stage: install package + dependencies
FROM python:3.13 as install

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY --from=build /app/dist/*.whl /app

# create virtualenv
RUN python -m venv /opt/venv

# ensure virtualenv python is preferred
ENV PATH="/opt/venv/bin:$PATH"

run pip install --upgrade pip
RUN pip install *.whl

# final stage: installed app
FROM python:3.13-slim as app

COPY --from=install /opt/venv /opt/venv

# create app user
RUN groupadd --gid 1000 arrakis && \
    useradd --uid 1000 --gid 1000 -m arrakis

USER arrakis

# ensure virtualenv python is preferred
ENV PATH="/opt/venv/bin:$PATH"

ENTRYPOINT ["arrakis-server"]
CMD ["kafka"]
