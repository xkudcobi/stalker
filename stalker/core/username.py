"""Check whether a username exists on popular websites.

Each site declares how "not found" looks (status code, page text, or an empty
API answer). Anything ambiguous - blocks, captchas, login walls - is reported
as UNKNOWN instead of guessing, so FOUND results can be trusted.
"""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import requests

from stalker.net import DEFAULT_TIMEOUT, StalkerError, session

FOUND = "found"
NOT_FOUND = "not_found"
UNKNOWN = "unknown"

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,40}$")


@dataclass(frozen=True)
class Site:
    name: str
    profile: str                      # URL shown to the user, `{}` = username
    probe: str | None = None          # URL actually requested (defaults to `profile`)
    absent_status: tuple = (404,)     # status codes meaning "no such user"
    absent_text: tuple = ()           # body snippets meaning "no such user"
    present_text: tuple = ()          # body snippets required for "user exists" (`{}` = username)
    missing_is_absent: bool = False   # no present_text match means NOT_FOUND (else UNKNOWN)
    manual: bool = False              # cannot be checked automatically; always UNKNOWN
    absent_redirect: str | None = None  # final URL substring meaning "no such user"
    empty_json: bool = False          # probe returns null / [] / {} when missing
    pattern: str | None = None        # usernames the site accepts (regex)
    browser_ua: bool = True
    headers: dict = field(default_factory=dict)

    def accepts(self, username: str) -> bool:
        return self.pattern is None or re.fullmatch(self.pattern, username) is not None


SITES: tuple[Site, ...] = (
    Site("GitHub", "https://github.com/{}", probe="https://api.github.com/users/{}",
         browser_ua=False, pattern=r"[A-Za-z0-9-]{1,39}"),
    Site("GitLab", "https://gitlab.com/{}", probe="https://gitlab.com/api/v4/users?username={}",
         empty_json=True, browser_ua=False),
    Site("Reddit", "https://www.reddit.com/user/{}", probe="https://www.reddit.com/user/{}/about.json",
         browser_ua=False, pattern=r"[A-Za-z0-9_-]{3,20}"),
    Site("YouTube", "https://www.youtube.com/@{}"),
    Site("Twitch", "https://www.twitch.tv/{}", manual=True, pattern=r"[A-Za-z0-9_]{4,25}"),
    Site("Instagram", "https://www.instagram.com/{}/",
         probe="https://www.instagram.com/api/v1/users/web_profile_info/?username={}",
         headers={"X-IG-App-ID": "936619743392459"}, pattern=r"[A-Za-z0-9._]{1,30}"),
    Site("TikTok", "https://www.tiktok.com/@{}",
         absent_text=('"statusCode":10221', '"statusCode":10202'),
         present_text=('"uniqueId":"',)),
    Site("X (Twitter)", "https://x.com/{}"),
    Site("Facebook", "https://www.facebook.com/{}"),
    Site("LinkedIn", "https://www.linkedin.com/in/{}"),
    Site("Pinterest", "https://www.pinterest.com/{}/", absent_redirect="/?show_error=true",
         present_text=('"username":"{}"',), missing_is_absent=True),
    Site("Tumblr", "https://{}.tumblr.com", pattern=r"[A-Za-z0-9-]{1,32}"),
    Site("SoundCloud", "https://soundcloud.com/{}"),
    Site("Snapchat", "https://www.snapchat.com/add/{}", pattern=r"[A-Za-z][A-Za-z0-9._-]{2,14}"),
    Site("Telegram", "https://t.me/{}", present_text=('class="tgme_page_title"',),
         missing_is_absent=True,
         pattern=r"[A-Za-z][A-Za-z0-9_]{4,31}"),
    Site("Medium", "https://medium.com/@{}"),
    Site("DEV Community", "https://dev.to/{}"),
    Site("Behance", "https://www.behance.net/{}"),
    Site("Dribbble", "https://dribbble.com/{}"),
    Site("Flickr", "https://www.flickr.com/people/{}"),
    Site("Vimeo", "https://vimeo.com/{}"),
    Site("Spotify", "https://open.spotify.com/user/{}", manual=True),
    Site("Steam", "https://steamcommunity.com/id/{}",
         absent_text=("The specified profile could not be found",)),
    Site("Chess.com", "https://www.chess.com/member/{}",
         probe="https://api.chess.com/pub/player/{}", browser_ua=False),
    Site("Lichess", "https://lichess.org/@/{}", probe="https://lichess.org/api/user/{}",
         browser_ua=False),
    Site("Hacker News", "https://news.ycombinator.com/user?id={}",
         probe="https://hacker-news.firebaseio.com/v0/user/{}.json",
         empty_json=True, browser_ua=False),
    Site("Docker Hub", "https://hub.docker.com/u/{}",
         probe="https://hub.docker.com/v2/users/{}/", browser_ua=False),
    # PyPI sometimes serves a JS challenge page with status 200; only trust the real page.
    Site("PyPI", "https://pypi.org/user/{}/", present_text=('name="availableLanguages"',)),
    Site("Keybase", "https://keybase.io/{}",
         probe="https://keybase.io/_/api/1.0/user/lookup.json?usernames={}",
         absent_text=('"them":[null]',), browser_ua=False),
    Site("Linktree", "https://linktr.ee/{}"),
    Site("Patreon", "https://www.patreon.com/{}"),
    Site("Gravatar", "https://gravatar.com/{}", probe="https://en.gravatar.com/{}.json",
         browser_ua=False),
    Site("Quora", "https://www.quora.com/profile/{}"),
    Site("Product Hunt", "https://www.producthunt.com/@{}"),
    Site("We Heart It", "https://weheartit.com/{}"),
)


