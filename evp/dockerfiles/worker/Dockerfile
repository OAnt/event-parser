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
COPY evp/dockerfiles/worker/amdrocm-stable.sources /etc/apt/sources.list.d/
ARG ROCM_ARCH
RUN apt-get update \
    && apt-get install -y \
    amdrocm10.0-${ROCM_ARCH} \
    amdrocm-core-sdk10.0-${ROCM_ARCH} \
    && rm -rf /var/lib/apt/lists
COPY evp /app/evp
COPY poetry.lock /app/
COPY pyproject.toml /app/
WORKDIR /app/
ENV CMAKE_ARGS="-DGGML_HIP=on"
RUN poetry install --no-root
