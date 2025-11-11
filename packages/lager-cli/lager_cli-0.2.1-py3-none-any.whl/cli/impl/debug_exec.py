#!/usr/bin/env python3
"""
Debug script to see the actual execution environment
"""
import sys
import os
import json

def main():
    result = {
        "sys_argv": sys.argv,
        "working_dir": os.getcwd(),
        "python_path": sys.path[:3],  # First 3 entries
        "env_vars": {k: v for k, v in os.environ.items() if 'LAGER' in k or 'PYTHON' in k}
    }
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()