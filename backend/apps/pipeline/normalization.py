import phonenumbers

FIELD_ALIASES = {
    "name": ("name", "full_name", "contact_name", "first_name", "contact"),
    "phone": ("phone", "phone_number", "mobile", "mobile_number", "telephone", "tel", "phone_no"),
    "company": ("company", "company_name", "organization", "business", "org"),
    "notes": ("notes", "note", "comments", "description", "details", "remarks"),
}

_ALIAS_MAP = {
    alias: field for field, aliases in FIELD_ALIASES.items() for alias in aliases
}


def map_fields(raw):
    mapped = {}
    for key, value in raw.items():
        field = _ALIAS_MAP.get(key.lower().replace(" ", "_"))
        if field:
            mapped.setdefault(field, value)
        else:
            mapped.setdefault("extra_fields", {})[key] = value
    return mapped


def normalize_phone(value):
    if not value:
        return None
    try:
        number = phonenumbers.parse(value, "US")
    except phonenumbers.NumberParseException:
        return None
    if not phonenumbers.is_valid_number(number):
        return None
    return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)