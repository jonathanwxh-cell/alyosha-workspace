#!/bin/bash
# secure-serve.sh - Serve files securely on localhost only
# Usage: ./secure-serve.sh [port] [directory]
# 
# This binds to 127.0.0.1 (localhost) only, not 0.0.0.0
# Use with cloudflared tunnel for external access

PORT=${1:-8080}
DIR=${2:-.}

echo "🔒 Secure server starting..."
echo "   Directory: $DIR"
echo "   Port: $PORT"
echo "   Binding: 127.0.0.1 (localhost only)"
echo ""
echo "For external access, use:"
echo "   cloudflared tunnel --url http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop"

cd "$DIR" && python3 -c "
import http.server
import socketserver

PORT = $PORT
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as httpd:
    print(f'Serving on http://127.0.0.1:{PORT}')
    httpd.serve_forever()
"
