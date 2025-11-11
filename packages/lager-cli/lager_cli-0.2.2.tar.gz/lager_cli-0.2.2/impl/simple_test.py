#!/usr/bin/env python3
"""
Simple test script to verify argument passing
"""
import sys
import json

def main():
    print(json.dumps({
        "script_name": __file__,
        "argv": sys.argv,
        "args": sys.argv[1:] if len(sys.argv) > 1 else []
    }))

if __name__ == "__main__":
    main()