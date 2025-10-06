import subprocess
import sys
import time

proc = subprocess.Popen(
    [sys.executable, "main.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
)

try:
    # Wait up to 12 seconds to capture startup output
    time.sleep(12)
    out, err = proc.communicate(timeout=1)
except subprocess.TimeoutExpired:
    proc.kill()
    out, err = proc.communicate()

print("--- STDOUT ---")
print(out[:2000])
print("--- STDERR (first 2000 chars) ---")
print(err[:2000])

# Exit with the subprocess return code if available
if proc.returncode is not None:
    sys.exit(proc.returncode)
else:
    sys.exit(0)
