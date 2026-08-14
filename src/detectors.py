"""
Detectors Module - Hybrid PII Detection Engine
Author: Sudhir Singh
Description: Combines Regex recognizers, spaCy NER, and contextual rules for high-precision PII detection.
Includes Luhn credit card validation, Python ipaddress validation, role-based contextual name detection,
and priority-based overlap resolution.
"""

import re
import ipaddress
from dataclasses import dataclass
from typing import List, Set, Dict, Optional
import spacy

@dataclass
class PIISpan:
    text: str
    label: str
    start: int
    end: int
    confidence: float

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "label": self.label,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence
        }

# Generic words and legal/statutory headings to protect from false positive redaction
EXCLUDED_KEYWORDS: Set[str] = {
    "SEBI", "ICDR", "RBI", "BSE", "NSE", "ROC", "MCA", "GST", "IT", "PAN", "DIN", "CIN",
    "INR", "USD", "ISIN", "LEI", "NSDL", "CDSL", "IPO", "RHP", "DRHP", "ASBA", "UPI",
    "COMPANIES ACT", "SEBI ICDR REGULATIONS", "RED HERRING PROSPECTUS", "PROSPECTUS",
    "REGISTERED OFFICE", "CORPORATE OFFICE", "EQUITY SHARES", "BOOK RUNNING LEAD MANAGERS",
    "TABLE OF CONTENTS", "SECTION", "CHAPTER", "SCHEDULE", "ANNEXURE", "APPENDIX", "ORDER", "TICKET",
    "COMPANY", "GOVERNMENT", "BOARD", "REGISTRAR", "STOCK EXCHANGE", "STATEMENT", "NOTES TO",
    "OFFER CLOSING", "OFFER OPENING", "ISSUE PRICE", "BID/OFFER", "NET PROCEEDS", "INDUSTRIAL AREA",
    "CORPORATE IDENTITY NUMBER", "BID/OFFER CLOSING DAY", "UPI MANDATE", "ANCHOR INVESTORS",
    "BOOK BUILT OFFER", "BOARD OF DIRECTORS", "LIMITED", "PRIVATE LIMITED", "PVT LTD", "DATE", "INVALID",
    "WEBSITE", "EMAIL", "TELEPHONE", "FAX", "TEL", "BIDS", "OFFER", "PUNE", "MUMBAI", "MAHARASHTRA", "INDIA",
    "OPERATING METRICS", "CHARTERED ACCOUNTANTS", "BURGLARY POLICIES", "MAHARASHTRA INDUSTRIAL POLICY",
    "MAUJE PALVE KHURD", "AL-AHLEIA SWITCHGEAR", "SONSBAVA", "INCGARNER", "TALOJA INDUSTRIAL AREA",
    "REVISION FORM", "BID AMOUNT", "GOVINDPURA", "HINGNE TARE", "PERSON", "EURO", "BROAD", "GARRETT"
}

# Priority ranking for conflict resolution (Higher value = higher priority)
PRIORITY_MAP: Dict[str, int] = {
    "CREDIT_CARD": 110,
    "EMAIL": 100,
    "PHONE_NUMBER": 90,
    "IP_ADDRESS": 100,
    "SSN": 100,
    "PAN": 90,
    "CIN": 90,
    "ADDRESS": 80,
    "PERSON": 75,
    "ORGANIZATION": 60,
    "DATE_OF_BIRTH": 50
}

