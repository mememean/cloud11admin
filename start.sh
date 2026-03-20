#!/bin/bash
# Cloud 11 CMS — Start Script
cd "$(dirname "$0")"
echo "Starting Cloud 11 CMS..."
echo "Open http://localhost:8080/admin/ in your browser"
python3 server.py
