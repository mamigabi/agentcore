import subprocess
import time
import os
import requests

def run_server():
    print("Starting server...")
    server_proc = subprocess.Popen(["python", "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return server_proc

def test_server():
    print("Waiting for server to start...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print("Server is up!")
                return True
        except:
            pass
        time.sleep(2)
    print("Server failed to start after 20 seconds.")
    return False

if __name__ == "__main__":
    server = run_server()
    try:
        if test_server():
            print("Running test agent...")
            test_proc = subprocess.run(["python", "test_agent.py"], capture_output=True, text=True)
            print("Test Output:")
            print(test_proc.stdout)
            print("Test Errors:")
            print(test_proc.stderr)
        else:
            print("Skipping tests because server didn't start.")
    finally:
        print("Stopping server...")
        server.terminate()
