def mask_email(email):
    """Mask an email address safely for logging."""
    if not email or not isinstance(email, str) or '@' not in email:
        return 'unknown_email'
    try:
        local, domain = email.split('@', 1)
        # If local part is very short, don't mask
        if len(local) <= 2:
            return f"{local}@{domain}"

        # For general cases preserve first character and everything from index 3 onwards,
        # inserting two asterisks after the first char. This matches the project's masking
        # expectations used in tests (e.g. 'john.doe' -> 'j**n.doe').
        return f"{local[0]}**{local[3:]}@{domain}"
    except Exception:
        return 'invalid_email'
