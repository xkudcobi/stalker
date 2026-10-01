"""Translations (English / Turkish) and language detection.

Every key must exist in every language; tests/test_i18n.py enforces this.
"""

from __future__ import annotations

import os
import sys

SUPPORTED = ("en", "tr")
DEFAULT = "en"

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        # general
        "app.tagline": "OSINT toolkit · IP · Phone · Username",
        "app.version": "version {version}",
        "common.yes": "Yes",
        "common.no": "No",
        "common.none": "-",
        "common.press_enter": "Press Enter to return to the menu...",
        "common.bye": "Goodbye!",
        "common.interrupted": "Interrupted.",
        "common.saved": "Results saved to: {path}",
        "common.save_prompt": "Save results to a JSON file? [y/N]: ",
        "common.save_yes": "y",
        "common.working": "Working, please wait...",
        # menu
        "menu.title": "MAIN MENU",
        "menu.ip": "IP Lookup",
        "menu.myip": "Show My IP",
        "menu.phone": "Phone Number Info",
        "menu.username": "Username Search",
        "menu.language": "Language: English (switch to Türkçe)",
        "menu.exit": "Exit",
        "menu.prompt": "Select an option: ",
        "menu.invalid": "Invalid option, please enter one of the numbers in the menu.",
        "menu.lang_changed": "Language set to English.",
        # ip lookup
        "ip.title": "IP ADDRESS INFORMATION",
        "ip.prompt": "Target IP address (leave empty for your own IP): ",
        "ip.invalid": "'{value}' is not a valid IPv4 or IPv6 address.",
        "ip.private": "'{value}' is a private/reserved address and cannot be located.",
        "ip.failed": "IP lookup failed: {reason}",
        "ip.source": "Data source",
        "ip.ip": "IP address",
        "ip.type": "IP type",
        "ip.continent": "Continent",
        "ip.continent_code": "Continent code",
        "ip.country": "Country",
        "ip.country_code": "Country code",
        "ip.flag": "Flag",
        "ip.capital": "Capital",
        "ip.borders": "Borders",
        "ip.calling_code": "Calling code",
        "ip.is_eu": "In the EU",
        "ip.region": "Region",
        "ip.region_code": "Region code",
        "ip.city": "City",
        "ip.postal": "Postal code",
        "ip.latitude": "Latitude",
        "ip.longitude": "Longitude",
        "ip.maps": "Google Maps",
        "ip.osm": "OpenStreetMap",
        "ip.asn": "ASN",
        "ip.org": "Organization",
        "ip.isp": "ISP",
        "ip.domain": "Domain",
        "ip.tz_id": "Time zone",
        "ip.tz_abbr": "Time zone abbr.",
        "ip.tz_dst": "Daylight saving",
        "ip.tz_offset": "UTC offset (sec)",
        "ip.tz_utc": "UTC",
        "ip.tz_time": "Current time",
        "ip.note": "Note: IP geolocation is approximate (usually the ISP's location).",
        # my ip
        "myip.title": "YOUR PUBLIC IP",
        "myip.ipv4": "IPv4 address",
        "myip.ipv6": "IPv6 address",
        "myip.unavailable": "not available",
        "myip.failed": "Could not determine your public IP: {reason}",
        # phone
        "phone.title": "PHONE NUMBER INFORMATION",
        "phone.prompt": "Phone number (e.g. +905xxxxxxxxx): ",
        "phone.invalid": "Could not parse '{value}' as a phone number.",
        "phone.input": "Input",
        "phone.location": "Location",
        "phone.region_code": "Region code",
        "phone.timezones": "Time zone(s)",
        "phone.carrier": "Carrier",
        "phone.valid": "Valid number",
        "phone.possible": "Possible number",
        "phone.international": "International format",
        "phone.national": "National format",
        "phone.mobile_dialing": "Mobile dialing format",
        "phone.e164": "E.164 format",
        "phone.country_code": "Country code",
        "phone.national_number": "National number",
        "phone.type": "Number type",
        "phone.note": "Note: carrier info reflects the original allocation; ported numbers may differ.",
        "phone.type.MOBILE": "Mobile",
        "phone.type.FIXED_LINE": "Fixed line",
        "phone.type.FIXED_LINE_OR_MOBILE": "Fixed line or mobile",
        "phone.type.TOLL_FREE": "Toll free",
        "phone.type.PREMIUM_RATE": "Premium rate",
        "phone.type.SHARED_COST": "Shared cost",
        "phone.type.VOIP": "VoIP",
        "phone.type.PERSONAL_NUMBER": "Personal number",
        "phone.type.PAGER": "Pager",
        "phone.type.UAN": "Universal access number (UAN)",
        "phone.type.VOICEMAIL": "Voicemail",
        "phone.type.UNKNOWN": "Unknown",
        # username
        "user.title": "USERNAME SEARCH",
        "user.prompt": "Username: ",
        "user.invalid": "'{value}' is not a valid username (letters, digits, . _ - only).",
        "user.checking": "Checking {count} sites...",
        "user.found": "FOUND",
        "user.not_found": "NOT FOUND",
        "user.unknown": "UNKNOWN",
        "user.summary": "Found: {found}  ·  Not found: {not_found}  ·  Unknown: {unknown}",
        "user.unknown_hint": "UNKNOWN = the site blocked the check or needs login; open the link to verify manually.",
        # cli
        "cli.description": "Stalker - OSINT toolkit for IP, phone number and username lookups.",
        "cli.lang": "interface language (en/tr)",
        "cli.json": "print results as JSON",
        "cli.output": "also save results to this JSON file",
        "cli.no_color": "disable colored output",
        "cli.cmd.ip": "look up an IP address",
        "cli.cmd.myip": "show your public IP",
        "cli.cmd.phone": "show information about a phone number",
        "cli.cmd.user": "search a username across websites",
        "cli.arg.ip": "IP address (omit for your own IP)",
        "cli.arg.number": "phone number, preferably with country code",
        "cli.arg.region": "default region for numbers without a country code (default: TR)",
        "cli.arg.username": "username to search",
        "cli.arg.timeout": "per-request timeout in seconds (default: 10)",
        "cli.arg.found_only": "only show sites where the username was found",
    },
    "tr": {
        # general
        "app.tagline": "OSINT aracı · IP · Telefon · Kullanıcı adı",
        "app.version": "sürüm {version}",
        "common.yes": "Evet",
        "common.no": "Hayır",
        "common.none": "-",
        "common.press_enter": "Menüye dönmek için Enter'a basın...",
        "common.bye": "Görüşmek üzere!",
        "common.interrupted": "İşlem durduruldu.",
        "common.saved": "Sonuçlar kaydedildi: {path}",
        "common.save_prompt": "Sonuçlar JSON dosyasına kaydedilsin mi? [e/H]: ",
        "common.save_yes": "e",
        "common.working": "İşleniyor, lütfen bekleyin...",
        # menu
        "menu.title": "ANA MENÜ",
        "menu.ip": "IP Sorgulama",
        "menu.myip": "IP Adresimi Göster",
        "menu.phone": "Telefon Numarası Bilgisi",
        "menu.username": "Kullanıcı Adı Arama",
        "menu.language": "Dil: Türkçe (switch to English)",
        "menu.exit": "Çıkış",
        "menu.prompt": "Bir seçenek girin: ",
        "menu.invalid": "Geçersiz seçenek, lütfen menüdeki numaralardan birini girin.",
        "menu.lang_changed": "Dil Türkçe olarak ayarlandı.",
        # ip lookup
        "ip.title": "IP ADRESİ BİLGİLERİ",
        "ip.prompt": "Hedef IP adresi (kendi IP'niz için boş bırakın): ",
        "ip.invalid": "'{value}' geçerli bir IPv4 veya IPv6 adresi değil.",
        "ip.private": "'{value}' özel/ayrılmış bir adres, konumu belirlenemez.",
        "ip.failed": "IP sorgulaması başarısız: {reason}",
        "ip.source": "Veri kaynağı",
        "ip.ip": "IP adresi",
        "ip.type": "IP türü",
        "ip.continent": "Kıta",
        "ip.continent_code": "Kıta kodu",
        "ip.country": "Ülke",
        "ip.country_code": "Ülke kodu",
        "ip.flag": "Bayrak",
        "ip.capital": "Başkent",
        "ip.borders": "Komşu ülkeler",
        "ip.calling_code": "Telefon kodu",
        "ip.is_eu": "AB üyesi",
        "ip.region": "Bölge",
        "ip.region_code": "Bölge kodu",
        "ip.city": "Şehir",
        "ip.postal": "Posta kodu",
        "ip.latitude": "Enlem",
        "ip.longitude": "Boylam",
        "ip.maps": "Google Haritalar",
        "ip.osm": "OpenStreetMap",
        "ip.asn": "ASN",
        "ip.org": "Kurum",
        "ip.isp": "İnternet sağlayıcı",
        "ip.domain": "Alan adı",
        "ip.tz_id": "Saat dilimi",
        "ip.tz_abbr": "Saat dilimi kısaltması",
        "ip.tz_dst": "Yaz saati",
        "ip.tz_offset": "UTC farkı (sn)",
        "ip.tz_utc": "UTC",
        "ip.tz_time": "Yerel saat",
        "ip.note": "Not: IP konumu yaklaşıktır (genellikle internet sağlayıcısının konumudur).",
        # my ip
        "myip.title": "GENEL IP ADRESİNİZ",
        "myip.ipv4": "IPv4 adresi",
        "myip.ipv6": "IPv6 adresi",
        "myip.unavailable": "mevcut değil",
        "myip.failed": "Genel IP adresiniz alınamadı: {reason}",
        # phone
        "phone.title": "TELEFON NUMARASI BİLGİLERİ",
        "phone.prompt": "Telefon numarası (örn. +905xxxxxxxxx): ",
        "phone.invalid": "'{value}' telefon numarası olarak çözümlenemedi.",
        "phone.input": "Girilen",
        "phone.location": "Konum",
        "phone.region_code": "Bölge kodu",
        "phone.timezones": "Saat dilim(ler)i",
        "phone.carrier": "Operatör",
        "phone.valid": "Geçerli numara",
        "phone.possible": "Olası numara",
        "phone.international": "Uluslararası format",
        "phone.national": "Ulusal format",
        "phone.mobile_dialing": "Mobil arama formatı",
        "phone.e164": "E.164 formatı",
        "phone.country_code": "Ülke kodu",
        "phone.national_number": "Ulusal numara",
        "phone.type": "Numara türü",
        "phone.note": "Not: Operatör bilgisi ilk tahsisi gösterir; taşınan numaralarda farklı olabilir.",
        "phone.type.MOBILE": "Mobil",
        "phone.type.FIXED_LINE": "Sabit hat",
        "phone.type.FIXED_LINE_OR_MOBILE": "Sabit hat veya mobil",
        "phone.type.TOLL_FREE": "Ücretsiz hat",
        "phone.type.PREMIUM_RATE": "Ücretli özel hat",
        "phone.type.SHARED_COST": "Paylaşımlı ücretli hat",
        "phone.type.VOIP": "VoIP",
        "phone.type.PERSONAL_NUMBER": "Kişisel numara",
        "phone.type.PAGER": "Çağrı cihazı",
        "phone.type.UAN": "Tek numara (UAN)",
        "phone.type.VOICEMAIL": "Sesli mesaj",
        "phone.type.UNKNOWN": "Bilinmiyor",
        # username
        "user.title": "KULLANICI ADI ARAMA",
        "user.prompt": "Kullanıcı adı: ",
        "user.invalid": "'{value}' geçerli bir kullanıcı adı değil (yalnızca harf, rakam, . _ -).",
        "user.checking": "{count} site kontrol ediliyor...",
        "user.found": "BULUNDU",
        "user.not_found": "YOK",
        "user.unknown": "BELİRSİZ",
        "user.summary": "Bulunan: {found}  ·  Bulunamayan: {not_found}  ·  Belirsiz: {unknown}",
        "user.unknown_hint": "BELİRSİZ = site kontrolü engelledi veya giriş istiyor; doğrulamak için bağlantıyı açın.",
        # cli
        "cli.description": "Stalker - IP, telefon numarası ve kullanıcı adı sorgulamak için OSINT aracı.",
        "cli.lang": "arayüz dili (en/tr)",
        "cli.json": "sonuçları JSON olarak yazdır",
        "cli.output": "sonuçları ayrıca bu JSON dosyasına kaydet",
        "cli.no_color": "renkli çıktıyı kapat",
        "cli.cmd.ip": "bir IP adresini sorgula",
        "cli.cmd.myip": "genel IP adresini göster",
        "cli.cmd.phone": "bir telefon numarası hakkında bilgi göster",
        "cli.cmd.user": "bir kullanıcı adını sitelerde ara",
        "cli.arg.ip": "IP adresi (kendi IP'niz için boş bırakın)",
        "cli.arg.number": "telefon numarası, tercihen ülke koduyla",
        "cli.arg.region": "ülke kodu olmayan numaralar için varsayılan bölge (varsayılan: TR)",
        "cli.arg.username": "aranacak kullanıcı adı",
        "cli.arg.timeout": "istek başına zaman aşımı, saniye (varsayılan: 10)",
        "cli.arg.found_only": "yalnızca kullanıcı adının bulunduğu siteleri göster",
    },
}

