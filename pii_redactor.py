#!/usr/bin/env python3
"""
Root Entry Point for PII Redaction Tool
Author: Sudhir Singh
"""

import sys
import os

# Redirect execution to src/pii_redactor.py
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_dir)

from pii_redactor import main

if __name__ == "__main__":
    main()
