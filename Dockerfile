# Ref: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# An example using multi-stage image builds to create a final image without uv.

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /apps
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY ./apps /apps

# Then, use a final image without uv
FROM python:3.13-alpine AS production
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Copy the application from the builder
COPY --from=builder --chown=apps:apps /apps /apps
WORKDIR /apps

# Place executables in the environment at the front of the path
ENV PATH="/apps/.venv/bin:$PATH"
ENV PYTHONPATH="."

CMD ["streamlit", "run", "web/main.py", "--server.address", "0.0.0.0", "--server.port", "8000", "--server.headless=true"]
