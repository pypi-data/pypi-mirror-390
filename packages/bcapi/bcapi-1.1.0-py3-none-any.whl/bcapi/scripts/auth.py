#! /usr/bin/env python

import json

from bcapi.client import Client
import sys

def main(verification_code=None):
    
    with Client(verification_code=verification_code or "bc91ffdf"):
        print("done")


if __name__ == "__main__":
    verification_code = sys.argv[1] if len(sys.argv) > 1 else None
    print(f"verification_code !!!!!: {verification_code}")
    main(verification_code)
