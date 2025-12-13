# in_note_rhyme_scraper.py
import re
import time
import logging
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://in-note.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
    )
}

# ログ設定
logging.basicConfig(
    filename="rhyme_scrape.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
)

# セッション設定
session = requests.Session()
session.headers.update(HEADERS)

retries = Retry(
    total=5,
    backoff_factor=1.0,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"],
)
adapter = HTTPAdapter(max_retries=retries)
session.mount("https://", adapter)
session.mount("http://", adapter)


def parse_rhyme_page(word_id: int) -> list[dict]:
    """単語ページ /words/<id> から韻候補を抽出して返す"""
    url = f"{BASE_URL}/words/{word_id}"
    try:
        html = session.get(url, timeout=30).text
    except Exception:
        return []

    soup = BeautifulSoup(html, "html.parser")

    h1 = soup.select_one("h1").get_text(strip=True)
    target = re.sub(r"^「|」.*$", "", h1)

    records = []
    pat = re.compile(r"\s*(\d+)\s*文字\s+(.+?)\s+（(.+?)）")
    for li in soup.select("li"):
        m = pat.match(li.get_text(" ", strip=True))
        if m:
            records.append(
                {
                    "source_id": word_id,
                    "target_word": target,
                    "rhyme_word": m.group(2),
                    "reading": m.group(3),
                    "n_chars": int(m.group(1)),
                }
            )
    return records


def collect_word_ids(prefix: str) -> set[int]:
    """
    /words?q=<prefix> 以下のすべての /words/<id> を列挙
    ページネーションを辿って全取得する
    """
    seen_pages = set()
    todo_pages = {f"{BASE_URL}/words?q={prefix}"}
    ids = set()

    while todo_pages:
        url = todo_pages.pop()
        if url in seen_pages:
            continue
        seen_pages.add(url)

        try:
            html = session.get(url, timeout=10).text
        except Exception:
            continue

        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select('a[href^="/words/"]'):
            try:
                word_id = int(a["href"].split("/")[-1])
                ids.add(word_id)
            except ValueError:
                continue

        for a in soup.select('a[href^="/words"]'):
            href = a.get("href", "")
            if href.startswith("/words?page="):
                full_url = BASE_URL + href
                if full_url not in seen_pages:
                    todo_pages.add(full_url)

    return ids


def crawl(prefixes: list[str], out_path: Path, sleep_sec: float = 1.0) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    grouped = {}
    for p in prefixes:
        head = p[0]
        grouped.setdefault(head, []).append(p)

    for head, group in grouped.items():
        all_records = []
        for p in group:
            wids = collect_word_ids(p)
            records_this_prefix = []
            for wid in wids:
                records_this_prefix.extend(parse_rhyme_page(wid))
            all_records.extend(records_this_prefix)
            logging.info(f"prefix: {p} total {len(wids)} words: total {len(records_this_prefix)} records")
            time.sleep(sleep_sec)

        if all_records:
            df = pd.DataFrame(all_records)
            df.to_csv(out_path, mode="a", index=False, header=not out_path.exists())
            logging.info(f"group: {head} written {len(all_records)} records to CSV")


def main() -> None:
    prefixes = [
        chr(i) + chr(j)
        for i in range(ord("あ"), ord("ん") + 1)
        for j in list(range(ord("あ"), ord("ん") + 1)) + [ord("っ")]
        if chr(i) not in "ぁぃぅぇぉゃゅょゎゐゑをん" and chr(j) not in "ぁぃぅぇぉゃゅょゎゐゑをん"
    ]
    print("start crawling...")
    out_path = Path("data") / "in_note_rhymes.csv"
    crawl(prefixes, out_path)


if __name__ == "__main__":
    main()
