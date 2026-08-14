"""
Replacement Module - Synthetic Data Replacer
Author: Sudhir Singh
Description: Generates format-preserving fake PII replacements using Faker.
Maintains deterministic entity mapping consistency across document.
"""

import hashlib
from typing import Dict, Tuple
from faker import Faker

class SyntheticReplacer:
    """Generates consistent synthetic replacements for PII entities."""

    def __init__(self, seed: int = 42):
        self.fake = Faker(["en_IN", "en_US"])
        self.fake.seed_instance(seed)
        self.mapping_cache: Dict[Tuple[str, str], str] = {}

    def _get_hash_seed(self, text: str) -> int:
        return int(hashlib.md5(text.lower().strip().encode("utf-8")).hexdigest(), 16) % (2**32)

    def get_replacement(self, text: str, label: str) -> str:
        clean_text = text.strip()
        key = (clean_text.lower(), label)

        if key in self.mapping_cache:
            return self.mapping_cache[key]

        entity_seed = self._get_hash_seed(clean_text)
        self.fake.seed_instance(entity_seed)

        if label == "EMAIL":
            user = self.fake.user_name()
            domain = self.fake.free_email_domain()
            replacement = f"{user}@{domain}"

        elif label == "PHONE_NUMBER":
            if clean_text.startswith("+91"):
                replacement = f"+91 {self.fake.numerify('##########')}"
            elif clean_text.startswith("+"):
                prefix = clean_text[:3]
                replacement = f"{prefix} {self.fake.numerify('##########')}"
            else:
                replacement = self.fake.numerify("##########")

        elif label == "PERSON":
            replacement = self.fake.name()

        elif label == "ORGANIZATION":
            replacement = self.fake.company()

        elif label == "ADDRESS":
            replacement = f"{self.fake.building_number()}, {self.fake.street_name()}, {self.fake.city()}, {self.fake.state()} - {self.fake.postcode()}"

        elif label == "SSN":
            replacement = self.fake.numerify("###-##-####")

        elif label == "CREDIT_CARD":
            replacement = self.fake.credit_card_number()

        elif label == "DATE_OF_BIRTH":
            replacement = self.fake.date_of_birth(minimum_age=18, maximum_age=70).strftime("%B %d, %Y")

        elif label == "IP_ADDRESS":
            replacement = self.fake.ipv4()

        # Domain extensions
        elif label == "PAN":
            prefix = self.fake.lexify("?????").upper()
            digits = self.fake.numerify("####")
            suffix = self.fake.lexify("?").upper()
            replacement = f"{prefix}{digits}{suffix}"

        elif label == "CIN":
            replacement = f"U{self.fake.numerify('#####')}MH2024PLC{self.fake.numerify('######')}"

        else:
            replacement = f"[REDACTED_{label}]"

        self.mapping_cache[key] = replacement
        return replacement
