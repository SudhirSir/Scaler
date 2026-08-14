# Evaluation Strategy & Metrics Specification

**Project:** Scaler AI PII Redaction Tool  
**Author:** Sudhir Singh (Environment Data Role - Scaler AI Labs)  
**Document Date:** August 14, 2026  

---

## 1. Executive Summary & Purpose

The **Scaler AI PII Redaction Tool** is designed to automatically detect, redact, and replace confidential Personally Identifiable Information (PII) within complex enterprise Word documents (`.docx`), such as Red Herring Prospectuses, financial filings, and legal records.

To guarantee zero real-PII leaks while preserving document readability and format structure, the system uses a **Hybrid Detection Architecture** coupled with a **Two-Layer Post-Redaction Residual Audit Engine**.

---

## 2. Evaluation Strategy & Metric Formulas

The pipeline is evaluated using a dual strategy:
1. **Controlled Ground-Truth Benchmark Evaluation**: Evaluated against an authoritative ground-truth dataset (`evaluation/test_cases.json`).
2. **Real-Document Post-Redaction Residual Audit**: Evaluated directly on the generated output document (`output/Red_Herring_Prospectus_Redacted.docx`).

### Quantitative Metric Definitions & Mathematical Formulas

#### A. Precision (\( P \))
The proportion of flagged PII spans that were true PII instances. High precision ensures non-PII terms (such as legal jargon or corporate names) are not unnecessarily redacted.
\[
\text{Precision} = \frac{TP}{TP + FP}
\]

#### B. Recall (\( R \))
The proportion of actual ground-truth PII instances correctly flagged by the engine. High recall is critical in privacy compliance to prevent confidential data leaks.
\[
\text{Recall} = \frac{TP}{TP + FN}
\]

#### C. F1-Score (\( F_1 \))
The harmonic mean of Precision and Recall, providing a balanced metric of overall detection capability.
\[
F_1 = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}
\]

#### D. Accuracy (\( A \))
The overall classification accuracy computed across positive PII spans and negative non-PII candidates in the benchmark suite.
\[
\text{Accuracy} = \frac{TP + TN}{TP + TN + FP + FN}
\]

---

## 3. Hybrid PII Detection Engine Architecture

The detection engine combines three complementary layers to achieve high precision and high recall:

| Layer | Engine / Model | Target PII Categories | Precision Guard & Validation |
| :--- | :--- | :--- | :--- |
| **Layer 1: RegEx & Algorithmic** | Deterministic RegEx + Python `ipaddress` & Luhn Algorithm | `EMAIL`, `PHONE_NUMBER`, `CREDIT_CARD`, `SSN`, `IP_ADDRESS`, `PAN`, `CIN` | Luhn Checksum validation for credit cards; IPv4 octet validation; Indian landline & adjacent mobile regex |
| **Layer 2: spaCy NER** | spaCy `en_core_web_sm` Statistical NER | `PERSON`, `ORGANIZATION` | Exclusion keyword set (`SEBI`, `BSE`, `ROC`, `IPO`, `RHP`) to filter regulatory false positives |
| **Layer 3: Contextual Rules** | Title Context & Trigger Prefixes | `DATE_OF_BIRTH`, `ADDRESS`, Role Names | Strict birth prefix context (`Date of Birth:`, `Born on:`) to prevent redacting prospectus dates |

---

## 4. Benchmark Performance Scores

Running `python src/evaluation.py` against `evaluation/test_cases.json` yields the following performance scores:

- **Overall Precision**: **83.87%**
- **Overall Recall**: **92.86%**
- **Overall F1-Score**: **88.14%**
- **Overall Accuracy**: **82.05%**

### Category-Level Benchmark Breakdown

| Category | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Precision | Recall | F1-Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `PERSON` | 8 | 1 | 1 | 88.9% | 88.9% | 88.9% |
| `EMAIL` | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `PHONE_NUMBER` | 5 | 2 | 0 | 71.4% | 100.0% | 83.3% |
| `ORGANIZATION` | 1 | 1 | 0 | 50.0% | 100.0% | 66.7% |
| `ADDRESS` | 2 | 1 | 1 | 66.7% | 66.7% | 66.7% |
| `SSN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `CREDIT_CARD` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `DATE_OF_BIRTH` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `IP_ADDRESS` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `PAN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| `CIN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% |
| **TOTAL** | **26** | **5** | **2** | **83.87%** | **92.86%** | **88.14%** |

---

## 5. Post-Redaction Residual Audit Strategy

To verify document sanitization on the full Red Herring Prospectus (`1,006` body paragraphs, `76` tables, `3,180` cells), a **Two-Layer Residual Audit** is performed on the output `.docx` file:

### Layer 1: Known-Source PII Regression Check
- Validates 25 target original PII values (`Sarthak Malvadkar`, `Prakash Boricha`, `cs.connect@kshinternational.com`, `+91 22 30752929`, `U28129PN1979PLC141032`, etc.).
- **Result**: **PASS (0 Target Source PII Remaining)**

### Layer 2: Whole-Entity Normalized Residual Audit
- Scans every detected entity on the output document and categorizes it using exact normalized tuple keys `(label, normalized_value)`:
  1. `ORIGINAL_PII_LEAK`: Matches key in original input document inventory. **(MUST BE 0 FOR PASS)**
  2. `SYNTHETIC_REPLACEMENT`: Matches synthetic replacement generated by `Faker`.
  3. `NEW_OR_UNMATCHED_PII_LIKE`: PII-shaped output span not in original inventory and not in replacement cache.

---

## 6. Output Document Preservation

- **File Location**: [`output/Red_Herring_Prospectus_Redacted.docx`](file:///d:/Downloads/Scaler/output/Red_Herring_Prospectus_Redacted.docx)
- **Formatting Preservation**: Preserves run-level font styles, bolding, italics, table cell structure, and headers/footers.
- **Entity Consistency**: All occurrences of the same real PII entity (e.g. `Prakash Boricha`) are deterministically mapped to the exact same synthetic replacement across all paragraphs and tables.
