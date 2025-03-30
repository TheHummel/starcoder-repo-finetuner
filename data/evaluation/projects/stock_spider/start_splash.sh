#!/bin/bash

if ! docker ps | grep -q "scrapinghub/splash"; then
    echo "Starting Splash container..."
    docker run -d -p 8050:8050 scrapinghub/splash
    if [ $? -eq 0 ]; then
        echo "Splash started successfully on port 8050."
    else
        echo "Failed to start Splash. Is Docker running?"
        exit 1
    fi
else
    echo "Splash is already running."
fi