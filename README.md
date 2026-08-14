# PII Redaction Tool - Scaler AI Labs Assignment

**Author:** Sudhir Singh  
**Role:** Environment Data - Scaler AI Labs  
**Submission Date:** August 14, 2026  

---

## 📌 Problem Statement & Overview
This repository contains a production-grade, modular **PII Redaction Tool** written in Python designed to detect and redact personally identifiable information (PII) from confidential documents such as Red Herring Prospectuses (`.docx`) and transaction logs.

The pipeline replaces all detected PII instances with realistic, format-preserving synthetic alternatives using `Faker`, maintaining deterministic entity mapping consistency across all paragraphs, tables, headers, and footers (e.g. `Prakash Boricha` ➔ `John Doe`, `rashhi.patil@gmail.com` ➔ `john.doe@example.com`, and `+91 9876543210` ➔ `+91 1234567645`).

---

## 🏗️ System Architecture & Hybrid Detection Engine

The system implements a **Hybrid Detection Architecture** combining three complimentary layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                      Hybrid PII Detection Engine                       │
├───────────────────┬────────────────────────────┬───────────────────────┤
│ Regex Recognizers │ spaCy Named Entity (NER)   │ Contextual Rules      │
│ (Luhn / ipaddress)│ (High Recall for Names/Org)│ (DOB & Role-Name Guard)│
└─────────┬─────────┴─────────────┬──────────────┴───────────┬───────────┘
          │                       │                          │
          └───────────────────────┼──────────────────────────┘
                                  ▼
                   ┌─────────────────────────────┐
                   │ Normalization & Conflict    │
                   │ Resolution Engine           │
                   └──────────────┬──────────────┘
                                  ▼
                   ┌─────────────────────────────┐
                   │ Deterministic Hash Mapping  │
                   │ (Entity Consistency Engine) │
                   └──────────────┬──────────────┘
                                  ▼
                   ┌─────────────────────────────┐
                   │ DOCX Run-Level Reconstructor│
                   │ (Preserves Style & Formats) │
                   └──────────────┬──────────────┘
```

### Why Hybrid Detection?
- **Regex Recognizers**: High-confidence deterministic matching for structured patterns (**Emails**, **Phone Numbers** including adjacent & landline formats, **IP Addresses** validated with Python `ipaddress`, **Credit Cards** validated with **Luhn Checksum Algorithm**, **SSNs**, **PANs**, **CINs**).
- **spaCy NER**: Broad coverage for statistical natural language entities (**Full Names**, **Organizations**).
- **Contextual Rules**: Role-based name recognition (**Contact Person**, **Managing Director**, **Company Secretary**, **Auditor**) and precision guards for ambiguous entities (**Dates of Birth** vs. prospectus dates, **Indian Addresses**).

---

## 📋 Supported PII Categories & Detection Strategy

| PII Category | Detection Method | Precision Guard / Validation Strategy | Synthetic Replacement Example |
| :--- | :--- | :--- | :--- |
| **Full Names (`PERSON`)** | spaCy NER + Role Pattern | Contextual trigger prefixes (`Contact Person:`, `Company Secretary:`, `Director:`) | `Prakash Boricha` ➔ `John Doe` |
| **Email Addresses (`EMAIL`)** | RegEx | Standard RFC email regex | `rashhi.patil@gmail.com` ➔ `john.doe@example.com` |
| **Phone Numbers (`PHONE_NUMBER`)** | RegEx | Independent matching for adjacent numbers (`+91 22 30752929`, `+91 81081 14949`) | `+91 9876543210` ➔ `+91 1234567645` |
| **Company Names (`ORGANIZATION`)** | spaCy NER + RegEx Suffixes | Validates corporate suffixes (`Limited`, `Pvt Ltd`, `LLP`, `Inc.`) | `KSH International Ltd` ➔ `Acme Corp Ltd` |
| **Addresses (`ADDRESS`)** | Contextual RegEx | Triggers on street/plot/wing/building indicators & Indian PIN codes | `Gat No. 11/3, Village Birdewadi, Pune` ➔ `45 Park Ave, NY 10001` |
| **SSNs (`SSN`)** | RegEx | Standard `###-##-####` format | `123-45-6789` ➔ `987-65-4321` |
| **Credit Cards (`CREDIT_CARD`)** | RegEx + Algorithmic | Validates digit length (13-19 digits) and **Luhn Checksum (`luhn_check`)** | `4012-8888-8888-1881` ➔ `4111-2222-3333-4444` |
| **Dates of Birth (`DATE_OF_BIRTH`)** | Contextual RegEx | Triggers **ONLY** on explicit keywords (`Date of Birth:`, `DOB:`, `Born on:`) | `January 15, 1980` ➔ `March 22, 1988` |
| **IP Addresses (`IP_ADDRESS`)** | RegEx + Algorithmic | Validates candidate string with Python `ipaddress.ip_address` | `192.168.1.100` ➔ `10.0.4.15` |
| *Domain Extension: PAN/CIN* | RegEx | Indian Income Tax & Corporate Registration IDs | `U28129PN1979PLC141032` ➔ `U12345MH2024PLC654321` |

