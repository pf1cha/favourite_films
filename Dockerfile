FROM ubuntu:22.04

# Установка Python и системных зависимостей
RUN apt-get update && apt-get install -y \
    python3-pip \
    libgl1-mesa-dev \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-render0 \
    libxcb-glx0 \
    libxi6 \
    libxkbfile1 \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    # X11 и графические библиотеки
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    libxi6 \
    libxrender1 \
    libxtst6 \
    # OpenGL/EGL
    libegl1 \
    libgl1 \
    libgl1-mesa-glx \
    libglvnd0 \
    libglx0 \
    libgles2 \
    # Дополнительные зависимости
    libfontconfig1 \
    libdbus-1-3 \
    libglib2.0-0 \
    # Виртуальный фреймбуфер
    xvfb \
    # Шрифты
    fonts-dejavu \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Настройка окружения Qt
ENV QT_DEBUG_PLUGINS=0
ENV QT_QPA_PLATFORM=xcb
ENV QT_XCB_GL_INTEGRATION=xcb_egl
ENV DISPLAY=:99
ENV XDG_RUNTIME_DIR=/tmp/runtime-root

WORKDIR /app
# Установка зависимостей Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Скрипт для запуска Xvfb и приложения
CMD ["python3", "main.py"]