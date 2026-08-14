# 📊 Evaluation Strategy & Metrics Specification

**Project:** Scaler AI PII Redaction Tool  
**Author:** Sudhir Singh — Scaler AI Labs (Environment Data Role)  
**Document Version:** v2.0  
**Date:** August 14, 2026  
**Repository:** [https://github.com/SudhirSir/PII-Redaction-Tool](https://github.com/SudhirSir/PII-Redaction-Tool)

---

## 1. Executive Summary

The **Scaler AI PII Redaction Tool** is an enterprise-grade pipeline designed to automatically detect, classify, and replace all Personally Identifiable Information (PII) within complex Microsoft Word `.docx` documents — such as Red Herring Prospectuses, legal filings, and financial disclosures — with semantically coherent, format-preserving synthetic replacements.

The system must satisfy two non-negotiable privacy guarantees:
1. **Zero original real PII leakage** in the output document (hard security constraint).
2. **Maximum PII coverage** without over-redacting non-PII content like legal/regulatory terms (quality constraint).

To measure and validate both guarantees, the system employs a **Dual Evaluation Strategy**: a controlled ground-truth benchmark evaluation and a real-document post-redaction residual audit.

---

## 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  SCALER AI PII REDACTION PIPELINE               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: Red Herring Prospectus.docx                             │
│         (1,006 paragraphs | 76 tables | 3,180 cells)           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           HYBRID PII DETECTION ENGINE                    │  │
│  │                                                          │  │
│  │  Layer 1: RegEx + Luhn + ipaddress validators            │  │
│  │           → EMAIL, PHONE, CREDIT_CARD, SSN, PAN, CIN    │  │
│  │                                                          │  │
│  │  Layer 2: spaCy en_core_web_sm (NER)                     │  │
│  │           → PERSON, ORGANIZATION                         │  │
│  │                                                          │  │
│  │  Layer 3: Contextual Prefix / Title Trigger Rules        │  │
│  │           → DATE_OF_BIRTH, ADDRESS                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         SYNTHETIC REPLACEMENT ENGINE (Faker)             │  │
│  │  - Deterministic MD5 hash-seeded replacement             │  │
│  │  - Category-aware substitutions (name→name, email→email) │  │
│  │  - Consistent cross-document entity mapping              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          ↓                                      │
│  OUTPUT: Red_Herring_Prospectus_Redacted.docx                   │
│          (run-level formatting fully preserved)                 │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         2-LAYER POST-REDACTION AUDIT ENGINE              │  │
│  │  Layer 1: Known-Source Regression Check (25 targets)     │  │
│  │  Layer 2: Whole-Entity Normalized Residual Audit          │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. PII Categories Detected

The pipeline detects and redacts **11 PII entity categories**:

| # | Category | Detection Method | Example Value | Synthetic Replacement Example |
|:---:|:---|:---|:---|:---|
| 1 | `PERSON` | spaCy NER + Known Name Patterns | `Prakash Boricha` | `James Carter` |
| 2 | `ORGANIZATION` | spaCy NER + Corp Suffix Regex | `KSH International Limited` | `Nexion Solutions LLC` |
| 3 | `EMAIL` | RegEx (RFC 5321 pattern) | `cs.connect@kshinternational.com` | `jane.doe@example.com` |
| 4 | `PHONE_NUMBER` | RegEx (India mobile + landline + intl.) | `+91 22 30752929` | `+91 98765 43210` |
| 5 | `ADDRESS` | Context-trigger prefix rules | `Plot No. 7, Pune` | `42 Oak Street, Mumbai` |
| 6 | `DATE_OF_BIRTH` | Strict birth-prefix context trigger | `12/08/1985` | `07/03/1990` |
| 7 | `SSN` | RegEx (`XXX-XX-XXXX` format) | `123-45-6789` | `987-65-4321` |
| 8 | `CREDIT_CARD` | RegEx + Luhn algorithm checksum | `4532 1234 5678 9010` | `5412 7534 5678 9012` |
| 9 | `IP_ADDRESS` | Python `ipaddress` module validation | `192.168.1.100` | `10.20.30.40` |
| 10 | `PAN` | Indian PAN format RegEx (`[A-Z]{5}[0-9]{4}[A-Z]`) | `ABCDE1234F` | `PQRST5678G` |
| 11 | `CIN` | Indian CIN format RegEx (21-char alphanumeric) | `U28129PN1979PLC141032` | `L17110MH2005PLC123456` |

---

## 4. Evaluation Strategy

### 4.1 Strategy 1 — Controlled Ground-Truth Benchmark

**Data Source:** `evaluation/test_cases.json`  
**Method:** The detection pipeline is run against 33 hand-curated test cases covering all 11 PII categories. Each test case includes:
- `input_text`: A realistic sentence or paragraph containing PII
- `expected_entities`: List of expected `{label, value}` detections
- `negative_examples`: Non-PII content expected NOT to be flagged (false-positive guards)

**Evaluation Mode:** Strict 1-to-1 exact-match span comparison (normalized text).

### 4.2 Strategy 2 — Real-Document Post-Redaction Residual Audit

**Data Source:** `output/Red_Herring_Prospectus_Redacted.docx`  
**Method:** After full document redaction, the output DOCX is re-scanned with the full `PIIDetectorPipeline`. Every detected span is classified using normalized tuple-key lookup:
- **`ORIGINAL_PII_LEAK`** — matched in original document inventory (critical fail condition)
- **`SYNTHETIC_REPLACEMENT`** — matched in Faker replacement cache (expected)
- **`NEW_OR_UNMATCHED_PII_LIKE`** — PII-shaped but unclassified (review)

---

## 5. Metric Definitions & Formulas

### 5.1 Precision

> Fraction of all flagged PII spans that are actual true PII. Guards against over-redaction.

$$\text{Precision} = \frac{TP}{TP + FP}$$

### 5.2 Recall

> Fraction of all ground-truth PII instances that were correctly detected. Guards against missed leaks.

$$\text{Recall} = \frac{TP}{TP + FN}$$

### 5.3 F1-Score

> Harmonic mean of Precision and Recall. Provides a single balanced quality measure.

$$F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

### 5.4 Accuracy

> Overall classification accuracy computed across all positive and negative benchmark instances.

$$\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}$$

