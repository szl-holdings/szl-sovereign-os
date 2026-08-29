#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Hugging Face Space entry. Stdlib HTTP on 7860."""
from szl_os.serve import serve

if __name__ == "__main__":
    serve("0.0.0.0", 7860)
