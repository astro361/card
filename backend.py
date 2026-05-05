#!/usr/bin/env python3
"""
Simple HTTP server to handle contact form submissions and save to CSV.
Messages are saved to messages.csv which can be imported into Excel.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import csv
import os
from datetime import datetime
from io import StringIO

MESSAGES_FILE = 'messages.csv'
PORT = 5000

class MessageHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/send-message':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(body)
                name = data.get('name', '').strip()
                email = data.get('email', '').strip()
                message = data.get('message', '').strip()
                
                # Validate
                if not name or not email or not message:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    response = json.dumps({'success': False, 'error': 'All fields required'})
                    self.wfile.write(response.encode('utf-8'))
                    return
                
                # Save to CSV
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                file_exists = os.path.exists(MESSAGES_FILE)
                
                with open(MESSAGES_FILE, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        # Write header
                        writer.writerow(['Name', 'Email', 'Message', 'Date & Time'])
                    # Write message
                    writer.writerow([name, email, message, timestamp])
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({
                    'success': True,
                    'message': 'Your message has been saved successfully!'
                })
                self.wfile.write(response.encode('utf-8'))
                print(f"✓ Message saved: {name} ({email})")
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'success': False, 'error': str(e)})
                self.wfile.write(response.encode('utf-8'))
                print(f"✗ Error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/api/messages':
            try:
                messages = []
                if os.path.exists(MESSAGES_FILE):
                    with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            messages.append(row)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'messages': messages})
                self.wfile.write(response.encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = json.dumps({'error': str(e)})
                self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), MessageHandler)
    print(f"✓ Message server running on http://localhost:{PORT}")
    print(f"✓ Messages will be saved to {os.path.abspath(MESSAGES_FILE)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
        server.server_close()
