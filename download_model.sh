#!/bin/bash
set -e

MODEL_DIR="$HOME/rag-chatbot/models"
MODEL_FILE="qwen2.5-7b-instruct-q4_k_m.gguf"
MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"

mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_DIR/$MODEL_FILE" ]; then
    SIZE=$(stat -c%s "$MODEL_DIR/$MODEL_FILE" 2>/dev/null || stat -f%z "$MODEL_DIR/$MODEL_FILE")
    if [ "$SIZE" -gt 1000000000 ]; then
        echo "Model already exists at $MODEL_DIR/$MODEL_FILE"
        ls -lh "$MODEL_DIR/$MODEL_FILE"
        exit 0
    else
        echo "Existing file looks too small ($SIZE bytes) - re-downloading"
        rm -f "$MODEL_DIR/$MODEL_FILE"
    fi
fi

echo "Downloading Qwen2.5-7B-Instruct Q4_K_M (~4.7GB) from bartowski's GGUF repo..."
curl -fL --progress-bar -o "$MODEL_DIR/$MODEL_FILE" "$MODEL_URL"

SIZE=$(stat -c%s "$MODEL_DIR/$MODEL_FILE" 2>/dev/null || stat -f%z "$MODEL_DIR/$MODEL_FILE")
if [ "$SIZE" -lt 1000000000 ]; then
    echo "ERROR: downloaded file is only $SIZE bytes - something went wrong"
    cat "$MODEL_DIR/$MODEL_FILE"
    exit 1
fi

echo ""
echo "Download complete:"
ls -lh "$MODEL_DIR/$MODEL_FILE"
