#!/usr/bin/env bash

# Start the npm watcher in the background
npm run watch:css &

# Start sphinx-autobuild in the foreground
sphinx-autobuild docs/source docs/build/html --host 0.0.0.0 --port 8000 --watch src/
