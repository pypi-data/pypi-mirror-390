"""Define package errors."""

from typing import Optional


class KwiksetError(Exception):
    """Define a base error."""

    pass


class RequestError(KwiksetError):
    """Define an error related to invalid requests."""

    pass


class MFAChallengeRequired(KwiksetError):
    """Define an error when MFA challenge is required."""
    
    def __init__(self, message: str = "MFA challenge required.", mfa_type: Optional[str] = None, mfa_tokens: Optional[dict] = None) -> None:
        """Initialize an MFA challenge required error."""
        super().__init__(message)
        self.mfa_type = mfa_type  # 'SMS_MFA' or 'SOFTWARE_TOKEN_MFA'
        self.mfa_tokens = mfa_tokens or {}
