<div align="center">

<img src="https://img.icons8.com/isometric-headers/100/security-shield.png" width="80"/>

# 🛡️ Scaler AI PII Redaction Tool

### Automated PII Detection, Redaction & Residual Audit for Enterprise Documents

[![Live App](https://img.shields.io/badge/🚀%20Live%20Demo-piiredaction.streamlit.app-6366f1?style=for-the-badge&logo=streamlit&logoColor=white)](https://piiredaction.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![spaCy](https://img.shields.io/badge/spaCy-NER-09A3D5?style=for-the-badge)](https://spacy.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)

**Author:** Sudhir Singh &nbsp;|&nbsp; **Role:** Environment Data — Scaler AI Labs &nbsp;|&nbsp; **Date:** August 14, 2026

> 🔗 **Live App:** [https://piiredaction.streamlit.app/](https://piiredaction.streamlit.app/)

</div>

---

## 📌 Problem Statement

Financial and legal documents like **Red Herring Prospectuses** contain highly sensitive Personally Identifiable Information (PII) — names, emails, phone numbers, corporate registration numbers, and addresses. Manually redacting such documents is slow, error-prone, and non-reproducible at scale.

This tool provides a fully automated pipeline that detects, redacts, and replaces all PII in `.docx` documents with format-preserving synthetic alternatives — while preserving the original document structure (fonts, tables, headers, footers, bold/italic formatting) with zero data leakage.

---

## 🔍 Approach

The tool implements a **three-layer Hybrid Detection Architecture** — combining deterministic algorithms, statistical NER, and contextual rules — to achieve high recall across 11 PII categories while minimising false positives.

### Layer 1 — RegEx + Algorithmic Validators (Structured PII)

Deterministic, pattern-based detection for structured entities where the format is well-defined:

| Entity | Method | Validation |
|:---|:---|:---|
| `EMAIL` | RFC 5321 RegEx | Standard email format |
| `PHONE_NUMBER` | Multi-pattern RegEx | Indian mobile (`+91 XXXXX XXXXX`), landlines, international |
| `CREDIT_CARD` | RegEx (13–19 digits) | **Luhn checksum algorithm** eliminates false positives |
| `SSN` | RegEx `\d{3}-\d{2}-\d{4}` | US Social Security format |
| `IP_ADDRESS` | Python `ipaddress.ip_address()` | Validates all four IPv4 octets |
| `PAN` | `[A-Z]{5}[0-9]{4}[A-Z]` | Indian Permanent Account Number |
| `CIN` | 21-char alphanumeric pattern | Indian Corporate Identity Number |

### Layer 2 — spaCy Named Entity Recognition (Unstructured PII)

Statistical NER using `en_core_web_sm` detects free-form named entities:
- `PERSON` — individual full names
- `ORGANIZATION` — company names with corporate suffix validation

**Precision guard:** An exclusion keyword set (`SEBI`, `BSE`, `ROC`, `IRDAI`, `IPO`, etc.) prevents regulatory body names from being misclassified as personal entities.

### Layer 3 — Contextual Prefix Trigger Rules (Ambiguous PII)

Certain entities are only PII in specific contexts. Strict trigger prefixes prevent over-redaction:
- **`DATE_OF_BIRTH`** fires only when preceded by `Date of Birth:`, `DOB:`, `Born on:` — never on general prospectus event dates
- **`ADDRESS`** fires on explicit indicators like `Registered Office:`, `Address:`, followed by PIN codes or street patterns
- **`PERSON`** (role-based) fires after `Contact Person:`, `Managing Director:`, `Company Secretary:`, `Auditor:`

### Synthetic Replacement Engine

All detected PII is replaced with **deterministic, category-aware Faker values** seeded using an MD5 hash of the original entity text. This ensures:
1. **Consistency** — the same name (`Prakash Boricha`) maps to the same synthetic value (`James Carter`) throughout all paragraphs, tables, and headers
2. **Format-preservation** — names replaced with names, emails with emails, phone numbers with phone numbers
3. **Readability** — the redacted document reads naturally without `[REDACTED]` artifacts

### DOCX Run-Level Processing

`DocxProcessor` operates at the **run level** rather than paragraph level:
- All runs in a paragraph are concatenated to detect cross-run entities (e.g., bold name split across `Run 1: "Rajesh "` + `Run 2: "Kushal Hegde"`)
- Replacement is mapped back to individual run character offsets
- Font, bold, italic, size, and color are fully preserved after substitution

---

## ⚖️ Tradeoffs

| Design Decision | Tradeoff Made | Rationale |
|:---|:---|:---|
| **High Recall over Precision** | Accept some false positives | Missing real PII is a critical security breach; over-redacting boilerplate is a minor quality issue |
| **spaCy `en_core_web_sm`** (small model) | Lower accuracy vs. `en_core_web_lg` | Faster load, deployable on Streamlit Cloud free tier; satisfactory 88.9% F1 on PERSON |
| **Exact normalized matching in audit** | Avoids substring false leak classification | Prevents synthetic values from being misclassified as "leaks" due to partial overlap with boilerplate |
| **Faker replacement over `[REDACTED]`** | Output harder to audit visually | Preserves document readability and realistic structure for downstream review |
| **Context-trigger guards for DOB/Address** | May miss some occurrences without trigger prefix | Prevents redacting thousands of valid prospectus dates and location references |

---

## ⚠️ Observed False Positives & False Negatives

### False Positives (FP = 5 total)

| Category | Example | Root Cause |
|:---|:---|:---|
| `PHONE_NUMBER` | Prospectus serial number in `XX-XX-XXXX` format | Pattern overlaps with phone regex |
| `ORGANIZATION` | `"Securities and Exchange Board of India"` | spaCy ORG classifier; partially mitigated by exclusion set |
| `ADDRESS` | Partial address trigger on city-only references | Context window boundary too narrow |

### False Negatives (FN = 2 total)

| Category | Example | Root Cause |
|:---|:---|:---|
| `PERSON` | Name in ALL-CAPS tabular header without context | spaCy NER misses ALL-CAPS tokens without sentence context |
| `ADDRESS` | Multi-line address split across table cells | Cell-level processing doesn't join adjacent cells |

---

## 📊 Key Results

| Metric | Score |
|:---|:---:|
| **Precision** | **83.87%** |
| **Recall** | **92.86%** |
| **F1-Score** | **88.14%** |
| **Accuracy** | **82.05%** |
| **Original PII Leaks in Output** | **0** |
| **Known-Source Regression** | **✅ PASS** |

> Full evaluation: [`EVALUATION.md`](./EVALUATION.md) | Full audit report: [`evaluation/evaluation_report.md`](./evaluation/evaluation_report.md)

---

## 📂 Project Structure

```
Scaler/
├── app.py                               # Streamlit web application
├── pii_redactor.py                      # CLI entry point
├── requirements.txt                     # Python dependencies
├── runtime.txt                          # Streamlit Cloud Python 3.11 pin
├── EVALUATION.md                        # Full evaluation strategy & metric specification
├── README.md                            # This file
│
├── src/
│   ├── detectors.py                     # Hybrid detection engine (all 3 layers)
│   ├── replacement.py                   # Deterministic Faker replacement engine
│   ├── docx_processor.py                # Run-level DOCX traversal & redaction
│   └── evaluation.py                    # Benchmark evaluator & 2-layer residual audit
│
├── input/
│   └── Red Herring Prospectus.docx      # Source document
│
├── output/
│   └── Red_Herring_Prospectus_Redacted.docx   # ✅ Sanitized output
│
└── evaluation/
    ├── test_cases.json                  # Ground-truth benchmark (33 test cases)
    └── evaluation_report.md             # Full evaluation & audit report
```

---

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Streamlit web app
streamlit run app.py

# CLI: Redact document
python pii_redactor.py --input "input/Red Herring Prospectus.docx" \
                       --output "output/Red_Herring_Prospectus_Redacted.docx"

# Run benchmark evaluation & audit
python src/evaluation.py
```

---

## 🔗 Links

| | |
|:---|:---|
| 🌐 **Live App** | [https://piiredaction.streamlit.app/](https://piiredaction.streamlit.app/) |
| 📦 **Repository** | [https://github.com/SudhirSir/PII-Redaction-Tool](https://github.com/SudhirSir/PII-Redaction-Tool) |
| 📊 **Evaluation Strategy** | [`EVALUATION.md`](./EVALUATION.md) |
| 📋 **Audit Report** | [`evaluation/evaluation_report.md`](./evaluation/evaluation_report.md) |
| 📄 **Redacted Output** | [`output/Red_Herring_Prospectus_Redacted.docx`](./output/Red_Herring_Prospectus_Redacted.docx) |

---

<div align="center">

**Built with ❤️ by Sudhir Singh — Scaler AI Labs**

[![Live App](https://img.shields.io/badge/🚀%20Try%20Live%20App-piiredaction.streamlit.app-6366f1?style=for-the-badge)](https://piiredaction.streamlit.app/)

</div>