### 5.5 Definitions

| Term | Definition |
|:---|:---|
| **TP (True Positive)** | Correctly flagged PII span that matches expected ground-truth entity |
| **FP (False Positive)** | Flagged span that is NOT actual PII (e.g., regulatory body flagged as PERSON) |
| **FN (False Negative)** | Actual PII span that was NOT detected by the pipeline |
| **TN (True Negative)** | Non-PII content correctly NOT flagged |

---

## 6. Benchmark Performance Results

Running `python src/evaluation.py` against `evaluation/test_cases.json`:

### 6.1 Overall Scores

| Metric | Score | Interpretation |
|:---|:---:|:---|
| **Precision** | **83.87%** | 26 of 31 flagged spans were true PII |
| **Recall** | **92.86%** | 26 of 28 ground-truth PII instances detected |
| **F1-Score** | **88.14%** | Strong harmonic balance of P & R |
| **Accuracy** | **82.05%** | 32/39 benchmark instances classified correctly |

### 6.2 Per-Category Breakdown

| PII Category | TP | FP | FN | Precision | Recall | F1-Score | Notes |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `PERSON` | 8 | 1 | 1 | 88.9% | 88.9% | 88.9% | 1 FP: regulatory entity misclassified |
| `EMAIL` | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | Perfect detection |
| `PHONE_NUMBER` | 5 | 2 | 0 | 71.4% | 100.0% | 83.3% | 2 FP: non-standard landline formats |
| `ORGANIZATION` | 1 | 1 | 0 | 50.0% | 100.0% | 66.7% | 1 FP: legal term flagged as ORG |
| `ADDRESS` | 2 | 1 | 1 | 66.7% | 66.7% | 66.7% | Context trigger boundary edge case |
| `SSN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Perfect detection |
| `CREDIT_CARD` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Luhn validation enforced |
| `DATE_OF_BIRTH` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Zero FP on general prospectus dates |
| `IP_ADDRESS` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | `ipaddress` module validation |
| `PAN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | India-specific regex |
| `CIN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | India-specific 21-char pattern |
| **TOTAL** | **26** | **5** | **2** | **83.87%** | **92.86%** | **88.14%** | |

---

## 7. Hybrid Detection Engine — Layer-by-Layer Details

### Layer 1: RegEx & Algorithmic Validators

| Sub-Detector | Pattern / Algorithm | Validates |
|:---|:---|:---|
| Email Detector | `[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}` | RFC 5321 format |
| Phone Detector | `(\+91[\s\-]?)?[6-9]\d{9}` + landline patterns | Indian mobile, international |
| Credit Card Detector | 13–19 digit groups + **Luhn checksum** | Prevents false positives on ID numbers |
| SSN Detector | `\d{3}-\d{2}-\d{4}` | US Social Security Number |
| IP Address Detector | Python `ipaddress.ip_address()` | Valid IPv4 octets only |
| PAN Detector | `[A-Z]{5}[0-9]{4}[A-Z]{1}` | Indian Permanent Account Number |
| CIN Detector | `[A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}` | Indian Corporate Identity Number |

### Layer 2: spaCy NER Model

- **Model:** `en_core_web_sm` (statistical NER, 12.8 MB)
- **Optimized Load:** `disable=["parser", "attribute_ruler", "lemmatizer"]` → 2–3× speedup
- **Targets:** `PERSON`, `ORGANIZATION`
- **Exclusion Guard:** Keyword set — `{SEBI, BSE, NSE, ROC, IPO, RHP, IRDAI, MCA, FSSAI, ...}` — prevents flagging of regulatory body names

### Layer 3: Contextual Prefix Rules

| Trigger Prefix | Entity Category | Example |
|:---|:---|:---|
| `Date of Birth:`, `DOB:`, `Born on:` | `DATE_OF_BIRTH` | `Date of Birth: 12/08/1985` |
| `Address:`, `Registered Office:` | `ADDRESS` | `Address: Plot 7, Pune` |
| `Contact Person:`, `Company Secretary:` | `PERSON` | `Contact Person: Prakash Boricha` |

---

## 8. Post-Redaction Residual Audit Results

### Layer 1: Known-Source Regression (25 Target PII Values)

All 25 specifically identified original PII values were verified ABSENT in the redacted output:

- **15 Named Persons**: Sarthak Malvadkar, Prakash Boricha, Hitesh Ramani, Chitra Raste, Manisha Shukla, Tushar Wakhele, Rajesh Kushal Hegde, Rakhi Girija Shetty, Kushal Subbayya Hegde, Pushpa Kushal Hegde, Rohit Kushal Hegde, Varun Badai, Cherag Gyara, Ashish Mathew Pulloor, Anand Soni
- **2 Organizations**: KSH INTERNATIONAL LIMITED, KSH International
- **2 Emails**: cs.connect@kshinternational.com, Sarthak.malvadkar@kshinterantional.com
- **5 Phone Numbers**: +91 22 30752929, +91 22 30752928, +91 22 30752914, +91 20 4505 3237, +91 81081 14949
- **1 CIN**: U28129PN1979PLC141032

**Result: ✅ PASS — 0 original target PII found in redacted output**

### Layer 2: Whole-Entity Normalized Audit

| Classification | Count | Meaning |
|:---|:---:|:---|
| `ORIGINAL_PII_LEAK` | **0** | ✅ ZERO real PII leaked — PASS |
| `SYNTHETIC_REPLACEMENT` | **932** | Expected Faker-generated replacements |
| `NEW_OR_UNMATCHED_PII_LIKE` | **980** | PII-shaped spans from document boilerplate |
| **TOTAL SCANNED SPANS** | **1,912** | Full residual scan of redacted output |

---

## 9. Document Traversal & Structural Integrity

| Attribute | Original Input | Redacted Output | Status |
|:---|:---:|:---:|:---:|
| Body Paragraphs | 1,006 | 1,006 | ✅ Preserved |
| Tables | 76 | 76 | ✅ Preserved |
| Unique Table Cells | 3,180 | 3,180 | ✅ Preserved |
| Header/Footer Sections | 3 | 3 | ✅ Preserved |
| Run-Level Formatting | — | — | ✅ Bold/Italic/Font preserved |
| Entity Consistency | — | — | ✅ Same PII → Same Synthetic value |

---

## 10. Known Limitations & Future Work

| Limitation | Impact | Mitigation |
|:---|:---|:---|
| spaCy `en_core_web_sm` misclassifies regulatory bodies | FP in ORGANIZATION | Exclusion keyword set applied |
| Non-standard landline formats | 2 FP in PHONE_NUMBER | Threshold tuning in progress |
| ADDRESS boundary detection | Occasional boundary truncation | Sliding-window context expansion planned |
| Handwritten/scanned PDFs | Not supported | Out of scope (DOCX-only) |
| Multi-language documents | English-only NER | Multilingual spaCy model for v2 |

---

*Document auto-generated and maintained by Scaler AI Labs.*  
*Evaluation pipeline: `src/evaluation.py` | Test suite: `evaluation/test_cases.json`*
