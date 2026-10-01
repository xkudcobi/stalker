"""Offline phone number analysis with Google's libphonenumber data."""

from __future__ import annotations

import phonenumbers
from phonenumbers import PhoneNumberFormat, PhoneNumberType, carrier, geocoder, timezone

from stalker.net import StalkerError

DEFAULT_REGION = "TR"

_TYPE_NAMES = {
    getattr(PhoneNumberType, name): name
    for name in (
        "MOBILE", "FIXED_LINE", "FIXED_LINE_OR_MOBILE", "TOLL_FREE", "PREMIUM_RATE",
        "SHARED_COST", "VOIP", "PERSONAL_NUMBER", "PAGER", "UAN", "VOICEMAIL", "UNKNOWN",
    )
}


def analyze(number: str, region: str = DEFAULT_REGION, lang: str = "en") -> dict:
    """Parse `number` and describe it. Location / carrier names use `lang` when available."""
    region = (region or DEFAULT_REGION).upper()
    try:
        parsed = phonenumbers.parse(number, region)
    except phonenumbers.NumberParseException:
        raise StalkerError("phone.invalid", value=number) from None

    number_region = phonenumbers.region_code_for_number(parsed)
    return {
        "input": number,
        "location": geocoder.description_for_number(parsed, lang) or None,
        "region_code": number_region,
        "timezones": [tz for tz in timezone.time_zones_for_number(parsed) if tz != "Etc/Unknown"],
        "carrier": carrier.name_for_number(parsed, lang) or None,
        "valid": phonenumbers.is_valid_number(parsed),
        "possible": phonenumbers.is_possible_number(parsed),
        "international": phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL),
        "national": phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL),
        "mobile_dialing": phonenumbers.format_number_for_mobile_dialing(
            parsed, number_region or region, with_formatting=True
        ) or None,
        "e164": phonenumbers.format_number(parsed, PhoneNumberFormat.E164),
        "country_code": f"+{parsed.country_code}",
        "national_number": str(parsed.national_number),
        "type": _TYPE_NAMES.get(phonenumbers.number_type(parsed), "UNKNOWN"),
    }
