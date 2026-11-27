#!/usr/bin/env python3
"""Počítadlo pokusů o útok na VM s veřejnou IP.

Projde log SSH (systemd journal) a access log nginx od okamžiku spuštění počítadla a zapíše souhrn do
/var/www/acmesoft-demo/stats.json, který zobrazuje stránka. Spouští ho systemd timer každých 30 sekund.

    sudo python3 attack_stats.py          # aktualizuje stats.json
    sudo python3 attack_stats.py --vse    # vypíše souhrn za celou historii logů (nic nezapisuje)

Počítání od nuly: sudo rm /var/lib/acmesoft-demo/start
"""
import ipaddress
import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone

STATE_DIR = "/var/lib/acmesoft-demo"
START_FILE = os.path.join(STATE_DIR, "start")
OUT_FILE = "/var/www/acmesoft-demo/stats.json"
NGINX_LOGS = ["/var/log/nginx/access.log.1", "/var/log/nginx/access.log"]
OWN_PATHS = {"/", "/index.html", "/health", "/api/status", "/favicon.ico", "/stats.json"}
LOCAL_IPS = {"127.0.0.1", "::1"}
RECENT = 15

IP = r"(?P<ip>[0-9a-fA-F.:]+)"
SSH_PATTERNS = [
    (re.compile(r"Failed \S+ for (?:invalid user )?(?P<user>\S+) from " + IP + r" port (?P<port>\d+)"),
     "špatné heslo nebo klíč", 4),
    (re.compile(r"Invalid user (?P<user>\S*) from " + IP + r" port (?P<port>\d+)"),
     "neexistující uživatel", 3),
    (re.compile(r"(?:Connection closed by|Connection reset by|Disconnected from|Received disconnect from) "
                r"(?:invalid user |authenticating user )?(?:(?P<user>\S+) )?" + IP + r" port (?P<port>\d+)"),
     "nedokončené přihlášení", 2),
    (re.compile(r"(?:banner exchange: Connection from|Unable to negotiate with|"
                r"Did not receive identification string from) " + IP + r"(?: port (?P<port>\d+))?"),
     "skenování portu", 1),
]
ACCEPTED = re.compile(r"Accepted \S+ for (?P<user>\S+) from " + IP)

HTTP_LINE = re.compile(r'^(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<req>[^"]*)" (?P<status>\d{3}) ')
HTTP_CATEGORIES = [
    ("Pokus o spuštění příkazu", re.compile(r"cgi-bin|shell|cmd=|exec|eval|wget|curl|/bin/|\.\./|%2e%2e|\$\{jndi", re.I)),
    ("Tajné soubory (.env, .git, klíče)", re.compile(r"\.env|\.git|\.aws|\.ssh|id_rsa|credential|secret|config|backup|\.sql", re.I)),
    ("WordPress", re.compile(r"wp-|wordpress|xmlrpc", re.I)),
    ("Admin panely a přihlášení", re.compile(r"phpmyadmin|pma|admin|manager|login|boaform|hnap|console|actuator|jenkins", re.I)),
    ("PHP skripty", re.compile(r"\.php", re.I)),
]


def mask_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip[:20]
    if addr.version == 4:
        return ".".join(ip.split(".")[:3] + ["x"])
    return ":".join(addr.exploded.split(":")[:3]) + "::x"


