"""
Main PII Redactor CLI Script
Author: Sudhir Singh
Description: Command-Line Interface for PII Redaction Tool supporting document redaction and dry-run modes.
"""

import sys
import os
import argparse

# Add src folder to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detectors import PIIDetectorPipeline
from replacement import SyntheticReplacer
from docx_processor import DocxProcessor

def main():
    parser = argparse.ArgumentParser(description="PII Redaction Tool - Scaler AI Labs Assignment")
    parser.add_argument(
        "--input", "-i",
        default=os.path.join("input", "Red Herring Prospectus.docx"),
        help="Path to input .docx document"
    )
    parser.add_argument(
        "--output", "-o",
        default=os.path.join("output", "Red_Herring_Prospectus_Redacted.docx"),
        help="Path to output redacted .docx document"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Perform dry-run entity count analysis without saving output file"
    )

    args = parser.parse_args()

    # Resolve relative paths relative to working directory or project root
    if not os.path.exists(args.input) and os.path.exists(os.path.join("input", "Red Herring Prospectus.docx")):
        args.input = os.path.join("input", "Red Herring Prospectus.docx")

    if not os.path.exists(args.input):
        print(f"Error: Input document '{args.input}' not found.")
        sys.exit(1)

    pipeline = PIIDetectorPipeline()
    replacer = SyntheticReplacer(seed=42)
    processor = DocxProcessor(pipeline, replacer)

    if args.dry_run:
        print("\n================ DRY-RUN PII ENTITY SUMMARY ================")
        counts = processor.dry_run(args.input)
        for label, count in counts.items():
            print(f"  {label:<15} {count}")
        print("============================================================\n")
    else:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        stats = processor.redact_document(args.input, args.output)
        print("\n================ REDACTION COMPLETE ================")
        print(f"Paragraphs Processed: {stats['paragraphs_processed']}")
        print(f"Tables Processed:     {stats['tables_processed']}")
        print(f"Cells Processed:      {stats['cells_processed']}")
        print(f"Total PII Redactions: {stats['total_redactions']}")
        print("\nRedactions by Category:")
        for label, count in stats["redactions_by_type"].items():
            print(f"  - {label:<15}: {count}")
        print(f"\nSaved redacted DOCX to: {args.output}")
        print("====================================================\n")

if __name__ == "__main__":
    main()
