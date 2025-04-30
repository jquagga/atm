# First, build the application in the `/app` directory
FROM ghcr.io/astral-sh/uv:bookworm-slim@sha256:6515f98c390edf376feb0e1fae510c65a088d84daa6f045c5ce728a839889d7f AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Configure the Python directory so it is consistent
ENV UV_PYTHON_INSTALL_DIR=/python

# Only use the managed Python version
ENV UV_PYTHON_PREFERENCE=only-managed

# Install Python before the project for caching
RUN uv python install 3.13

WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Then, use a final image without uv
FROM gcr.io/distroless/base-debian12:nonroot@sha256:fa5f94fa433728f8df3f63363ffc8dec4adcfb57e4d8c18b44bceccfea095ebc

# Copy the Python version
COPY --from=builder --chown=python:python /python /python

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Run the FastAPI application by default
CMD ["python", "-u", "/app/main.py"]