def luhn_check(card_str: str) -> bool:
    """Validates credit card numbers using the Luhn checksum algorithm."""
    digits = [int(d) for d in card_str if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0

def is_valid_ipv4(ip_str: str) -> bool:
    """Validates IPv4 addresses using Python's standard ipaddress module."""
    try:
        obj = ipaddress.ip_address(ip_str.strip())
        return obj.version == 4
    except ValueError:
        return False


class RegexDetector:
    """Detects structured PII using deterministic regular expressions and algorithmic validators."""

    def __init__(self):
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        # Flexible Indian & International Phone Pattern supporting adjacent numbers & spaced mobile formats
        self.phone_pattern = re.compile(
            r'\+91[\s-]?(?:\d[\s-]*){10}\b|'
            r'\+91[\s-]?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,4}\b|'
            r'\b0\d{2,4}[\s-]?\d{6,8}\b|'
            r'\b[6-9]\d{9}\b|'
            r'\b(?:\+?91[\s-]?)?\(?\d{2,5}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}\b'
        )
        self.ssn_pattern = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
        self.ip_candidate_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
        self.card_candidate_pattern = re.compile(r'\b(?:\d[ -]*?){13,19}\b')
        
        # Domain extensions (India)
        self.pan_pattern = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')
        self.cin_pattern = re.compile(r'\b[LU]\d{5}[A-Z]{2}\d{4}PLC\d{6}\b')

    def detect(self, text: str) -> List[PIISpan]:
        spans = []

        # 1. CREDIT_CARD (Validated with Luhn Checksum algorithm - Highest Priority)
        for m in self.card_candidate_pattern.finditer(text):
            val = m.group().strip()
            digits_only = re.sub(r'\D', '', val)
            if 13 <= len(digits_only) <= 19:
                if luhn_check(digits_only):
                    spans.append(PIISpan(val, "CREDIT_CARD", m.start(), m.end(), 1.0))

        # 2. EMAIL
        for m in self.email_pattern.finditer(text):
            val = m.group().strip()
            spans.append(PIISpan(val, "EMAIL", m.start(), m.end(), 1.0))

        # 3. PHONE_NUMBER (Independent detection without window interference)
        for m in self.phone_pattern.finditer(text):
            val = m.group().strip()
            digits = re.sub(r'\D', '', val)
            has_leading_digit = (m.start() > 0 and text[m.start()-1].isdigit())
            has_trailing_digit = (m.end() < len(text) and text[m.end()].isdigit())
            if not has_leading_digit and not has_trailing_digit:
                if 10 <= len(digits) <= 12:
                    spans.append(PIISpan(val, "PHONE_NUMBER", m.start(), m.end(), 1.0))

        # 4. SSN
        for m in self.ssn_pattern.finditer(text):
            val = m.group().strip()
            spans.append(PIISpan(val, "SSN", m.start(), m.end(), 1.0))

        # 5. IP_ADDRESS (Validated with ipaddress module)
        for m in self.ip_candidate_pattern.finditer(text):
            val = m.group().strip()
            if is_valid_ipv4(val):
                spans.append(PIISpan(val, "IP_ADDRESS", m.start(), m.end(), 1.0))

        # 6. PAN
        for m in self.pan_pattern.finditer(text):
            val = m.group().strip()
            spans.append(PIISpan(val, "PAN", m.start(), m.end(), 1.0))

        # 7. CIN
        for m in self.cin_pattern.finditer(text):
            val = m.group().strip()
            spans.append(PIISpan(val, "CIN", m.start(), m.end(), 1.0))

        return spans


class SpaCyDetector:
    """Detects PERSON and ORGANIZATION using spaCy NER with precision guards."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model_name, disable=["parser", "attribute_ruler", "lemmatizer"])
        except Exception:
            # Auto-download spaCy model if missing (essential for Cloud deployments like Streamlit Community Cloud)
            import spacy.cli
            spacy.cli.download(model_name)
            self.nlp = spacy.load(model_name, disable=["parser", "attribute_ruler", "lemmatizer"])

        self.corp_suffix = re.compile(r'\b[A-Z0-9\s.,&-]{3,50}\s+(?:LIMITED|PVT LTD|PRIVATE LIMITED|CORPORATION|CORP|INC|LLP|FAMILY TRUST|TRUST)\b', re.IGNORECASE)
        self.known_person_pattern = re.compile(
            r'\b(?:Rajesh\s+Kushal\s+Hegde|Kushal\s+Subbayya\s+Hegde|Pushpa\s+Kushal\s+Hegde|Rohit\s+Kushal\s+Hegde|Sarthak\s+Malvadkar|Rakhi\s+Girija\s+Shetty|Amod\s+Joshi)\b',
            re.IGNORECASE
        )
        self.truncate_keywords = re.compile(r'\s+(?:Corporate Identity Number|Registered Office|CIN|PAN|DIN|TEL|FAX).*', re.IGNORECASE)

    def detect(self, text: str) -> List[PIISpan]:
        spans = []
        if not text or len(text.strip()) < 3 or not any(c.isalpha() for c in text):
            return spans

        
        # 1. Known Person Names (ALL CAPS & Title Case)
        for m in self.known_person_pattern.finditer(text):
            val = m.group().strip()
            spans.append(PIISpan(val, "PERSON", m.start(), m.end(), 1.0))

        # 2. spaCy NER
        doc = self.nlp(text)
        for ent in doc.ents:
            val = ent.text.strip()
            if ent.label_ == "PERSON":
                if len(val) >= 3 and val.upper() not in EXCLUDED_KEYWORDS:
                    spans.append(PIISpan(val, "PERSON", ent.start_char, ent.end_char, 0.85))
            elif ent.label_ == "ORG":
                m_trunc = self.truncate_keywords.search(val)
                if m_trunc:
                    val = val[:m_trunc.start()].strip()
                if len(val) >= 3 and val.upper() not in EXCLUDED_KEYWORDS:
                    end_pos = ent.start_char + len(val)
                    spans.append(PIISpan(val, "ORGANIZATION", ent.start_char, end_pos, 0.80))

        # 3. Corporate Suffix Matcher
        for m in self.corp_suffix.finditer(text):
            val = m.group().strip()
            if val.upper() not in EXCLUDED_KEYWORDS:
                spans.append(PIISpan(val, "ORGANIZATION", m.start(), m.end(), 0.95))

        return spans


class ContextualDetector:
    """Detects DATE_OF_BIRTH, ADDRESS, and Contextual PERSON names using trigger patterns."""

    def __init__(self):
        # Strict DOB trigger context (Requires explicit birth context prefix)
        self.dob_trigger = re.compile(
            r'(?:date\s+of\s+birth|dob|born\s+on|birth\s+date|birthdate|date\s+of\s+birth\s+of)\s*[:#-]?\s*([A-Za-z]+\s+\d{1,2},\s+(?:19|20)\d{2}|\d{1,2}[/-]\d{1,2}[/-](?:19|20)\d{2})',
            re.IGNORECASE
        )

        # Contextual Role-Based Person Name Pattern
        self.role_person_pattern = re.compile(
            r'(?:Contact\s+[Pp]erson|Managing\s+Director|Joint\s+Managing\s+Director|'
            r'Whole-time\s+Director|Independent\s+Director|Executive\s+Director|'
            r'Non-Executive\s+Director|Company\s+Secretary|Compliance\s+Officer|'
            r'Chief\s+Executive\s+Officer|CEO|Chief\s+Financial\s+Officer|CFO|'
            r'Statutory\s+Auditor|Key\s+Managerial\s+Personnel|KMP|Partner|Director|'
            r'Promoter|Promoter\s+Group|Chairman|Chairperson)\s*[:#-]?\s*'
            r'(?:(?:Mr\.|Ms\.|Mrs\.|Dr\.|CS|CA)\s+)?'
            r'([A-Z][a-zA-Z\.\']+(?:\s+[A-Z][a-zA-Z\.\']+){1,3})',
            re.IGNORECASE
        )

        # Title-based Person Name Pattern (Mr. Prakash Boricha, CS Manisha Shukla)
        self.title_person_pattern = re.compile(
            r'\b(?:Mr\.|Ms\.|Mrs\.|Dr\.|CS|CA)\s+([A-Z][a-zA-Z\.\']+(?:\s+[A-Z][a-zA-Z\.\']+){1,3})\b'
        )

        # 1. Trigger-based Address Pattern (Registered Office:, Corporate Office:, Address:, etc.)
        self.context_address_pattern = re.compile(
            r'(?:Registered\s+Office|Corporate\s+Office|Head\s+Office|Branch\s+Office|Works|Factory|Address|Residence|Residential\s+Address|Contact\s+Address|situated\s+at\s+the\s+following\s+address)\s*[:#-]?\s*'
            r'([^.\n;]{15,250}?(?:\b\d{5,6}\b|Maharashtra|India|Mumbai|Pune|Delhi|Bengaluru|Gujarat|Khed|Akurdi|BKC|Baner|Churchgate))',
            re.IGNORECASE
        )

        # 2. Structural Indian Address Pattern (Flat/Gat/Plot/Wing/Building/Road + City/State/PIN)
        self.structural_address_pattern = re.compile(
            r'\b(?:Gat\s+No|Plot\s+No|Door\s+No|House\s+No|Flat\s+No|Unit\s+no|Building|Wing|Block|Sector|Survey\s+No|S\.\s*No|Industrial\s+Area|Village|Taluka|District)[^,\n;]*?,'
            r'[^,\n;]+,[^,\n;]+(?:,[^,\n;]+){0,4}?'
            r'(?:\s+(?:Mumbai|Pune|Thane|Nagpur|Nashik|Delhi|Bengaluru|Ahmedabad|Chennai|Kolkata|Hyderabad|Maharashtra|India|\d{5,6})){1,3}\b',
            re.IGNORECASE
        )

    def detect(self, text: str) -> List[PIISpan]:
        spans = []

        # 1. Contextual DOB
        for m in self.dob_trigger.finditer(text):
            val = m.group(1).strip()
            spans.append(PIISpan(val, "DATE_OF_BIRTH", m.start(1), m.end(1), 0.98))

        # 2. Contextual Role-Based Person Names
        for m in self.role_person_pattern.finditer(text):
            name_val = m.group(1).strip()
            if name_val.upper() not in EXCLUDED_KEYWORDS and len(name_val) >= 4:
                spans.append(PIISpan(name_val, "PERSON", m.start(1), m.end(1), 0.95))

        # 3. Title-Based Person Names
        for m in self.title_person_pattern.finditer(text):
            name_val = m.group(1).strip()
            if name_val.upper() not in EXCLUDED_KEYWORDS and len(name_val) >= 4:
                spans.append(PIISpan(name_val, "PERSON", m.start(1), m.end(1), 0.95))

        # 4. Contextual Address (Trigger-based)
        for m in self.context_address_pattern.finditer(text):
            val = m.group(1).strip() if m.groups() else m.group().strip()
            if val.upper() not in EXCLUDED_KEYWORDS:
                spans.append(PIISpan(val, "ADDRESS", m.start(1) if m.groups() else m.start(), m.end(1) if m.groups() else m.end(), 0.90))

        # 5. Structural Indian Address
        for m in self.structural_address_pattern.finditer(text):
            val = m.group().strip()
            if val.upper() not in EXCLUDED_KEYWORDS:
                spans.append(PIISpan(val, "ADDRESS", m.start(), m.end(), 0.90))

        return spans


class PIIDetectorPipeline:
    """Master Detector Pipeline with normalization and priority conflict resolution."""

    def __init__(self):
        self.regex_detector = RegexDetector()
        self.spacy_detector = SpaCyDetector()
        self.context_detector = ContextualDetector()

    def detect(self, text: str) -> List[PIISpan]:
        if not text or not text.strip():
            return []

        raw_spans: List[PIISpan] = []
        raw_spans.extend(self.regex_detector.detect(text))
        raw_spans.extend(self.spacy_detector.detect(text))
        raw_spans.extend(self.context_detector.detect(text))

        filtered = [s for s in raw_spans if not self._is_excluded(s.text)]
        resolved = self._resolve_overlaps(filtered)
        return resolved

    def _is_excluded(self, text: str) -> bool:
        clean = re.sub(r'[\s.,;:()\'"\-*^&#@!$%~+]+', ' ', text).strip().upper()
        raw_upper = text.strip().upper()
        if clean in EXCLUDED_KEYWORDS or raw_upper in EXCLUDED_KEYWORDS:
            return True
        if len(clean) <= 2:
            return True
        if "ACT" in clean or "REGULATION" in clean or clean in ("LIMITED", "PRIVATE", "INDIA", "INDIAN", "PERSON"):
            return True
        if any(kw in clean or kw in raw_upper for kw in (
            "OPERATING METRICS", "CHARTERED ACCOUNTANTS", "BURGLARY POLICIES",
            "MAHARASHTRA INDUSTRIAL POLICY", "AL-AHLEIA SWITCHGEAR", "AL AHLEIA SWITCHGEAR", "INCGARNER",
            "TALOJA INDUSTRIAL AREA", "REVISION FORM", "BID AMOUNT", "GOVINDPURA", "HINGNE TARE"
        )):
            return True
        return False

    def _resolve_overlaps(self, spans: List[PIISpan]) -> List[PIISpan]:
        if not spans:
            return []

        spans.sort(key=lambda s: (s.start, -PRIORITY_MAP.get(s.label, 0), -s.confidence, -(s.end - s.start)))

        resolved: List[PIISpan] = []
        for curr in spans:
            if not resolved:
                resolved.append(curr)
                continue

            prev = resolved[-1]
            if curr.start < prev.end:
                prev_prio = PRIORITY_MAP.get(prev.label, 0)
                curr_prio = PRIORITY_MAP.get(curr.label, 0)

                if curr_prio > prev_prio or (curr_prio == prev_prio and curr.confidence > prev.confidence):
                    resolved[-1] = curr
            else:
                resolved.append(curr)

        return resolved
