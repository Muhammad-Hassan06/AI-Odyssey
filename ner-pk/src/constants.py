"""
Constants, label schemas, and reproducible random seeds for Pakistani NER.
Strictly adheres to the 20 entity classes defined by the competition.
"""

import os
import random
import numpy as np

# Exact 20 Entity Types
ENTITY_TYPES = [
    "PERSON",
    "CITY",
    "PROVINCE_REGION",
    "COUNTRY",
    "LANDMARK_FACILITY",
    "GOVERNMENT_BODY",
    "POLITICAL_PARTY",
    "ORGANIZATION",
    "EDUCATIONAL_INSTITUTION",
    "COURT_LEGAL_BODY",
    "LAW_ACT",
    "EVENT",
    "MEDIA_OUTLET",
    "SPORTS_TEAM",
    "DATE",
    "TIME",
    "MONEY",
    "PERCENT",
    "PHONE_NUMBER",
    "ID_NUMBER"
]

# Verify exact length
assert len(ENTITY_TYPES) == 20, f"Expected exactly 20 entity types, got {len(ENTITY_TYPES)}"

# BIO Schema: 41 labels
BIO_LABELS = ["O"] + [f"B-{ent}" for ent in ENTITY_TYPES] + [f"I-{ent}" for ent in ENTITY_TYPES]
assert len(BIO_LABELS) == 41, f"Expected 41 BIO labels, got {len(BIO_LABELS)}"

LABEL2ID = {label: idx for idx, label in enumerate(BIO_LABELS)}
ID2LABEL = {idx: label for idx, label in enumerate(BIO_LABELS)}

def validate_entity_type(entity_type: str) -> bool:
    """Validate that an entity type is strictly one of the 20 approved categories."""
    return entity_type in ENTITY_TYPES

def set_seed(seed: int = 42) -> None:
    """Set global seeds across Python, NumPy, and PyTorch for determinism."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except (ImportError, OSError, Exception):
        pass