def is_private(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def start_time(all_history):
    if all_history:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(START_FILE):
        with open(START_FILE, "w") as fh:
            fh.write(datetime.now(timezone.utc).isoformat())
    with open(START_FILE) as fh:
        return datetime.fromisoformat(fh.read().strip())


def ssh_stats(since):
    # Celá historie: adresy správců (úspěšné přihlášení kdykoli) se do útoků nepočítají.
    cmd = ["journalctl", "--no-pager", "-o", "json", "-t", "sshd", "-t", "sshd-session"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    attempts, accepted, admin_ips = {}, 0, set()
    for n, line in enumerate(out.splitlines()):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        msg = entry.get("MESSAGE")
        if not isinstance(msg, str):
            continue
        when = datetime.fromtimestamp(int(entry["__REALTIME_TIMESTAMP"]) / 1e6, timezone.utc)
        ok = ACCEPTED.search(msg)
        if ok:
            admin_ips.add(ok.group("ip"))
            accepted += when >= since
            continue
        for pattern, kind, weight in SSH_PATTERNS:
            m = pattern.search(msg)
            if not m:
                continue
            ip = m.group("ip").rstrip(":")
            key = (ip, m.group("port") or "line%d" % n)
            user = m.groupdict().get("user")
            prev = attempts.get(key)
            if prev is None:
                attempts[key] = {"t": when, "ip": ip, "user": user, "kind": kind, "w": weight}
            else:
                if weight > prev["w"]:
                    prev.update(kind=kind, w=weight)
                if user and not prev["user"]:
                    prev["user"] = user
            break
    all_items = sorted((a for a in attempts.values() if a["ip"] not in admin_ips), key=lambda a: a["t"])
    items = [a for a in all_items if a["t"] >= since]
    history = {"first": all_items[0]["t"].isoformat() if all_items else None,
               "attempts": len(all_items), "ips": len({a["ip"] for a in all_items})}
    return {
        "history": history,
        "attempts": len(items),
        "ips": len({a["ip"] for a in items}),
        "accepted": accepted,
        "kinds": Counter(a["kind"] for a in items).most_common(),
        "top_users": Counter(a["user"] for a in items if a["user"]).most_common(10),
        "recent": [{"t": a["t"].isoformat(), "ip": mask_ip(a["ip"]), "user": a["user"] or "", "what": a["kind"]}
                   for a in items[-RECENT:]][::-1],
    }, Counter(a["ip"] for a in items), admin_ips


def classify(method, path, req):
    if not method or not req or req.startswith("\\x"):
        return "Nesmyslný nebo binární požadavek"
    for name, pattern in HTTP_CATEGORIES:
        if pattern.search(req):
            return name
    return "Ostatní neznámé adresy"


def http_stats(since, ignore_ips):
    total, ips, suspicious, suspicious_all = 0, set(), [], 0
    for path_ in NGINX_LOGS:
        if not os.path.exists(path_):
            continue
        with open(path_, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                m = HTTP_LINE.match(line)
                if not m:
                    continue
                try:
                    when = datetime.strptime(m.group("time"), "%d/%b/%Y:%H:%M:%S %z")
                except ValueError:
                    continue
                ip, req = m.group("ip"), m.group("req")
                parts = req.split(" ")
                method = parts[0] if len(parts) == 3 else ""
                path = parts[1].split("?")[0] if len(parts) == 3 else ""
                # privátní adresy = provoz z virtuální sítě (např. Application Gateway a její sondy), ne z internetu
                if ip in LOCAL_IPS or ip in ignore_ips or is_private(ip) or path == "/stats.json":
                    continue
                if not (method in ("GET", "HEAD") and path in OWN_PATHS):
                    suspicious_all += 1
                if when < since:
                    continue
                total += 1
                ips.add(ip)
                if method in ("GET", "HEAD") and path in OWN_PATHS:
                    continue
                suspicious.append({"t": when.astimezone(timezone.utc), "ip": ip, "req": req,
                                   "status": m.group("status"), "kind": classify(method, path, req)})
    suspicious.sort(key=lambda s: s["t"])
    return {
        "history": {"suspicious": suspicious_all},
        "requests": total,
        "ips": len(ips),
        "suspicious": len(suspicious),
        "kinds": Counter(s["kind"] for s in suspicious).most_common(),
        "recent": [{"t": s["t"].isoformat(), "ip": mask_ip(s["ip"]), "req": s["req"][:90],
                    "status": s["status"], "what": s["kind"]} for s in suspicious[-RECENT:]][::-1],
    }, Counter(s["ip"] for s in suspicious)


def main():
    all_history = "--vse" in sys.argv[1:]
    since = start_time(all_history)
    ssh, ssh_ips, admin_ips = ssh_stats(since)
    http, http_ips = http_stats(since, admin_ips)
    top = (ssh_ips + http_ips).most_common(8)
    stats = {
        "since": since.isoformat(),
        "updated": datetime.now(timezone.utc).isoformat(),
        "ssh": ssh,
        "http": http,
        "top_ips": [[mask_ip(ip), count] for ip, count in top],
    }
    if all_history:
        print(json.dumps({k: stats[k] for k in ("ssh", "http", "top_ips")}, ensure_ascii=False, indent=1))
        return
    tmp = OUT_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(stats, fh, ensure_ascii=False)
    os.chmod(tmp, 0o644)
    os.replace(tmp, OUT_FILE)


if __name__ == "__main__":
    main()
