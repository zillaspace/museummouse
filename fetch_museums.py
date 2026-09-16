"""Fetch every museum with coordinates from Wikidata and write museums.js
beside index.html so the map opens instantly without a live query.

Run:  python3 fetch_museums.py
Needs Python 3.8 or newer and an internet connection. No packages to install.
Takes roughly ten to twenty minutes depending on Wikidata's mood.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "MuseumMouseMap/0.1 (personal research map)",
}
FALLBACK_CLASSES = ["Q33506", "Q207694", "Q2772772", "Q1970365", "Q588140",
                    "Q1595639", "Q3329412", "Q756102", "Q2087181"]
LANGS = "en,fr,de,es,it,pt,nl,sv,da,no,fi,ja,zh,ru,pl,is"


def sparql(query, retries=3):
    url = ENDPOINT + "?format=json&query=" + urllib.parse.quote(query)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:  # timeouts and 429s both land here
            if attempt == retries - 1:
                raise
            time.sleep(5 * (attempt + 1))


def country_query(qid, fallback):
    if fallback:
        values = " ".join("wd:" + c for c in FALLBACK_CLASSES)
        type_clause = f"VALUES ?cls {{ {values} }} ?item wdt:P31 ?cls ."
    else:
        type_clause = "?item wdt:P31/wdt:P279* wd:Q33506 ."
    return f"""SELECT ?item ?itemLabel ?coord ?website WHERE {{
      ?item wdt:P17 wd:{qid} ; wdt:P625 ?coord .
      {type_clause}
      OPTIONAL {{ ?item wdt:P856 ?website . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{LANGS}". }}
    }}"""


def parse(bindings, country):
    out = []
    for b in bindings:
        m = re.search(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", b["coord"]["value"])
        if not m:
            continue
        qid = b["item"]["value"].rsplit("/", 1)[-1]
        name = b.get("itemLabel", {}).get("value", qid)
        if re.fullmatch(r"Q\d+", name):
            continue  # no label in any of our languages
        out.append([qid, name, float(m.group(2)), float(m.group(1)), country,
                    b.get("website", {}).get("value", "")])
    return out


def main():
    print("Fetching the list of countries")
    countries = sparql("""SELECT ?c ?cLabel WHERE {
      ?c wdt:P31 wd:Q6256 . MINUS { ?c wdt:P576 ?d }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } }""")
    seen, museums, failed = set(), [], []
    for i, c in enumerate(countries, 1):
        qid = c["c"]["value"].rsplit("/", 1)[-1]
        name = c["cLabel"]["value"]
        print(f"[{i}/{len(countries)}] {name}", end=" ", flush=True)
        rows = None
        for fallback in (False, True):
            try:
                rows = sparql(country_query(qid, fallback))
                break
            except Exception:
                continue
        if rows is None:
            failed.append(name)
            print("timed out")
            continue
        added = 0
        for m in parse(rows, name):
            if m[0] not in seen:
                seen.add(m[0])
                museums.append(m)
                added += 1
        print(f"{added}")
        time.sleep(0.5)
    with open("museums.js", "w", encoding="utf-8") as f:
        f.write("window.MUSEUMS = ")
        json.dump(museums, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    print(f"\nWrote museums.js with {len(museums)} museums.")
    if failed:
        print("Timed out for:", ", ".join(failed))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Stopped.")
