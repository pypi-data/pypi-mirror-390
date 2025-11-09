"""
Data privacy controls.
Masking, redaction, and retention policies.
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta


# Common PII patterns
PII_PATTERNS = [
    (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),  # SSN
    (r'\b\d{3}\.\d{2}\.\d{4}\b', 'SSN'),  # SSN with dots
    (r'\b\d{16}\b', 'CREDIT_CARD'),  # Credit card (16 digits)
    (r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', 'CREDIT_CARD'),  # Credit card formatted
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),  # Email
    (r'\b\d{3}-\d{3}-\d{4}\b', 'PHONE'),  # Phone
    (r'\b\(\d{3}\)\s?\d{3}-\d{4}\b', 'PHONE'),  # Phone formatted
]


def mask_pii(text: str, mask_char: str = '*') -> tuple[str, List[str]]:
    """
    Mask PII in text.
    
    Args:
        text: Text to mask
        mask_char: Character to use for masking
    
    Returns:
        Tuple of (masked_text, detected_types)
    """
    if not isinstance(text, str):
        return text, []
    
    masked_text = text
    detected_types = []
    
    for pattern, pii_type in PII_PATTERNS:
        matches = re.findall(pattern, masked_text)
        if matches:
            detected_types.append(pii_type)
            # Mask the matches
            if pii_type == 'SSN':
                masked_text = re.sub(pattern, r'***-**-****', masked_text)
            elif pii_type == 'CREDIT_CARD':
                masked_text = re.sub(pattern, r'****-****-****-****', masked_text)
            elif pii_type == 'EMAIL':
                masked_text = re.sub(pattern, r'***@***.***', masked_text)
            elif pii_type == 'PHONE':
                masked_text = re.sub(pattern, r'***-***-****', masked_text)
    
    return masked_text, detected_types


def should_redact_log(log_entry: Dict[str, Any], redaction_rules: Optional[List[str]] = None) -> bool:
    """
    Determine if a log entry should be redacted.
    
    Args:
        log_entry: Log entry dictionary
        redaction_rules: List of fields to redact (e.g., ['model', 'prompt_id'])
    
    Returns:
        True if log should be redacted
    """
    if not redaction_rules:
        return False
    
    # Check if any redaction rule matches
    for rule in redaction_rules:
        if rule in log_entry:
            return True
    
    return False


def redact_log(log_entry: Dict[str, Any], redaction_rules: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Redact sensitive fields from log entry.
    
    Args:
        log_entry: Log entry dictionary
        redaction_rules: List of fields to redact
    
    Returns:
        Redacted log entry
    """
    if not redaction_rules:
        return log_entry
    
    redacted = log_entry.copy()
    
    for rule in redaction_rules:
        if rule in redacted:
            redacted[rule] = '[REDACTED]'
    
    return redacted


def should_retain_log(timestamp: str, retention_days: Optional[int] = None) -> bool:
    """
    Determine if a log should be retained based on retention policy.
    
    Args:
        timestamp: Log timestamp (ISO format)
        retention_days: Number of days to retain logs (None = keep forever)
    
    Returns:
        True if log should be retained
    """
    if retention_days is None:
        return True
    
    try:
        log_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        cutoff_date = datetime.now(log_date.tzinfo) - timedelta(days=retention_days)
        return log_date >= cutoff_date
    except Exception:
        # If we can't parse timestamp, keep it
        return True


class PrivacyConfig:
    """Configuration for privacy controls."""
    
    def __init__(
        self,
        mask_pii_enabled: bool = False,
        redaction_rules: Optional[List[str]] = None,
        retention_days: Optional[int] = None
    ):
        self.mask_pii_enabled = mask_pii_enabled
        self.redaction_rules = redaction_rules or []
        self.retention_days = retention_days
    
    def should_mask(self) -> bool:
        """Check if PII masking is enabled."""
        return self.mask_pii_enabled
    
    def should_redact(self, log_entry: Dict[str, Any]) -> bool:
        """Check if log should be redacted."""
        return should_redact_log(log_entry, self.redaction_rules)
    
    def should_retain(self, timestamp: str) -> bool:
        """Check if log should be retained."""
        return should_retain_log(timestamp, self.retention_days)

