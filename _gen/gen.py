#!/usr/bin/env python3
"""Generates the zostaff profile SVGs. Data comes from _gen/gh.json (GitHub GraphQL dump).

Refresh data:  python3 _gen/gen.py --fetch   (needs gh logged in as zostaff)
Rebuild only:  python3 _gen/gen.py
"""
import json, math, os, subprocess, sys, datetime
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "-apple-system,Segoe UI,Inter,Helvetica,Arial,sans-serif"

G1, G2 = "#2bff88", "#d4ff3a"      # pump green -> lime
WHITE, RED = "#f2fff6", "#ff3b6b"
BG, LINE, MUTED, TXT = "#08090a", "#18201b", "#7d8a82", "#e6efe9"

QUERY = '''query{user(login:"zostaff"){followers{totalCount} contributionsCollection{totalCommitContributions
contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
repositories(first:100,ownerAffiliations:OWNER,privacy:PUBLIC,isFork:false){totalCount nodes{name stargazerCount
languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}'''


def fetch():
    raw = subprocess.check_output(["gh", "api", "graphql", "-f", "query=" + QUERY])
    open(os.path.join(HERE, "gh.json"), "wb").write(raw)


def load():
    d = json.load(open(os.path.join(HERE, "gh.json")))["data"]["user"]
    c = d["contributionsCollection"]
    repos = d["repositories"]["nodes"]
    langs = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    tot = sum(langs.values()) or 1
    days = [x for w in c["contributionCalendar"]["weeks"] for x in w["contributionDays"]]
    run = longest = 0
    for x in days:
        run = run + 1 if x["contributionCount"] else 0
        longest = max(longest, run)
    top = max(repos, key=lambda r: r["stargazerCount"])
    return dict(
        stars=sum(r["stargazerCount"] for r in repos),
        repos=len(repos),
        followers=d.get("followers", {}).get("totalCount", 141),
        commits=c["totalCommitContributions"],
        contribs=c["contributionCalendar"]["totalContributions"],
        longest=longest,
        busiest=max(x["contributionCount"] for x in days),
        top=(top["name"], top["stargazerCount"]),
        langs=[(k, 100 * v / tot) for k, v in sorted(langs.items(), key=lambda x: -x[1])[:5]],
        weeks=c["contributionCalendar"]["weeks"],
        updated=datetime.date.today().isoformat(),
    )


# ---------------------------------------------------------------- shared bits
def defs(blur=6):
    return (f'<defs><linearGradient id="pc" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G1}"/>'
            f'<stop offset="1" stop-color="{G2}"/><animate attributeName="x1" values="0;-1;0" dur="6s" repeatCount="indefinite"/>'
            f'<animate attributeName="x2" values="1;2;1" dur="6s" repeatCount="indefinite"/></linearGradient>'
            f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{G1}" stop-opacity=".75"/>'
            f'<stop offset=".5" stop-color="#1c241f"/><stop offset="1" stop-color="{G2}" stop-opacity=".6"/></linearGradient>'
            f'<filter id="gl" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="{blur}" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')


