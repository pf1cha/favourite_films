FROM ubuntu:22.04

# Install Python and system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-icccm4 \
    libxcb-render-util0 \
    libx11-xcb1 \
    libgl1 \
    libegl1 \
    libfontconfig1 \
    libdbus-1-3 \
    xvfb \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Qt environment variables
ENV QT_DEBUG_PLUGINS=1
ENV QT_QPA_PLATFORM=xcb
ENV DISPLAY=:99

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Entrypoint script to handle Xvfb and app launch
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
