"""
Data verification module for ensuring 100% data integrity.

Features:
- Fast O(n) verification with indexing
- Missing sample detection (any pattern: beginning, middle, end, gaps)
- Quality validation (turn counts, message integrity)
- Automatic recheck file generation
- Recheck file priority loading
- Production-ready, fault-tolerant
Verification module for data quality validation.

Provides validators for different pipeline types and a unified verifier.
"""

from omnigen.verification.verifier import DataVerifier
from omnigen.verification.conversation_validator import ConversationValidator
from omnigen.verification.text_validator import TextValidator
from omnigen.verification.base_file_validator import BaseFileValidator

__all__ = [
    'DataVerifier',
    'ConversationValidator',
    'TextValidator',
    'BaseFileValidator',
]
