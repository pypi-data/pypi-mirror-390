# python:3.14-slim
# Using sha image tag to prevent caching errors:
#   "why am I getting different results between local run & CI run?"
FROM python:3.14-slim AS venv_setup

ARG project_dir=/tmp
ARG project_name
ARG python_version
ARG venv_path

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_PATH=/bin/uv
ENV VENV_PATH="${venv_path}"

COPY . "${project_dir}/"

SHELL [ "/bin/bash", "-c" ]

RUN set -ex \
 && "${UV_PATH}" python install ${python_version}

# Initialize the venv for the specified python version acquired via uv.
RUN set -ex \
 && python3 --version \
 && "${UV_PATH}" python pin "${python_version}" \
 && "${UV_PATH}" venv "${venv_path}"

ENV UV_PROJECT_ENVIRONMENT="${venv_path}"
ENV UV_PYTHON="${venv_path}/bin/python3"

WORKDIR "${project_dir}"

# install project dependencies ready for use in pipeline
RUN set -ex \
 && "${UV_PATH}" run python3 --version \
 && "${UV_PATH}" pip install ".[dev,doc,test]" \
 && "${UV_PATH}" pip uninstall "${project_name}"


FROM python:3.14-slim

ARG python_version
ARG requirements_lock=/tmp/apt_requirements.lock
ARG venv_path

ENV UV_PROJECT_ENVIRONMENT="${venv_path}"
ENV UV_PYTHON="${venv_path}/bin/python3"

COPY docker/ci/apt2_requirements.lock "${requirements_lock}"

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=venv_setup /venv /venv/
COPY --from=venv_setup /root/.local/share/uv/python /root/.local/share/uv/python/

SHELL [ "/bin/bash", "-c" ]

RUN set -ex \
 && apt-get update \
 && /usr/bin/xargs -a "${requirements_lock}" \
    apt-get install \
      -y \
      --no-install-recommends \
 && rm -rf /var/lib/apt/lists/* \
 && git config --global user.email "you@example.com" \
 && git config --global user.name "Your Name"
