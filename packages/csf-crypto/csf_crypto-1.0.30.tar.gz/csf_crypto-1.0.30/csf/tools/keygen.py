#!/usr/bin/env python3
"""
Key generation utility.

Generates cryptographic keys for CSF.
"""

import sys
import argparse
from csf.core.keys import KeyManager
from csf.utils.encoding import encode_base64


def main():
    parser = argparse.ArgumentParser(description="Generate CSF cryptographic keys")
    parser.add_argument(
        "--scheme",
        default="Kyber768",
        choices=["Kyber512", "Kyber768", "Kyber1024"],
        help="PQC scheme to use",
    )
    parser.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")

    args = parser.parse_args()

    # Generate keys
    key_manager = KeyManager(args.scheme)
    public_key, private_key = key_manager.generate_key_pair()

    # Format output
    output = f"""CSF Key Pair
Scheme: {args.scheme}
Public Key (base64): {encode_base64(public_key)}
Private Key (base64): {encode_base64(private_key)}

WARNING: Keep private key secure and secret!
"""

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Keys saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
