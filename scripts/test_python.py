import sys
import os

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

try:
    from rembg import remove
    print("rembg is installed")
except ImportError:
    print("rembg is not installed") 