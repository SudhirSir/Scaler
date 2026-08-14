<div align="center">

<img src="https://img.icons8.com/isometric-headers/100/security-shield.png" width="80"/>

# 🛡️ Scaler AI PII Redaction Tool

### Enterprise-grade Automated PII Detection, Redaction & Residual Audit Engine

[![Live App](https://img.shields.io/badge/🚀%20Live%20Demo-piiredaction.streamlit.app-6366f1?style=for-the-badge&logo=streamlit&logoColor=white)](https://piiredaction.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![spaCy](https://img.shields.io/badge/spaCy-en__core__web__sm-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)](https://spacy.io)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

**Author:** Sudhir Singh &nbsp;|&nbsp; **Role:** Environment Data — Scaler AI Labs &nbsp;|&nbsp; **Date:** August 14, 2026

---

> 🔗 **[https://piiredaction.streamlit.app/](https://piiredaction.streamlit.app/)** — Try the live deployed application

</div>

---

## 📌 Problem Statement

Financial and legal documents like **Red Herring Prospectuses** contain highly sensitive personally identifiable information (PII) — including names, emails, phone numbers, corporate registration numbers, and addresses. Manually redacting such documents is error-prone, time-consuming, and non-reproducible.

The **Scaler AI PII Redaction Tool** is a production-grade, fully automated pipeline that:
- **Detects** 11 categories of PII using a hybrid multi-layer NLP engine
- **Replaces** all PII with semantically coherent, format-preserving synthetic alternatives
- **Validates** zero data leakage through a two-layer post-redaction residual audit
- **Preserves** complete document structure — fonts, tables, headers, footers, bold/italic formatting

---

## 🌐 Live Application

> ### 🚀 [https://piiredaction.streamlit.app/](https://piiredaction.streamlit.app/)

The Streamlit web app provides an interactive dashboard to:
- ✅ Upload any `.docx` document for PII redaction
- ✅ Select which PII categories to detect and redact
- ✅ Run dry-run analysis (detect-only, no modification)
- ✅ Download the sanitized redacted `.docx` file
- ✅ View live audit results, metric cards, and entity replacement mapping
- ✅ Explore per-paragraph and per-table redaction snippets

---

## 📊 Performance Metrics at a Glance

| Metric | Score | Description |
|:---|:---:|:---|
| **Precision** | **83.87%** | Fraction of flagged spans that are genuine PII |
| **Recall** | **92.86%** | Fraction of real PII correctly detected |
| **F1-Score** | **88.14%** | Harmonic mean of Precision & Recall |
| **Accuracy** | **82.05%** | Overall correct classification rate |
| **Original PII Leaks** | **0** | Zero real PII values in redacted output |
| **Known-Source Regression** | **✅ PASS** | All 25 target PII values verified absent |

> Full evaluation details: [`EVALUATION.md`](./EVALUATION.md) | Audit report: [`evaluation/evaluation_report.md`](./evaluation/evaluation_report.md)

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    SCALER AI PII REDACTION PIPELINE                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  📄 INPUT: Red Herring Prospectus.docx                                     │
│     (1,006 paragraphs | 76 tables | 3,180 cells | 3 header/footer sects)  │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                HYBRID PII DETECTION ENGINE                          │  │
│  │                                                                     │  │
│  │  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │  │
│  │  │  Layer 1: RegEx  │  │ Layer 2: spaCy   │  │ Layer 3: Context │  │  │
│  │  │  + Luhn + ipadr  │  │ en_core_web_sm   │  │ Prefix Triggers  │  │  │
│  │  │                  │  │ (NER)            │  │                  │  │  │
│  │  │ EMAIL            │  │ PERSON           │  │ DATE_OF_BIRTH    │  │  │
│  │  │ PHONE_NUMBER     │  │ ORGANIZATION     │  │ ADDRESS          │  │  │
│  │  │ CREDIT_CARD      │  │                  │  │ Role Names       │  │  │
│  │  │ SSN / PAN / CIN  │  │                  │  │                  │  │  │
│  │  │ IP_ADDRESS       │  │                  │  │                  │  │  │
│  │  └─────────────────┘  └──────────────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │           NORMALIZATION & CONFLICT RESOLUTION ENGINE                │  │
│  │           (span deduplication, priority resolution)                 │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │         SYNTHETIC REPLACEMENT ENGINE  (Faker + MD5 Seed)            │  │
│  │         Deterministic: same entity → same replacement everywhere    │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │        DOCX RUN-LEVEL RECONSTRUCTOR (DocxProcessor)                 │  │
│  │        Preserves bold, italic, font size, color, table structure    │  │
│  └──────────────────────────────────┬──────────────────────────────────┘  │
│                                     ▼                                      │
│  📄 OUTPUT: Red_Herring_Prospectus_Redacted.docx                           │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                2-LAYER POST-REDACTION AUDIT ENGINE                  │  │
│  │                                                                     │  │
│  │  Layer 1: Known-Source Regression Check (25 target PII values)      │  │
│  │  Layer 2: Whole-Entity Normalized Residual Audit (1,912 spans)       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Supported PII Categories

| # | Category | Detection Method | Example (Original → Synthetic) |
|:---:|:---|:---|:---|
| 1 | `PERSON` | spaCy NER + Known Name Patterns | `Prakash Boricha` → `James Carter` |
| 2 | `ORGANIZATION` | spaCy NER + Corporate Suffix Regex | `KSH International Ltd` → `Nexion Solutions LLC` |
| 3 | `EMAIL` | RegEx (RFC 5321) | `cs.connect@kshinternational.com` → `jane.doe@example.com` |
| 4 | `PHONE_NUMBER` | Multi-pattern RegEx (India + Intl.) | `+91 22 30752929` → `+91 98765 43210` |
| 5 | `ADDRESS` | Context-trigger prefix rules | `Plot No. 7, Pune` → `42 Oak Street, Mumbai` |
| 6 | `DATE_OF_BIRTH` | Strict birth-prefix context trigger only | `12/08/1985` → `07/03/1990` |
| 7 | `SSN` | RegEx (`XXX-XX-XXXX`) | `123-45-6789` → `987-65-4321` |
| 8 | `CREDIT_CARD` | RegEx + **Luhn Algorithm Checksum** | `4532 1234 5678 9010` → `5412 7534 5678 9012` |
| 9 | `IP_ADDRESS` | Python `ipaddress` module validation | `192.168.1.100` → `10.20.30.40` |
| 10 | `PAN` | India-specific RegEx `[A-Z]{5}[0-9]{4}[A-Z]` | `ABCDE1234F` → `PQRST5678G` |
| 11 | `CIN` | India-specific 21-char alphanumeric pattern | `U28129PN1979PLC141032` → `L17110MH2005PLC123456` |

---

## 🛡️ Two-Layer Post-Redaction Validation

### Layer 1 — Known-Source PII Regression Check
Verifies that **25 specifically identified** original PII strings are **100% absent** from the output document:

- ✅ **15 Named Persons** (Sarthak Malvadkar, Prakash Boricha, Hitesh Ramani, ...)
- ✅ **2 Organizations** (KSH International Limited, KSH International)
- ✅ **2 Emails** (cs.connect@kshinternational.com, ...)
- ✅ **5 Phone Numbers** (+91 22 30752929, +91 22 30752928, ...)
- ✅ **1 CIN** (U28129PN1979PLC141032)

**Result: ✅ PASS — 0/25 original values found in redacted output**

### Layer 2 — Whole-Entity Normalized Residual Audit
Re-scans the redacted document with the full detection pipeline and classifies every span:

| Classification | Count | Status |
|:---|:---:|:---:|
| `ORIGINAL_PII_LEAK` | **0** | ✅ PASS |
| `SYNTHETIC_REPLACEMENT` | 932 | ✅ Expected |
| `NEW_OR_UNMATCHED_PII_LIKE` | 980 | ⚠️ Review |

---

## 📂 Project Structure

```
Scaler/
├── 📄 app.py                        # Streamlit web application (main entry point)
├── 📄 pii_redactor.py               # CLI entry point wrapper
├── 📄 requirements.txt              # Python package dependencies
├── 📄 runtime.txt                   # Streamlit Cloud Python version pin (3.11)
├── 📄 EVALUATION.md                 # Full evaluation strategy & metrics spec
├── 📄 README.md                     # This file
│
├── 📁 src/
│   ├── detectors.py                 # Hybrid detection engine (RegEx + spaCy NER + Context)
│   ├── replacement.py               # Deterministic Faker synthetic replacement generator
│   ├── docx_processor.py            # Run-level DOCX traverser & redactor
│   └── evaluation.py               # Benchmark evaluator & 2-layer residual auditor
│
├── 📁 input/
│   └── Red Herring Prospectus.docx  # Source document (1,006 paragraphs, 76 tables)
│
├── 📁 output/
│   └── Red_Herring_Prospectus_Redacted.docx  # ✅ Final sanitized output
│
└── 📁 evaluation/
    ├── test_cases.json              # Ground-truth benchmark dataset (33 test cases)
    └── evaluation_report.md         # Auto-generated evaluation & audit report
```

---

## ⚡ Quick Start

### Prerequisites

```bash
# Python 3.11+ recommended
pip install -r requirements.txt
```

Dependencies: `python-docx`, `spacy`, `faker`, `streamlit`, `en_core_web_sm`

### 🌐 Launch Web App (Streamlit)

```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

### 🖥️ CLI — Redact Document

```bash
# Full redaction
python pii_redactor.py --input "input/Red Herring Prospectus.docx" --output "output/Red_Herring_Prospectus_Redacted.docx"

# Dry-run (detect only, no modification)
python pii_redactor.py --input "input/Red Herring Prospectus.docx" --dry-run
```

### 📊 Run Benchmark Evaluation & Audit

```bash
python src/evaluation.py
```

Outputs:
- Overall Precision / Recall / F1 / Accuracy
- Per-category TP/FP/FN breakdown
- Layer 1 known-source regression results
- Layer 2 residual audit classification counts

---

## 🎨 Key Technical Highlights

| Feature | Implementation |
|:---|:---|
| **Cross-run entity detection** | Concatenates all runs in a paragraph, maps spans back to individual run offsets |
| **Format preservation** | Bold, italic, font name/size/color preserved at run level during replacement |
| **Deterministic replacements** | MD5 hash of original entity text seeds Faker for consistent cross-document mapping |
| **spaCy optimization** | `parser`, `lemmatizer`, `attribute_ruler` disabled → 2–3× faster NER inference |
| **Single-pass inventory** | Original PII inventory collected during redaction pass — eliminates redundant 2nd document scan |
| **Luhn validation** | Credit card number validation using Luhn checksum algorithm — prevents false positives |
| **IPv4 validation** | Python `ipaddress.ip_address()` validates octets — prevents numeric ID false positives |
| **DOB context guard** | `DATE_OF_BIRTH` triggers ONLY on explicit prefix keywords — prevents redacting prospectus event dates |

---

## 📈 Evaluation Strategy

Two-strategy evaluation framework — full details in [`EVALUATION.md`](./EVALUATION.md):

1. **Controlled Ground-Truth Benchmark** — 33 test cases in `evaluation/test_cases.json` covering all 11 PII categories with positive examples and negative counter-examples.

2. **Real-Document Post-Redaction Residual Audit** — Full pipeline re-scan of the output DOCX to verify zero original PII leakage using exact normalized tuple-key matching.

---

## 📄 Documents & Reports

| Document | Description |
|:---|:---|
| [`EVALUATION.md`](./EVALUATION.md) | Full evaluation strategy, metric formulas, per-category tables, architecture layers, limitations |
| [`evaluation/evaluation_report.md`](./evaluation/evaluation_report.md) | Auto-generated benchmark results, audit tables, confusion matrix, tradeoff analysis |
| [`output/Red_Herring_Prospectus_Redacted.docx`](./output/Red_Herring_Prospectus_Redacted.docx) | ✅ Final sanitized output document |
| [`evaluation/test_cases.json`](./evaluation/test_cases.json) | Ground-truth benchmark dataset (33 test cases) |

---

## 🔗 Links

| | |
|:---|:---|
| 🌐 **Live App** | [https://piiredaction.streamlit.app/](https://piiredaction.streamlit.app/) |
| 📦 **Repository** | [https://github.com/SudhirSir/PII-Redaction-Tool](https://github.com/SudhirSir/PII-Redaction-Tool) |
| 📊 **Evaluation Doc** | [`EVALUATION.md`](./EVALUATION.md) |
| 📋 **Audit Report** | [`evaluation/evaluation_report.md`](./evaluation/evaluation_report.md) |

---

<div align="center">

**Built with ❤️ by Sudhir Singh — Scaler AI Labs**

[![Live App](https://img.shields.io/badge/🚀%20Try%20Live%20App-piiredaction.streamlit.app-6366f1?style=for-the-badge)](https://piiredaction.streamlit.app/)

</div>
