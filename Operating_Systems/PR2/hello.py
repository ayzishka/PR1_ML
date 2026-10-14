
#!/usr/bin/env python3

import os
import sys

if len(sys.argv) != 2:
    print("Usage: python3 hello.py <file>")
    sys.exit(1)

file_path = sys.argv[1]

try:
    with open(file_path, "rb") as file:
        content = file.read()

    print(f"File size: {len(content)} bytes")

except OSError as error:
    print(f"Error: {error}", file=sys.stderr)
    sys.exit(1)