def card(w, h, body, blur=6, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="{MONO}">'
            f'{defs(blur)}<style>.cur{{animation:b 1s steps(1) infinite}}@keyframes b{{50%{{opacity:0}}}}{style}</style>'
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="16" fill="{BG}" stroke="url(#bd)" stroke-width="1.5"/>{body}</svg>')


def head(left, right, x1=32, x2=828, y=42):
    return (f'<text x="{x1}" y="{y}" fill="{MUTED}" font-size="13">{escape(left)}</text>'
            f'<text x="{x2}" y="{y}" fill="{MUTED}" font-size="13" text-anchor="end">{escape(right)}</text>'
            f'<line x1="{x1}" y1="{y+16}" x2="{x2}" y2="{y+16}" stroke="{LINE}"/>')


def fade(begin):
    return f'<animate attributeName="opacity" values="0;1" dur="0.12s" begin="{begin:.2f}s" fill="freeze"/>'


def t(x, y, s, size=15, fill=TXT, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" xml:space="preserve" {extra}>{escape(s)}</text>'


# ---------------------------------------------------------------- ASCII art
FONT = {
    "Z": ["███████╗", "╚══███╔╝", "  ███╔╝ ", " ███╔╝  ", "███████╗", "╚══════╝"],
    "O": [" ██████╗ ", "██╔═══██╗", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
    "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "F": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "██║     ", "╚═╝     "],
    "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
    "N": ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║", "╚═╝  ╚═══╝"],
    "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    ".": ["   ", "   ", "   ", "   ", "██╗", "╚═╝"],
    " ": ["  ", "  ", "  ", "  ", "  ", "  "],
}


def block(word):
    return ["".join(FONT[ch][r] for ch in word) for r in range(6)]


def pill(cols, rows, L=None, R=None, ang=40):
    """pump.fun pill rasterised into characters: list of rows of (char, color)."""
    th = math.radians(ang)
    ar = 2.05  # char cell height / width
    R = R or rows * ar * 0.27
    L = L or R * 1.05
    out = []
    for j in range(rows):
        row = []
        for i in range(cols):
            x = i + 0.5 - cols / 2
            y = -(j + 0.5 - rows / 2) * ar
            u = x * math.cos(th) + y * math.sin(th)
            v = -x * math.sin(th) + y * math.cos(th)
            d = math.hypot(max(abs(u) - L, 0), v)
            if d > R:
                row.append((" ", None)); continue
            green = u > 0
            if d > R - 1.15:
                row.append(("@" if green else "%", "#0f7a45" if green else "#9aa59f"))
            elif abs(u) < 0.55:
                row.append(("/" if j % 2 else "\\", "#2a3a31"))
            elif v > R * 0.42 and abs(u) < L * 0.8:
                row.append(("#" if green else "=", "#9dffc4" if green else "#ffffff"))
            else:
                row.append(("#" if green else "=", G1 if green else WHITE))
        out.append(row)
    return out


def art_rows(rows, x, y, size, lh, begin=0.0, step=0.04, ls=0):
    """render (char,color) rows as text lines with per-color tspans."""
    s = []
    for k, row in enumerate(rows):
        spans, cur, buf = [], None, ""
        for ch, col in row:
            col = col or "none"
            if col != cur and buf:
                spans.append((cur, buf)); buf = ""
            cur = col; buf += ch
        if buf:
            spans.append((cur, buf))
        inner = "".join(f'<tspan fill="{c}">{escape(b)}</tspan>' if c != "none" else escape(b) for c, b in spans)
        s.append(f'<text x="{x}" y="{y + k*lh:.1f}" font-size="{size}" letter-spacing="{ls}" xml:space="preserve" opacity="0">'
                 f'{inner}{fade(begin + k*step)}</text>')
    return "".join(s)


def avatar_ascii(cols=58, rows=29):
    raw = os.path.join(HERE, "avatar.gray")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "avatar.png"), "-vf",
                    f"crop=290:330:85:70,eq=contrast=1.5:brightness=0.02,scale={cols}:{rows},format=gray",
                    "-f", "rawvideo", raw], check=True)
    px = open(raw, "rb").read()
    os.remove(raw)
    ramp = " .,:;i1tfLCG08@"
    shades = ["#0c2a1a", "#11593a", "#1d9a5c", G1, "#b9ffd6", WHITE]
    out = []
    for j in range(rows):
        row = []
        for i in range(cols):
            b = px[j * cols + i] / 255
            ch = ramp[min(len(ramp) - 1, int(b * len(ramp)))]
            row.append((ch, shades[min(len(shades) - 1, int(b * len(shades)))]) if ch != " " else (" ", None))
        out.append(row)
    return out


