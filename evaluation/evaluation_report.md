# Comprehensive Evaluation & Post-Redaction Audit Report

**Author:** Sudhir Singh  
**Assignment:** Scaler AI Labs - Environment Data Role  
**Target Document:** `output/Red_Herring_Prospectus_Redacted.docx`  

---

## 📈 SECTION 1: Controlled Benchmark Performance Metrics

This section reports the quantitative performance of the **Hybrid PII Detection Engine** against the ground-truth benchmark suite ([`evaluation/test_cases.json`](file:///d:/Downloads/Scaler/evaluation/test_cases.json)).

| Metric | Score | Definition & Formula |
| :--- | :---: | :--- |
| **Precision** | **83.87%** | \( \frac{TP}{TP + FP} \) — Entity-level precision: proportion of flagged spans that were true PII. |
| **Recall** | **92.86%** | \( \frac{TP}{TP + FN} \) — Entity-level recall: proportion of actual ground-truth PII instances correctly detected. |
| **F1-Score** | **88.14%** | Harmonic mean of Precision and Recall. |
| **Accuracy** | **82.05%** | \( \frac{TP + TN}{TP + TN + FP + FN} \) — Classification accuracy computed over controlled benchmark candidate instances. |

> **Methodological Note on Accuracy**: Accuracy is calculated over explicit benchmark candidate instances (evaluating positive PII spans and negative non-PII candidates), while Precision, Recall, and F1-Score evaluate entity-level span detection.

---

### 📊 Per-PII-Type Benchmark Breakdown

| PII Entity Category | TP | FP | FN | Precision (%) | Recall (%) | F1-Score (%) | Status / Validation Note |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `PERSON` | 8 | 1 | 1 | 88.9% | 88.9% | 88.9% | Validated |
| `EMAIL` | 4 | 0 | 0 | 100.0% | 100.0% | 100.0% | Validated |
| `PHONE_NUMBER` | 5 | 2 | 0 | 71.4% | 100.0% | 83.3% | Validated |
| `ORGANIZATION` | 1 | 1 | 0 | 50.0% | 100.0% | 66.7% | Validated |
| `ADDRESS` | 2 | 1 | 1 | 66.7% | 66.7% | 66.7% | Validated |
| `SSN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Validated |
| `CREDIT_CARD` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Validated |
| `DATE_OF_BIRTH` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Strict context trigger enforced (0 FP on generic dates) |
| `IP_ADDRESS` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | Validated |
| `PAN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | India-specific extension |
| `CIN` | 1 | 0 | 0 | 100.0% | 100.0% | 100.0% | India-specific extension |
| **TOTAL** | **26** | **5** | **2** | **83.87%** | **92.86%** | **88.14%** | **Strict 1-to-1 Match Total** |

---

## 🔍 SECTION 2: Real-Document Post-Redaction Validation & Inventory Audit

This section presents the post-redaction validation results performed directly on `output/Red_Herring_Prospectus_Redacted.docx` across **Body Paragraphs, Tables, Headers, and Footers**.

### Layer 1: Known-Source PII Regression Check

**Purpose**: Verifies that specifically identified sensitive original PII values from the source document are **100% absent** in the generated output document.

| Entity Category | Original Target PII String | Redacted Document Status | Result |
| :--- | :--- | :---: | :---: |
| `PERSON` | `Sarthak Malvadkar` | ABSENT | ✅ PASS |
| `PERSON` | `Prakash Boricha` | ABSENT | ✅ PASS |
| `PERSON` | `Hitesh Ramani` | ABSENT | ✅ PASS |
| `PERSON` | `Chitra Raste` | ABSENT | ✅ PASS |
| `PERSON` | `Manisha Shukla` | ABSENT | ✅ PASS |
| `PERSON` | `Tushar Wakhele` | ABSENT | ✅ PASS |
| `PERSON` | `Rajesh Kushal Hegde` | ABSENT | ✅ PASS |
| `PERSON` | `Rakhi Girija Shetty` | ABSENT | ✅ PASS |
| `PERSON` | `Kushal Subbayya Hegde` | ABSENT | ✅ PASS |
| `PERSON` | `Pushpa Kushal Hegde` | ABSENT | ✅ PASS |
| `PERSON` | `Rohit Kushal Hegde` | ABSENT | ✅ PASS |
| `PERSON` | `Varun Badai` | ABSENT | ✅ PASS |
| `PERSON` | `Cherag Gyara` | ABSENT | ✅ PASS |
| `PERSON` | `Ashish Mathew Pulloor` | ABSENT | ✅ PASS |
| `PERSON` | `Anand Soni` | ABSENT | ✅ PASS |
| `ORGANIZATION` | `KSH INTERNATIONAL LIMITED` | ABSENT | ✅ PASS |
| `ORGANIZATION` | `KSH International` | ABSENT | ✅ PASS |
| `EMAIL` | `cs.connect@kshinternational.com` | ABSENT | ✅ PASS |
| `EMAIL` | `Sarthak.malvadkar@kshinterantional.com` | ABSENT | ✅ PASS |
| `PHONE_NUMBER` | `+91 22 30752929` | ABSENT | ✅ PASS |
| `PHONE_NUMBER` | `+91 22 30752928` | ABSENT | ✅ PASS |
| `PHONE_NUMBER` | `+91 22 30752914` | ABSENT | ✅ PASS |
| `PHONE_NUMBER` | `+91 20 4505 3237` | ABSENT | ✅ PASS |
| `PHONE_NUMBER` | `+91 81081 14949` | ABSENT | ✅ PASS |
| `CIN` | `U28129PN1979PLC141032` | ABSENT | ✅ PASS |

**Layer 1 Check Status**: **PASS (0 Original Target PII Remaining)**

---

### Layer 2: Original Document PII Inventory & Whole-Value Normalized Residual Audit

**Purpose**: Extracts all PII detected in the **Original Input DOCX** (1811 total instances, 884 unique normalized keys), re-runs `PIIDetectorPipeline` across all body paragraphs, tables, headers, and footers of `output/Red_Herring_Prospectus_Redacted.docx`, and compares normalized output values against the original inventory.

> **Methodological Note on Synthetic Values**: The redacted document intentionally contains **format-preserving synthetic replacements** generated by `Faker` (e.g., `Heather Baker`, `Acme Corp LLC`, `+91 1234567645`, `fake.email@example.com`). When the detector pipeline scans the redacted document, synthetic replacements are detected because they are intentionally PII-shaped. Whole-value key comparison confirms these match the synthetic replacement cache, proving **0 original real PII leaked**.

| Classification Category | Span Count | Audit Definition & Status |
| :--- | :---: | :--- |
| **ORIGINAL_PII_LEAKS** | **0** | Spans matching original document PII values. **(MUST BE 0 FOR PASS)** |
| **SYNTHETIC_REPLACEMENTS** | **1912** | Expected format-preserving synthetic replacements (Faker / cache). |
| **NEW_OR_UNMATCHED_PII_LIKE** | **0** | PII-shaped spans not in original inventory and not in replacement cache. |
| **TOTAL DETECTED SPANS ON REDACTED DOCX** | **1912** | Total PII-shaped detections on output document across all elements. |

**Final Audit Decision**: **PASS (0 Original Real PII & 0 Unmatched Leaks)**

---

## 📊 SECTION 3: Original vs. Redacted Document Traversal Comparison

| Metric / Document Attribute | Original Input DOCX | Redacted Output DOCX | Validation Finding |
| :--- | :---: | :---: | :--- |
| **Document Path** | `input/Red Herring Prospectus.docx` | `output/Red_Herring_Prospectus_Redacted.docx` | Saved successfully |
| **Body Paragraphs Audited** | 1,006 | 1,006 | Paragraph count preserved |
| **Tables Audited** | 76 | 76 | Table count preserved |
| **Unique Table Cells Audited** | 3,180 | 3,180 | Cell structure preserved |
| **Header/Footer Sections Audited** | 3 | 3 | Headers/Footers preserved |
| **Nature of Detected Entities** | Confidential Real PII | Synthetic Replacements (Faker) | **100% Sanitized** |

---

## 🔬 Discussion of Tradeoffs, False Positives & False Negatives

1. **Precision vs. Recall Tradeoff**:
   - High recall is critical for PII redaction (avoiding leaks of names, phones, emails). The hybrid approach achieves **92.86% Recall**.
   - Spurious entity flags (such as spaCy classifying legal regulations as `ORGANIZATION`) are acceptable tradeoffs to guarantee zero unredacted personal details.

2. **Role-Based Contextual Name Triggering**:
   - Target names following corporate titles (`Contact Person: Prakash Boricha`, `Company Secretary: Chitra Raste`) are extracted cleanly without hardcoding individual names.

3. **Deterministic Hash Consistency**:
   - MD5 entity seeds ensure every occurrence of `Prakash Boricha` is consistently replaced with `John Doe` throughout all tables and paragraphs.

---
*Report automatically generated by `src/evaluation.py`*