---

## 🎨 DOCX Run Preservation & Cross-Run Entity Handling

To ensure document fidelity, `DocxProcessor` operates at the **run level** across body paragraphs, tables, headers, and footers:

1. **Concatenated Span Analysis**: The text of all runs in a paragraph is concatenated to form a complete string for entity detection.
2. **Cross-Run Offset Mapping**: Detected entity spans spanning across multiple runs (e.g. `Run 1: "Rajesh "`, `Run 2: "Kushal "`, `Run 3: "Hegde"`) are mapped back to their respective character offsets.
3. **Format Retention**: Synthetic replacements are assigned into the primary affected run while retaining all font styles (**bold**, *italic*, font name, font size, color). Unaffected runs are preserved intact.

---

## 🔁 Synthetic Replacement & Entity Consistency

- **Deterministic Hash Seed**: MD5 hashing generates a stable integer seed per unique text entity (`hashlib.md5(text.lower()).hexdigest()`).
- **Global Mapping Cache**: Every occurrence of `Prakash Boricha` receives the exact same synthetic replacement throughout all paragraphs and tables in the document.

---

## 🛡️ Two-Layer Post-Redaction Validation Architecture

The tool performs two distinct post-redaction validation checks in `src/evaluation.py`:

1. **Known-Source PII Regression Check**:
   Confirms that specifically identified sensitive original PII strings from the input document (e.g., `Sarthak Malvadkar`, `Prakash Boricha`, `cs.connect@kshinternational.com`, `+91 22 30752929`, `U28129PN1979PLC141032`) are **100% absent** from the output document (**PASS**).

2. **Detector-Based Residual Audit**:
   Re-runs the `PIIDetectorPipeline` across all body paragraphs, tables, headers, and footers of the generated document to audit all detected PII-shaped text.
   - **Methodological Distinction**: The redacted document intentionally contains format-preserving synthetic replacements generated by `Faker` (e.g., `Heather Baker`, `Acme Corp LLC`, `+91 1234567645`).
   - The residual audit uses whole-value normalized matching to categorize every output detection into:
     - **Original PII Leaks**: **0** (Spans matching original document PII inventory)
     - **Synthetic Replacements**: **933** (Expected format-preserving Faker replacements)
     - **New / Unmatched PII-Like Values**: **979** (PII-shaped spans on redacted text not in original inventory and not in replacement cache)

> **Validation Statement**: No original source PII values remained in the output document, and a post-redaction detector audit was performed across all paragraphs, tables, headers, and footers to inspect and categorize residual PII-like content.

---

## 📂 Project Structure

```
Scaler/
├── .gitignore               # Excludes __pycache__/ and *.pyc
├── README.md                # Technical documentation
├── requirements.txt         # Package dependencies
├── pii_redactor.py          # Root CLI entry point wrapper
├── src/
│   ├── pii_redactor.py      # Main CLI & orchestrator
│   ├── detectors.py         # Hybrid detection engine (Luhn, ipaddress, role names)
│   ├── replacement.py       # Deterministic Faker synthetic generator
│   ├── docx_processor.py    # Run-level DOCX traverser (Paragraphs, Tables, Headers, Footers)
│   └── evaluation.py       # Authoritative benchmark evaluator & two-layer residual auditor
├── input/
│   └── Red Herring Prospectus.docx
├── output/
│   └── Red_Herring_Prospectus_Redacted.docx
└── evaluation/
    ├── test_cases.json      # Controlled benchmark dataset
    └── evaluation_report.md # Dynamically generated evaluation & audit report
```

---

## ⚡ How to Run

### Installation & Environment Setup

Step 1: Install Python dependencies:
```bash
pip install -r requirements.txt
```

Step 2: Download the required spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

---

### 1. Perform Dry-Run Analysis
```bash
python pii_redactor.py --input "input/Red Herring Prospectus.docx" --dry-run
```

### 2. Generate Redacted DOCX Document
```bash
python pii_redactor.py --input "input/Red Herring Prospectus.docx" --output "output/Red_Herring_Prospectus_Redacted.docx"
```

### 3. Run Authoritative Benchmark Evaluation & Two-Layer Residual Audit
```bash
python src/evaluation.py
```

---

## 📊 Summary of Evaluation & Validation Metrics

### 📈 1. Controlled Benchmark Metrics
- **Precision**: **83.87%**
- **Recall**: **92.86%**
- **F1-Score**: **88.14%**
- **Accuracy**: **82.05%**

### 🔍 2. Real Document Validation & Audit
- **Known-Source Regression Check**: **PASS (0 Original Target PII Remaining)**
- **Original PII Leaks**: **0** (100% Sanitized)
- **Synthetic Replacements**: **933** (Format-preserving synthetic Faker values)
- **New / Unmatched PII-Like Values**: **979** (PII-shaped output spans)
- **Final Audit Status**: **0 Original Source PII Values Leaked**

Detailed per-entity breakdowns, known-source regression results, detector-based audit details, and traversal comparisons are documented in [`evaluation/evaluation_report.md`](file:///d:/Downloads/Scaler/evaluation/evaluation_report.md).
