FROM python:3.14-slim

ENV UV_VERSION=0.9.6
ENV NODE_VERSION=22.20.0

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl xz-utils \
    && ARCH=$(dpkg --print-architecture) \
    && case "$ARCH" in \
         amd64) NODE_ARCH="x64";; \
         arm64) NODE_ARCH="arm64";; \
         armhf) NODE_ARCH="armv7l";; \
         *) echo "Unsupported architecture: $ARCH" && exit 1;; \
       esac \
    && curl -fsSL "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-$NODE_ARCH.tar.xz" \
       | tar -xJ -C /usr/local --strip-components=1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/$UV_VERSION/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Install Node.js deps
COPY package.json package-lock.json ./
RUN npm ci

# Install Python deps
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Provide a fallback version for setuptools_scm, which fails when the
# .git directory is not available in the Docker build context.
ARG VERSION="0.0.1"
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_SPHINX_ICORE_OPEN_THEME=$VERSION

RUN uv pip install --system .[dev]

# Copy the rest of the application code
COPY . .

# Build the static assets
RUN npm run build

# Expose the port for the development server
EXPOSE 8000

CMD ["./entrypoint.sh"]
