import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import seqlog
    print("SUCCESS: seqlog imported")
    print(f"seqlog file: {seqlog.__file__}")
except ImportError as e:
    print(f"FAILURE: {e}")
except Exception as e:
    print(f"FAILURE (Other): {e}")
