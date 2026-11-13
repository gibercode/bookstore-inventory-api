import re

from rest_framework import serializers

ISBN_FORMAT = re.compile(r'\d+(-\d+)*')


def isbn13_digits(value):
    """Return the 13 digits of a valid ISBN-13, or raise a ValidationError."""
    if not ISBN_FORMAT.fullmatch(value):
        raise serializers.ValidationError(
            'ISBN must contain only digits, optionally separated by single hyphens.'
        )

    digits = value.replace('-', '')
    if len(digits) != 13 or not digits.startswith(('978', '979')):
        raise serializers.ValidationError(
            'ISBN must be a valid ISBN-13 starting with 978 or 979.'
        )

    checksum = sum(int(d) * (3 if i % 2 else 1) for i, d in enumerate(digits))
    if checksum % 10 != 0:
        raise serializers.ValidationError('ISBN-13 check digit is invalid.')

    return digits