def _classify(site: Site, resp: requests.Response, username: str) -> str:
    status = resp.status_code
    if status in site.absent_status:
        return NOT_FOUND
    if site.absent_redirect and site.absent_redirect in resp.url:
        return NOT_FOUND
    if status != 200:
        # 403 / 429 / 5xx: blocked or rate limited, we cannot tell.
        return UNKNOWN

    body = resp.text
    if site.empty_json:
        stripped = body.strip()
        return NOT_FOUND if stripped in ("null", "[]", "{}", "") else FOUND
    if any(snippet in body for snippet in site.absent_text):
        return NOT_FOUND
    if site.present_text:
        if any(snippet.replace("{}", username) in body for snippet in site.present_text):
            return FOUND
        return NOT_FOUND if site.missing_is_absent else UNKNOWN
    if site.absent_text or site.absent_status != (404,):
        return FOUND
    # Plain status check: only trust 200 when we were not bounced to a login page.
    if re.search(r"/(login|signin|accounts/login|authwall|checkpoint)", resp.url):
        return UNKNOWN
    return FOUND


def check_site(site: Site, username: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    url = site.profile.format(username)
    result = {"site": site.name, "url": url, "status": UNKNOWN}
    if site.manual:
        return result
    if not site.accepts(username):
        result["status"] = NOT_FOUND
        return result
    http = session(browser=site.browser_ua)
    http.headers.update(site.headers)
    try:
        resp = http.get((site.probe or site.profile).format(username), timeout=timeout,
                        allow_redirects=True)
        result["status"] = _classify(site, resp, username)
    except requests.RequestException:
        result["status"] = UNKNOWN
    return result


def normalize(username: str) -> str:
    """Strip whitespace and a leading @; raise StalkerError if the name is unusable."""
    cleaned = username.strip().lstrip("@")
    if not USERNAME_RE.match(cleaned):
        raise StalkerError("user.invalid", value=cleaned)
    return cleaned


def search(username: str, timeout: float = DEFAULT_TIMEOUT, workers: int = 16,
           sites: tuple[Site, ...] = SITES) -> list[dict]:
    """Check every site in parallel; results keep the order of `sites`."""
    username = normalize(username)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda s: check_site(s, username, timeout), sites))
