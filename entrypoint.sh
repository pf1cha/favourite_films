#!/bin/bash

# Start Xvfb in the background on display :99
Xvfb :99 -screen 0 1024x768x16 &

# Wait for Xvfb to initialize
sleep 1

# Run database migrations, tests and app
alembic upgrade head
pytest
python3 main.py
