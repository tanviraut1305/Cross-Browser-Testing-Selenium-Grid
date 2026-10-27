
import json
import time
import urllib.request
import sys

url = "http://localhost:4444/status"
deadline = time.time() + 120

while time.time() < deadline:
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("value", {}).get("ready"):
            print("Selenium Grid is ready!")
            sys.exit(0)

    except Exception:
        pass

    print("Waiting for Selenium Grid...")
    time.sleep(3)

print("ERROR: Selenium Grid did not become ready within 120 seconds.")
sys.exit(1)
