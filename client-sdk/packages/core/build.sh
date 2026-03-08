#!/bin/bash
# rust-wasm/build.sh
CRATE_DIR="$(pwd)"
CRATE_NAME="wasm_analytics"
TARGET="bundler"
OUTPUT_DIR="pkg"

echo "Building WebAssembly module for $CRATE_NAME..."

if ! command -v wasm-pack &> /dev/null; then
    echo "Installing wasm-pack..."
    cargo install wasm-pack
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install wasm-pack."
        exit 1
    fi
fi

echo "Cleaning previous build artifacts..."
cargo clean

echo "Running wasm-pack build --target $TARGET..."
wasm-pack build --target "$TARGET" --out-dir "$OUTPUT_DIR" --out-name "$CRATE_NAME"

if [ $? -eq 0 ]; then
    echo "Build successful! Output in $CRATE_DIR/$OUTPUT_DIR/"
else
    echo "Error: Build failed."
    exit 1
fi

echo "Generated files:"
ls -l "$OUTPUT_DIR"