# ---------------------------------------------------------------- banner
def banner(D):
    W, H = 1500, 500
    word = block("SEND IT.")
    size, lh, x0, y0 = 30, 31, 70, 120
    big = "".join(t(x0, y0 + r * lh, line, size, "url(#bg)", 'letter-spacing="-1.2"') for r, line in enumerate(word))
    ghost_r = "".join(t(x0, y0 + r * lh, line, size, RED, 'letter-spacing="-1.2"') for r, line in enumerate(word))
    ghost_g = "".join(t(x0, y0 + r * lh, line, size, "#7dfcff", 'letter-spacing="-1.2"') for r, line in enumerate(word))
    pl = f'<g class="oc">{art_rows(pill(40, 18), 1010, 92, 17, 19.5, begin=0.3, step=0.05)}</g>'
    av = ""
    bar_len = 30
    bar = "█" * bar_len
    style = (".t{animation:sh 3.2s infinite steps(1)}.r{animation:rr 3.2s infinite steps(1)}.c{animation:cc 3.2s infinite steps(1)}"
             ".oc{animation:fl 3s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-8px)}}"
             ".scan{animation:sc 5s linear infinite}.cur{animation:bl 1.1s infinite steps(1)}"
             "@keyframes sh{0%,100%{transform:translate(0,0)}62%{transform:translate(-6px,2px)}64%{transform:translate(5px,-3px)}66%{transform:translate(-3px,0)}68%{transform:translate(0,0)}86%{transform:translate(4px,1px)}87%{transform:translate(0,0)}}"
             "@keyframes rr{0%,100%{transform:translate(0,0);opacity:0}62%{transform:translate(-12px,0);opacity:.85}66%{transform:translate(8px,3px);opacity:.85}69%{opacity:0}86%{transform:translate(-9px,0);opacity:.7}88%{opacity:0}}"
             "@keyframes cc{0%,100%{transform:translate(0,0);opacity:0}62%{transform:translate(11px,-2px);opacity:.8}66%{transform:translate(-7px,0);opacity:.8}69%{opacity:0}86%{transform:translate(8px,1px);opacity:.7}88%{opacity:0}}"
             "@keyframes sc{0%{transform:translateY(-60px)}100%{transform:translateY(560px)}}"
             "@keyframes bl{50%{opacity:0}}")
    dots = "".join(t(18, 22 + k * 24, ("·   " * 60), 11, "#121a15") for k in range(21))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}">'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G1}"/><stop offset="1" stop-color="{G2}"/>'
            f'<animate attributeName="x1" values="0;-1;0" dur="6s" repeatCount="indefinite"/><animate attributeName="x2" values="1;2;1" dur="6s" repeatCount="indefinite"/></linearGradient>'
            f'<linearGradient id="sl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G1}" stop-opacity="0"/><stop offset=".5" stop-color="{G1}" stop-opacity=".09"/><stop offset="1" stop-color="{G1}" stop-opacity="0"/></linearGradient>'
            f'<filter id="gb" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            f'<clipPath id="bc"><rect x="70" y="341" width="0" height="26"><animate attributeName="width" values="0;{bar_len*12.6:.0f}" dur="3.2s" begin="0.6s" fill="freeze"/></rect></clipPath>'
            f'<pattern id="ln" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern></defs>'
            f'<style>{style}</style><rect width="{W}" height="{H}" fill="#060807"/>'
            f'<g class="r">{ghost_r}</g><g class="c">{ghost_g}</g><g class="t">{big}</g>'
            f'{t(72, 318, "> zostaff, quant dev in the pump.fun trenches", 26, TXT)}'
            f'<rect class="cur" x="782" y="297" width="14" height="26" fill="{G1}"/>'
            f'{t(70, 360, "░" * bar_len, 21, "#1b2a21")}<g clip-path="url(#bc)">{t(70, 360, bar, 21, "url(#bg)")}</g>'
            f'<text x="460" y="360" font-size="20" fill="{MUTED}">bonding curve <tspan fill="{G1}" opacity="0">100%, migrated{fade(3.8)}</tspan></text>'
            f'{t(72, 410, "$ buy the curve, sell the migration, never marry a bag", 20, "#9fb0a6")}'
            f'{pl}{av}'
            f'<text x="1440" y="470" font-size="18" font-weight="700" fill="{WHITE}" text-anchor="end" font-family="{SANS}">dyor, mfers</text>'
            f'</svg>')


