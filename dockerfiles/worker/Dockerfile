FROM ubuntu:24.04
RUN apt-get update \
    && apt-get install -y \
    python3-poetry \
    wget \
    libatomic1 \
    libquadmath0 \
    && rm -rf /var/lib/apt/lists
RUN mkdir --parents --mode=0755 /etc/apt/keyrings
RUN wget https://stable.repo.amd.com/rocm/gpg/packages.gpg -O - | \
    gpg --dearmor | tee /etc/apt/keyrings/amdrocm.gpg > /dev/null
COPY dockerfiles/worker/amdrocm-stable.sources /etc/apt/sources.list.d/
ARG ROCM_ARCH
RUN apt-get update \
    && apt-get install -y \
    amdrocm10.0-${ROCM_ARCH} \
    amdrocm-core-sdk10.0-${ROCM_ARCH} \
    && rm -rf /var/lib/apt/lists
RUN mkdir /app/
ARG UID=1000
ARG GID=1000
RUN userdel --remove ubuntu 2>/dev/null || true \ 
    && groupadd --gid ${GID} app \
    && useradd --uid ${UID} --gid ${GID} --create-home --shell /bin/bash --groups video app
COPY --chown=app:app poetry.lock /app/
COPY --chown=app:app pyproject.toml /app/
WORKDIR /app/
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    CMAKE_ARGS="-DGGML_HIP=on"
ARG POETRY_ARGS="--only main"
RUN poetry install --no-root ${POETRY_ARGS}
COPY --chown=app:app evp /app/evp
ENV LD_LIBRARY_PATH="/opt/rocm/lib:$LD_LIBRARY_PATH"
ENV PATH="/app/.venv/bin:$PATH"
USER app
CMD ["celery", "-A", "evp.workers", "worker",  "-l", "INFO"]
