#!/usr/bin/env python3
"""Convert "ip timezone" lines to FoxyProxy Extended import lines.
Country/ISO code come from the system tz database (zone.tab + iso3166.tab). Optional --map CSV overrides/extends it.
"""
import argparse, re, sys
from pathlib import Path
from urllib.parse import quote

TZ_DIRS = ["/usr/share/zoneinfo", "/usr/lib/zoneinfo", "/usr/share/lib/zoneinfo", "/etc/zoneinfo"]

def find_tzdir():
    cands = [Path(d) for d in TZ_DIRS]
    try:
        import tzdata
        cands.append(Path(tzdata.__file__).parent / "zoneinfo")
    except ImportError:
        pass
    for d in cands:
        if (d / "zone.tab").exists() and (d / "iso3166.tab").exists():
            return d
    sys.exit("zone.tab/iso3166.tab not found. Install tzdata (pip install tzdata) or pass --tzdir.")

def load_tz(tzdir):
    names = {}
    for line in (tzdir / "iso3166.tab").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            cc, name = line.split("\t")[:2]
            names[cc] = name
    zones = {}
    for line in (tzdir / "zone.tab").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            p = line.split("\t")
            zones[p[2]] = p[0]
    return names, zones

def load_overrides(path):
    # CSV: timezone,cc,country   e.g. Europe/Kyiv,UA,Ukraine
    out = {}
    if path:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                tz, cc, country = [x.strip() for x in line.split(",", 2)]
                out[tz] = (cc, country)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--region", help="only this tz prefix, e.g. Europe or America")
    ap.add_argument("--port", type=int, default=1080)
    ap.add_argument("--scheme", default="socks5")
    ap.add_argument("--map", help="CSV overrides: timezone,cc,country")
    ap.add_argument("--tzdir")
    a = ap.parse_args()

    tzdir = Path(a.tzdir) if a.tzdir else find_tzdir()
    names, zones = load_tz(tzdir)
    over = load_overrides(a.map)

    out, seen, missing = [], set(), set()
    for ip, tz in re.findall(r"(\d+\.\d+\.\d+\.\d+)\s+(\S+)", Path(a.input).read_text()):
        if a.region and tz.split("/")[0] != a.region:
            continue
        if ip in seen:
            continue
        seen.add(ip)
        if tz in over:
            cc, country = over[tz]
        elif tz in zones:
            cc = zones[tz]; country = names[cc]
        else:
            missing.add(tz); continue
        city = tz.rsplit("/", 1)[1].replace("_", " ")
        q = lambda s: quote(s, safe="")
        out.append(f"{a.scheme}://{ip}:{a.port}?title={q(cc + ' - ' + city)}&cc={cc}&city={q(city)}&country={q(country)}")

    if missing:
        sys.exit("No country for: " + ", ".join(sorted(missing)) + " (add them via --map)")
    Path(a.output).write_text("\n".join(out) + "\n")
    print(f"Wrote {len(out)} proxies to {a.output}")

if __name__ == "__main__":
    main()
