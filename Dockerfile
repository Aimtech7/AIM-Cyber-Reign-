# ══════════════════════════════════════════════════════════════════════════ #
#  Dockerfile — AIM: Cyber Reign
#  Author : Aimtech
# ══════════════════════════════════════════════════════════════════════════ #
#  This Dockerfile packages the game into a container.
#
#  IMPORTANT — GUI NOTE:
#  Ursina/Panda3D is an OpenGL application that requires a display.
#  To run inside Docker you must either:
#    1. Forward an X11 display  (Linux / WSL)
#    2. Use a virtual framebuffer (Xvfb — headless testing only)
#    3. Run on a GPU‑enabled host with nvidia‑docker
#
#  See README.md for full instructions.
# ══════════════════════════════════════════════════════════════════════════ #

# ── Base image ────────────────────────────────────────────────────────── #
# We use a slim Python image to keep the container small.
FROM python:3.11-slim

# ── Metadata labels ───────────────────────────────────────────────────── #
LABEL maintainer="Aimtech"
LABEL project="AIM: Cyber Reign"
LABEL phase="Phase 1 — Foundation"

# ── System dependencies ───────────────────────────────────────────────── #
# Panda3D / Ursina need OpenGL libraries and X11 headers at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────── #
WORKDIR /app

# ── Install Python dependencies first (layer caching optimisation) ───── #
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy project source ──────────────────────────────────────────────── #
COPY . .

# ── Default command ───────────────────────────────────────────────────── #
# When the container starts, run the game entry point.
CMD ["python", "main.py"]
