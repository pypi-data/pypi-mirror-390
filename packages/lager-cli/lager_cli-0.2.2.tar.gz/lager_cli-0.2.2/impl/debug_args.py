#!/usr/bin/env python3
"""
Debug script to see what arguments are being passed
"""
import sys
import json

def main():
    print(json.dumps({
        "sys_argv": sys.argv,
        "argc": len(sys.argv),
        "args": sys.argv[1:] if len(sys.argv) > 1 else []
    }))

if __name__ == "__main__":
    main()