# ---------------------------------------------------------------- profile
def profile(D):
    line = "writing bots that buy the curve before you do"
    cw = 10.84
    n = len(line) + 2
    widths = ";".join(str(round(k * cw)) for k in range(n + 1))
    end = 32 + round(n * cw) + 4
    cols = [("(Trenches)", "pump.fun / Solana / Polymarket"),
            ("(Top repo)", f"{D['top'][0]} ★{D['top'][1]}"),
            ("(Stars earned)", f"{D['stars']} across {D['repos']} repos")]
    c = ""
    for k, (a, b) in enumerate(cols):
        x = 32 + k * 270
        if k:
            c += f'<line x1="{x-16}" y1="224" x2="{x-16}" y2="272" stroke="{LINE}"/>'
        c += (f'<text x="{x}" y="236" fill="{MUTED}" font-size="13">{escape(a)}</text>'
              f'<text x="{x}" y="262" fill="#f4fff8" font-size="17" font-weight="700" font-family="{SANS}">{escape(b)}</text>')
    body = (f'<defs><clipPath id="tc"><rect x="30" y="150" width="0" height="40"><animate attributeName="width" values="{widths}" '
            f'dur="3s" begin="0.3s" fill="freeze" calcMode="discrete"/></rect></clipPath></defs>'
            + head("[ profile ]", "")
            + f'<text x="430" y="42" fill="{MUTED}" font-size="13" text-anchor="middle">github.com/zostaff</text>'
            f'<circle class="dot" cx="776" cy="38" r="5" fill="{G1}"/><text x="828" y="42" fill="#b8c8be" font-size="13" text-anchor="end">live</text>'
            f'<text x="30" y="132" font-size="72" font-weight="900" font-family="{SANS}" fill="url(#pc)" letter-spacing="-2">zostaff</text>'
            f'<g clip-path="url(#tc)"><text x="32" y="176" fill="{TXT}" font-size="18"><tspan fill="{G1}">&gt;</tspan> {escape(line)}</text></g>'
            f'<rect class="cur" x="{end}" y="161" width="10" height="20" fill="{G2}"/>'
            f'<line x1="32" y1="206" x2="828" y2="206" stroke="{LINE}"/>{c}')
    return card(860, 298, body, style=".dot{animation:p 1.4s ease-in-out infinite}@keyframes p{50%{opacity:.25}}")


# ---------------------------------------------------------------- terminal
def terminal(D):
    word = block("ZOSTAFF")
    s = ""
    for r, line in enumerate(word):
        s += (f'<text x="24" y="{80 + r*15}" font-size="15.2" letter-spacing="-0.6" fill="url(#pc)" '
              f'xml:space="preserve" opacity="0">{escape(line)}{fade(0.1 + r*0.1)}</text>')
    s += f'<g class="oc">{art_rows(pill(26, 11), 630, 70, 13, 14.2, begin=0.8, step=0.06)}</g>'
    cmds = [
        ("$ whoami", "zostaff, quant dev and memecoin degen, ships at 4am"),
        ("$ ls ~/bots", "grokbot-pumpfun  pumpfunbots-reverse  firstkiller  pumpnuke  curvegap"),
        ("$ cat strategy.txt", "buy the curve, sell the migration, never marry a bag"),
        ("$ echo $PNL", "up only (unverified)"),
    ]
    y, tm = 226, 1.5
    for c, out in cmds:
        s += f'<text x="24" y="{y}" font-size="15" fill="{G1}" opacity="0">{escape(c)}{fade(tm)}</text>'
        s += f'<text x="24" y="{y+22}" font-size="15" fill="{TXT}" opacity="0" xml:space="preserve">{escape(out)}{fade(tm+0.45)}</text>'
        y += 54; tm += 0.8
    s += f'<text x="24" y="{y}" font-size="15" fill="{G1}" opacity="0">${fade(tm)}</text><rect class="cur" x="40" y="{y-14}" width="10" height="18" fill="{G2}"/>'
    body = (f'<circle cx="28" cy="26" r="6" fill="#ff5f57"/><circle cx="48" cy="26" r="6" fill="#febc2e"/><circle cx="68" cy="26" r="6" fill="#28c840"/>'
            f'<text x="430" y="31" fill="{MUTED}" font-size="13" text-anchor="middle">zostaff@pump.fun: ~</text>'
            f'<line x1="1" y1="46" x2="859" y2="46" stroke="{LINE}"/>{s}')
    return card(860, 470, body, blur=3, style=".oc{animation:fl 3s ease-in-out infinite}@keyframes fl{50%{transform:translateY(-6px)}}")


