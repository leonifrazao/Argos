FROM ultralytics/ultralytics:latest-cpu
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_SYSTEM_PYTHON=1
WORKDIR /app
RUN mkdir -p src/domain/models && \
    curl -L -o src/domain/models/yolov8n.pt https://huggingface.co/Ultralytics/YOLOv8/resolve/main/yolov8n.pt

COPY pyproject.toml uv.lock ./

RUN uv pip install -e .
COPY . .

CMD ["python", "main.py"]
