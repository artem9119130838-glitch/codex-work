#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook Auto-Deploy Daemon for Tender RAG API
Слушает входящие HTTP POST-запросы на порту 9876.
При получении валидного X-Deploy-Token запускает /usr/local/bin/deploy-tender.sh.
"""

import os
import subprocess
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

SECRET_TOKEN = "tender_deploy_sec_9119130838_wlisses"
PORT = 9876

class DeployHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "tender-webhook-deploy"}).encode())
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        token_header = self.headers.get("X-Deploy-Token", "")
        auth_header = self.headers.get("Authorization", "").replace("Bearer ", "")
        
        # Check query param as fallback
        query_token = ""
        if "?" in self.path:
            for param in self.path.split("?")[1].split("&"):
                if param.startswith("token="):
                    query_token = param.split("=")[1]

        if SECRET_TOKEN not in (token_header, auth_header, query_token):
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Forbidden: invalid deploy token"}).encode())
            return

        def run_deploy():
            subprocess.run(["/usr/local/bin/deploy-tender.sh"], capture_output=True)

        threading.Thread(target=run_deploy).start()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok", "message": "Deployment triggered successfully"}).encode())

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), DeployHandler)
    server.serve_forever()
