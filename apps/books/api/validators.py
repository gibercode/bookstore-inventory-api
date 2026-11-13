import re

from rest_framework import serializers

# Digits with single hyphens between them; the last character may be an X (ISBN-10).
ISBN_FORMAT = re.compile(r'(?:\d-?)*[\dXx]')


def validate_isbn(value):
    """Check that `value` is a valid ISBN-10 or ISBN-13 (hyphens optional)."""
    if not ISBN_FORMAT.fullmatch(value):
        raise serializers.ValidationError(
            'ISBN must contain only digits, optionally separated by single hyphens '
            '(an ISBN-10 may end in X).'
        )

    digits = value.replace('-', '').upper()
    if len(digits) == 10:
        valid = _isbn10_checksum(digits)
    elif len(digits) == 13:
        valid = _isbn13_checksum(digits)
    else:
        raise serializers.ValidationError('ISBN must have 10 or 13 digits.')

    if not valid:
        raise serializers.ValidationError('ISBN check digit is invalid.')


def _isbn10_checksum(digits):
    values = [10 if d == 'X' else int(d) for d in digits]
    return sum(v * (10 - i) for i, v in enumerate(values)) % 11 == 0


def _isbn13_checksum(digits):
    if 'X' in digits or not digits.startswith(('978', '979')):
        return False
    return sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(digits)) % 10 == 0