# Turkish versions of argparse's built-in messages (help headings, common errors).
# argparse looks these up through `gettext`; English needs no table.
ARGPARSE_TR: dict[str, str] = {
    "usage: ": "kullanım: ",
    "positional arguments": "konumsal argümanlar",
    "options": "seçenekler",
    "optional arguments": "seçenekler",
    "show this help message and exit": "bu yardım mesajını göster ve çık",
    "show program's version number and exit": "programın sürüm numarasını göster ve çık",
    "%(prog)s: error: %(message)s\n": "%(prog)s: hata: %(message)s\n",
    "unrecognized arguments: %s": "tanınmayan argümanlar: %s",
    "the following arguments are required: %s": "şu argümanlar zorunlu: %s",
    "invalid choice: %(value)r (choose from %(choices)s)":
        "geçersiz seçim: %(value)r (şunlardan birini seçin: %(choices)s)",
    "argument %(argument_name)s: %(message)s": "argüman %(argument_name)s: %(message)s",
    "expected one argument": "bir değer bekleniyordu",
    "invalid %(type)s value: %(value)r": "geçersiz %(type)s değeri: %(value)r",
}

_current = DEFAULT


def argparse_gettext(message: str) -> str:
    return ARGPARSE_TR.get(message, message) if _current == "tr" else message


def detect_language() -> str:
    """Pick a language from STALKER_LANG, the usual locale variables, or the OS UI language."""
    explicit = os.environ.get("STALKER_LANG", "").strip().lower()
    if explicit in SUPPORTED:
        return explicit

    for var in ("LC_ALL", "LC_MESSAGES", "LANG", "LANGUAGE"):
        value = os.environ.get(var, "").lower()
        if value:
            return "tr" if value.startswith("tr") else "en"

    if sys.platform == "win32":
        try:
            import ctypes

            lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            # Primary language id 0x1F is Turkish.
            return "tr" if (lang_id & 0x3FF) == 0x1F else "en"
        except Exception:
            pass

    return DEFAULT


def set_language(lang: str) -> None:
    global _current
    lang = (lang or "").lower()
    _current = lang if lang in SUPPORTED else DEFAULT


def get_language() -> str:
    return _current


def t(key: str, **kwargs) -> str:
    """Translate a key into the current language, falling back to English, then to the key."""
    text = STRINGS[_current].get(key) or STRINGS[DEFAULT].get(key) or key
    return text.format(**kwargs) if kwargs else text


def yes_no(value) -> str:
    if value is None:
        return t("common.none")
    return t("common.yes") if value else t("common.no")
