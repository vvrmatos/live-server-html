"""
Author: victorkolis
Contact: victorkolis@duck.com

This script serves a web page and automatically refreshes the browser when changes are detected in the served file.

Usage:
    - Place the index.html file in the same directory as this script.
    - Run the script using Python.

Dependencies:
    - Python 3.12

Instructions:
    - The script serves the index.html file on port (set in the scripy).
    - Modify the index.html file as needed.
    - Whenever a change is detected and the server is restarted, the script automatically refreshes the Firefox browser.

"""

# TODO: Make code Browser agnostic in order to work with other tools other than Firefox 

import os
import time
import subprocess
from http.server import SimpleHTTPRequestHandler, HTTPServer
from threading import Thread, Event

class CustomHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

def run_server(stop_event):
    """
    Starts an HTTP server on port 8000 and handles requests indefinitely until the stop event is set.
    """
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, CustomHandler)
    print("Serving on port 8000")

    while not stop_event.is_set():
        httpd.handle_request()

def watch_file(file_path, restart_event):
    """
    Monitors the given file for changes and refreshes Firefox when a change is detected.
    """
    while True:
        last_modified_time = os.path.getmtime(file_path)
        while not restart_event.is_set():
            time.sleep(0.3)  
            current_modified_time = os.path.getmtime(file_path)
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                print(f"Detected change in {file_path}, reloading server and refreshing Firefox...")
                restart_event.set()
                subprocess.run(["osascript", "-e", 'tell application "Firefox" to activate', "-e", 'tell application "System Events" to keystroke "r" using command down'])
        restart_event.clear()

if __name__ == "__main__":
    restart_event = Event()

    while True:
        stop_event = Event()

        server_thread = Thread(target=run_server, args=(stop_event,))
        server_thread.start()

        watch_file('index.html', restart_event)

        stop_event.set()
        server_thread.join()

        restart_event.clear()
