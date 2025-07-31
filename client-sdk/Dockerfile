# Stage 1: Build Stage
FROM rust:1.82 AS builder

# Install Node.js, npm, and TypeScript for JavaScript/TS build
RUN apt-get update && apt-get install -y nodejs npm

# Define build arguments
ARG INSIGHTS_ENDPOINT
ARG INSIGHTS_SECRET
ARG INSIGHTS_SALT
ARG INSIGHTS_DEBUG

# Set working directory
WORKDIR /app

# Copy Rust project files from core folder
COPY core ./core

# Install Rust toolchain components
RUN cargo install wasm-pack

# Build Rust code from core folder
RUN cd core && wasm-pack build --target web --release

# Copy JavaScript/TypeScript project files
COPY package.json ./
COPY tsconfig.json ./
COPY src ./src
COPY build.mjs ./

# Install JS/TS dependencies, including typescript
RUN npm install
RUN npm install -g typescript

# Build JS/TS code with environment variables from build arguments
RUN INSIGHTS_ENDPOINT=${INSIGHTS_ENDPOINT} \
    INSIGHTS_SECRET=${INSIGHTS_SECRET} \
    INSIGHTS_SALT=${INSIGHTS_SALT} \
    INSIGHTS_DEBUG=${INSIGHTS_DEBUG} \
    node build.mjs

# Create dist folder and move pkg into it
RUN mkdir -p dist && mv core/pkg dist/

# Stage 2: Runner Stage
FROM node:20-slim AS runner

# Set working directory
WORKDIR /app

# Copy only the dist folder from builder
COPY --from=builder /app/dist ./dist

# Install a lightweight HTTP server
RUN npm install -g serve

# Expose port for serving
EXPOSE 9005

# Clean up unnecessary files to optimize image
RUN apt-get update && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Serve the dist folder
CMD ["serve", "-s", "dist", "-l", "9005", "--cors"]