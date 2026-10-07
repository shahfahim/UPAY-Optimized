"""Errors whose message is meant for the user (Bangla). Any other exception's text stays in the server log."""


class UserError(ValueError):
    pass


class LockedOut(Exception):
    """Too many wrong PINs or OTPs; the message is shown to the user (HTTP 429)."""
