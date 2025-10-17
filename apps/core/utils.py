def mask_email(email):
    """Mask an email address safely for logging."""
    if not email or not isinstance(email, str) or '@' not in email:
        return 'unknown_email'
    try:
        local, domain = email.split('@', 1)
        return f"{local[:3]}****@{domain}"
    except Exception:
        return 'invalid_email'
