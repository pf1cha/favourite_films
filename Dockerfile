FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3-pip \
    libxkbcommon-x11-0 \
    libxcb-xinerama0 \
    libglib2.0-0 \
    libxcb-xinput0 \
    libxcb-cursor0 \
    libxcb-render0 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-icccm4 \
    libxcb-sync1 \
    libxcb-render-util0 \
    libx11-xcb1 \
    libgl1 \
    libegl1 \
    libfontconfig1 \
    libdbus-1-3 \
    xvfb \
    fonts-liberation \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Qt environment variables
ENV QT_DEBUG_PLUGINS=0
ENV QT_QPA_PLATFORM=xcb
ENV DISPLAY=:99

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