# ---------------------------------------------------------------- stats
def stats(D):
    nums = [(D["stars"], "", "STARS EARNED"), (D["contribs"], "", "CONTRIBUTIONS 12 MO"),
            (D["commits"], "", "COMMITS 12 MO"), (D["repos"], "", "PUBLIC REPOS"),
            (D["followers"], "", "FOLLOWERS"), (D["longest"], " days", "LONGEST STREAK")]
    s = head("[ numbers ]", "github", 32, 402) + head("[ languages ]", "by code size", 458, 828)
    s += f'<line x1="430" y1="30" x2="430" y2="300" stroke="{LINE}"/>'
    for k, (v, unit, lab) in enumerate(nums):
        x = 32 + (k % 2) * 190
        y = 100 + (k // 2) * 74
        s += (f'<text x="{x}" y="{y}" fill="url(#pc)" font-size="32" font-weight="900" font-family="{SANS}">{v}'
              f'<tspan font-size="13" fill="#9aaca2" font-weight="400">{unit}</tspan></text>'
              f'<text x="{x}" y="{y+20}" fill="{MUTED}" font-size="11" letter-spacing="1">{lab}</text>')
    cells = 26
    for k, (name, pct) in enumerate(D["langs"]):
        y = 92 + k * 46
        on = max(1, round(cells * pct / 100))
        s += (f'<text x="458" y="{y}" fill="#f4fff8" font-size="13" font-weight="700">{escape(name)}</text>'
              f'<text x="828" y="{y}" fill="{MUTED}" font-size="12" text-anchor="end">{pct:.1f}%</text>'
              f'<text x="458" y="{y+20}" font-size="13" xml:space="preserve"><tspan fill="{MUTED}">[</tspan>'
              f'<tspan fill="url(#pc)">{"#" * on}</tspan><tspan fill="#26332b">{"-" * (cells - on)}</tspan><tspan fill="{MUTED}">]</tspan></text>')
    s += f'<text x="32" y="306" fill="#3e4a43" font-size="10">updated {D["updated"]}</text>'
    return card(860, 328, s)


# ---------------------------------------------------------------- activity
def activity(D):
    weeks = D["weeks"]
    s = head("[ activity ]", "last 12 months")
    lv = lambda n: 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 9 else 4
    chars = ["░", "░", "▒", "▓", "█"]
    cols = ["#151c18", "#11663e", "#1ea862", G1, G2]
    x0, y0, dx, dy = 78, 108, 13.3, 14.2
    last_m = None
    for wi, w in enumerate(weeks):
        x = x0 + wi * dx
        for di, day in enumerate(w["contributionDays"]):
            dd = datetime.date.fromisoformat(day["date"])
            wd = (dd.weekday() + 1) % 7
            l = lv(day["contributionCount"])
            s += f'<text x="{x:.1f}" y="{y0 + wd*dy:.1f}" font-size="14" fill="{cols[l]}">{chars[l]}</text>'
            if wd == 0 and dd.month != last_m and dd.day <= 7:
                s += f'<text x="{x:.1f}" y="90" fill="{MUTED}" font-size="11">{dd.strftime("%b")}</text>'
                last_m = dd.month
    for wd, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        s += f'<text x="32" y="{y0 + wd*dy:.1f}" fill="{MUTED}" font-size="10">{lab}</text>'
    for k, (v, unit, lab) in enumerate([(D["contribs"], "", "CONTRIBUTIONS"), (D["busiest"], "", "BUSIEST DAY"),
                                        (D["longest"], " days", "LONGEST STREAK")]):
        x = 32 + k * 270
        s += (f'<text x="{x}" y="258" fill="url(#pc)" font-size="32" font-weight="900" font-family="{SANS}">{v}'
              f'<tspan font-size="13" fill="#9aaca2" font-weight="400">{unit}</tspan></text>'
              f'<text x="{x}" y="278" fill="{MUTED}" font-size="11" letter-spacing="1">{lab}</text>')
    s += f'<text x="32" y="306" fill="#3e4a43" font-size="10">updated {D["updated"]}</text>'
    s += f'<text x="828" y="306" font-size="12" text-anchor="end"><tspan fill="#3e4a43" font-size="10">less </tspan>'
    s += "".join(f'<tspan fill="{cols[i]}">{chars[i]}</tspan>' for i in range(5))
    s += '<tspan fill="#3e4a43" font-size="10"> more</tspan></text>'
    return card(860, 324, s)


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        fetch()
    D = load()
    for name, fn in (("banner", banner), ("profile", profile), ("ascii", terminal), ("stats", stats), ("activity", activity)):
        open(os.path.join(OUT, f"{name}.svg"), "w").write(fn(D))
        print("wrote", name)
