# Stalker

**English** · [Türkçe](README.tr.md)

A small terminal OSINT toolkit for quick information gathering:

| Tool | What it does |
|---|---|
| **IP Lookup** | Geolocation, ISP / ASN, time zone and map links for any public IPv4 / IPv6 address |
| **Show My IP** | Your public IPv4 and IPv6 address |
| **Phone Number Info** | Country / region, carrier, time zone, number type and every standard format, fully offline |
| **Username Search** | Checks 35 websites in parallel and reports *found / not found / unknown* |

The whole interface (menu, results, help and error messages) is available in **English and Turkish**.

## Installation

Requires **Python 3.8+**. Works on Windows, Linux, macOS and Termux.

```bash
git clone https://github.com/xkudcobi/stalker.git
cd stalker
pip install -r requirements.txt
python -m stalker
```

Or install it as a command:

```bash
pip install .
stalker
```

<details>
<summary>Termux / Debian setup</summary>

```bash
# Termux
pkg install git python
# Debian / Ubuntu / Kali
sudo apt install git python3 python3-pip
```
</details>

## Usage

### Interactive menu

Run `python -m stalker` (or `stalker`) with no arguments:

```
  [1] IP Lookup
  [2] Show My IP
  [3] Phone Number Info
  [4] Username Search
  [5] Language: English (switch to Türkçe)
  [0] Exit
```

After each lookup you can save the results to `results/<type>-<date>.json`.

### Command line

```bash
stalker ip 8.8.8.8                 # look up an IP
stalker ip                         # look up your own IP
stalker myip                       # show your public IPv4 / IPv6
stalker phone +905321234567        # phone number info
stalker phone 02125551234 -r TR    # number without country code + default region
stalker user johndoe               # username search
stalker user johndoe --found-only  # only list sites where it exists
```

Options available on every command:

| Option | Description |
|---|---|
| `--lang en\|tr` | Interface language |
| `--json` | Print results as JSON (handy for scripts) |
| `-o FILE` | Also save results to a JSON file |
| `--timeout SEC` | Per-request timeout (default 10) |
| `--no-color` | Disable colors (also honors `NO_COLOR`) |

### Language

The language is picked in this order: `--lang` flag → `STALKER_LANG` environment variable → the last choice made in the menu → your system language. Choosing a language from the menu is remembered in `~/.config/stalker/config.json`.

## How accurate is it?

- **IP Lookup** uses [ipwho.is](https://ipwho.is) and falls back to [ip-api.com](https://ip-api.com). IP geolocation is approximate: it usually shows the ISP's location, not a person's.
- **Phone Number Info** uses Google's [libphonenumber](https://github.com/google/libphonenumber) data. It describes the *number* (where it was allocated, by which carrier). It cannot locate a phone. Ported numbers may show their original carrier.
- **Username Search** only reports *FOUND* when the site gives a clear answer. Sites that block automated checks or need a login are shown as *UNKNOWN* with a link so you can verify by hand.

## Development

```bash
python -m unittest discover -s tests
```

The tests run offline. Among other things they check that every text exists in both languages with the same placeholders.

Adding a site to the username search is one `Site(...)` line in [`stalker/core/username.py`](stalker/core/username.py).

## Disclaimer

This tool is for education, authorized security testing and investigating your own digital footprint. Only use it on data you are allowed to look up, and follow the laws that apply to you. The authors are not responsible for misuse.

## License

[MIT](LICENSE)
