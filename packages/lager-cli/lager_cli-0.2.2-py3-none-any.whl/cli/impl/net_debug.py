#!/usr/bin/env python3
"""
Debug version of net.py to see what arguments are received
"""
import sys
import os

print(f"DEBUG: sys.argv = {sys.argv}", file=sys.stderr)
print(f"DEBUG: Number of args = {len(sys.argv)}", file=sys.stderr)
for i, arg in enumerate(sys.argv):
    print(f"DEBUG: arg[{i}] = {repr(arg)}", file=sys.stderr)

# Add the gateway python path to sys.path so we can import lager modules
sys.path.insert(0, '/app/gateway_python')

# Now import and run the net module's CLI
from lager.pcb.net import _cli

if __name__ == "__main__":
    _cli()