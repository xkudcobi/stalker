"""Offline tests (no network): translations, phone parsing, IP validation, site rules."""

import re
import string
import unittest
from unittest import mock

from stalker import cli, i18n
from stalker.core import ip_lookup, phone, username
from stalker.net import StalkerError


def _placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


class TranslationTests(unittest.TestCase):
    def test_every_language_has_the_same_keys(self):
        keys = {lang: set(table) for lang, table in i18n.STRINGS.items()}
        for lang in i18n.SUPPORTED:
            self.assertEqual(keys[lang], keys["en"], f"key mismatch in '{lang}'")

    def test_placeholders_match(self):
        for key, text in i18n.STRINGS["en"].items():
            for lang in i18n.SUPPORTED:
                self.assertEqual(_placeholders(i18n.STRINGS[lang][key]), _placeholders(text),
                                 f"placeholder mismatch for '{key}' in '{lang}'")

    def test_no_empty_strings(self):
        for lang, table in i18n.STRINGS.items():
            for key, text in table.items():
                self.assertTrue(text.strip(), f"empty string for '{key}' in '{lang}'")

    def test_every_used_key_exists(self):
        """Literal t("...") keys in the source must be defined."""
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1] / "stalker"
        used = set()
        for path in root.rglob("*.py"):
            used |= set(re.findall(r"""\bt\(\s*["']([a-z_.A-Z0-9]+)["']""", path.read_text("utf-8")))
            used |= set(re.findall(r"""StalkerError\(\s*["']([a-z_.]+)["']""", path.read_text("utf-8")))
        missing = used - set(i18n.STRINGS["en"])
        self.assertFalse(missing, f"undefined translation keys: {missing}")

    def test_dynamic_keys_exist(self):
        for field in ip_lookup.FIELDS:
            self.assertIn(f"ip.{field}", i18n.STRINGS["en"])
        for name in phone._TYPE_NAMES.values():
            self.assertIn(f"phone.type.{name}", i18n.STRINGS["en"])

    def test_switching_language(self):
        i18n.set_language("tr")
        self.assertEqual(i18n.t("common.yes"), "Evet")
        i18n.set_language("en")
        self.assertEqual(i18n.t("common.yes"), "Yes")
        i18n.set_language("xx")
        self.assertEqual(i18n.get_language(), "en")

    def test_env_override(self):
        with mock.patch.dict("os.environ", {"STALKER_LANG": "tr"}):
            self.assertEqual(i18n.detect_language(), "tr")

    def test_help_renders_in_both_languages(self):
        for lang in i18n.SUPPORTED:
            i18n.set_language(lang)
            self.assertIn(i18n.t("cli.description"), cli.build_parser().format_help())
        i18n.set_language("en")


class PhoneTests(unittest.TestCase):
    def test_turkish_mobile(self):
        info = phone.analyze("+905321234567", lang="tr")
        self.assertEqual(info["region_code"], "TR")
        self.assertEqual(info["type"], "MOBILE")
        self.assertEqual(info["e164"], "+905321234567")
        self.assertTrue(info["valid"])

    def test_default_region_applies_without_country_code(self):
        info = phone.analyze("02125551234", region="TR")
        self.assertEqual(info["country_code"], "+90")
        self.assertEqual(info["type"], "FIXED_LINE")

    def test_garbage_raises(self):
        with self.assertRaises(StalkerError) as ctx:
            phone.analyze("hello")
        self.assertEqual(ctx.exception.key, "phone.invalid")


class IpTests(unittest.TestCase):
    def test_validation(self):
        self.assertEqual(ip_lookup.validate(" 8.8.8.8 "), "8.8.8.8")
        self.assertEqual(ip_lookup.validate("2001:4860:4860::8888"), "2001:4860:4860::8888")
        for bad, key in (("abc", "ip.invalid"), ("999.1.1.1", "ip.invalid"),
                         ("192.168.1.1", "ip.private"), ("127.0.0.1", "ip.private")):
            with self.assertRaises(StalkerError) as ctx:
                ip_lookup.validate(bad)
            self.assertEqual(ctx.exception.key, key)

    def test_ipapi_mapping_fills_every_field(self):
        data = ip_lookup._from_ipapi({"status": "success", "query": "1.1.1.1", "lat": 1.5,
                                      "lon": 2.5, "offset": 10800, "as": "AS13335 Cloudflare"})
        self.assertTrue(set(ip_lookup.FIELDS) <= set(data))
        self.assertEqual(data["asn"], "AS13335")
        self.assertEqual(data["tz_utc"], "+03:00")
        self.assertIn("1.5,2.5", data["maps"])


class UsernameTests(unittest.TestCase):
    @staticmethod
    def _resp(status=200, text="", url="https://example.com/x"):
        return mock.Mock(status_code=status, text=text, url=url)

    def test_status_rules(self):
        site = username.Site("Example", "https://example.com/{}")
        self.assertEqual(username._classify(site, self._resp(404), "x"), username.NOT_FOUND)
        self.assertEqual(username._classify(site, self._resp(200), "x"), username.FOUND)
        self.assertEqual(username._classify(site, self._resp(403), "x"), username.UNKNOWN)
        login = self._resp(200, url="https://example.com/login?next=x")
        self.assertEqual(username._classify(site, login, "x"), username.UNKNOWN)

    def test_text_rules(self):
        site = username.Site("Ex", "https://e.com/{}", present_text=('"user":"{}"',),
                             missing_is_absent=True)
        self.assertEqual(username._classify(site, self._resp(text='{"user":"bob"}'), "bob"),
                         username.FOUND)
        self.assertEqual(username._classify(site, self._resp(text="{}"), "bob"), username.NOT_FOUND)

    def test_empty_json(self):
        site = username.Site("Ex", "https://e.com/{}", empty_json=True)
        self.assertEqual(username._classify(site, self._resp(text="null"), "x"), username.NOT_FOUND)
        self.assertEqual(username._classify(site, self._resp(text='{"id":1}'), "x"), username.FOUND)

    def test_invalid_username(self):
        with self.assertRaises(StalkerError):
            username.search("bad name!")

    def test_site_names_unique(self):
        names = [s.name for s in username.SITES]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
