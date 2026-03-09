#!/usr/bin/env python3
"""
Simple health check server that runs in background.
The bot runs independently.
"""
import os
import time
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = int(os.getenv("PORT", "8000"))

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # Suppress logs

def start_health_server():
    """Start a simple HTTP server for health checks"""
    server = HTTPServer(('0.0.0.0', PORT), HealthHandler)
    print(f"Health check server started on port {PORT}")
    server.serve_forever()

def start_bot():
    """Start the Telegram bot"""
    print("Starting bot...")
    subprocess.run(["python", "-m", "src.bot.main"])

if __name__ == "__main__":
    # Start health server in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # Give health server time to start
    time.sleep(1)

    # Start bot in foreground (blocking)
    start_bot()
