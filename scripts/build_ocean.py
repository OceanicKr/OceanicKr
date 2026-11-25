import math, random, os, sys, json, urllib.request, datetime
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
LOGIN = os.environ.get("GH_LOGIN", "OceanicKr")

QUERY = """query($login:String!){ user(login:$login){
  followers{totalCount}
  repositories(ownerAffiliations:OWNER, isFork:false, first:100, privacy:PUBLIC){ totalCount
    nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name } } } } }
  contributionsCollection{ totalCommitContributions totalPullRequestContributions totalIssueContributions
    totalRepositoriesWithContributedCommits
    contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount } } } } } }"""

def fetch_stats():
    if os.environ.get("STATS_JSON"):
        return json.load(open(os.environ["STATS_JSON"]))
    tok = os.environ["GITHUB_TOKEN"]
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {tok}", "Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d: raise SystemExit(f"GraphQL error: {d['errors']}")
    u = d["data"]["user"]; cc = u["contributionsCollection"]
    langs = {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    days = [dd for w in cc["contributionCalendar"]["weeks"] for dd in w["contributionDays"]]
    longest = cur = run = 0
    for dd in days:
        run = run + 1 if dd["contributionCount"] > 0 else 0
        longest = max(longest, run)
    for dd in reversed(days):
        if dd["contributionCount"] > 0: cur += 1
        elif dd is days[-1]: continue
        else: break
    return {
        "contributions": cc["contributionCalendar"]["totalContributions"],
        "commits": cc["totalCommitContributions"], "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"], "contributed_to": cc["totalRepositoriesWithContributedCommits"],
        "repos": u["repositories"]["totalCount"], "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"], "langs": langs,
        "days": [dd["contributionCount"] for dd in days], "longest": longest, "current": cur,
    }
ST = fetch_stats()
W = 1200

def ysurf(x, y, comps):
    return y + sum(a*math.sin(2*math.pi*x/wl + ph) for a, wl, ph in comps)

def band(top_y, top_c, bot_y, bot_c, width=2400, step=8):
    p = [f"M0,{ysurf(0,top_y,top_c):.1f}"]
    for x in range(step, width+1, step): p.append(f"L{x},{ysurf(x,top_y,top_c):.1f}")
    for x in range(width, -1, -step): p.append(f"L{x},{ysurf(x,bot_y,bot_c):.1f}")
    return " ".join(p) + " Z"

def line(y, comps, width=2400, step=8):
    return "M" + " L".join(f"{x},{ysurf(x,y,comps):.1f}" for x in range(0, width+1, step))

# all wavelengths divide 1200 so a -1200px translate loops seamlessly
def C(*t): return list(t)
L1 = C((2.5,400,0),(1.2,150,1))
L2 = C((5,600,1),(2,200,2.2),(1,100,.3))
L3 = C((8,600,2),(3.5,300,.5),(1.5,120,1.7))
L4 = C((11,1200,.4),(5,400,2.8),(2,150,.9))
UNDER = C((4,600,1.1),(2,240,.2))


H = 2500; HZ = 300
random.seed(11)
glitter = "".join(
    f'<ellipse cx="{abs(random.gauss(0,35+ (y-300)*0.9)):.0f}" cy="{y}" rx="{random.uniform(6,22):.0f}" ry="1.2" fill="#ffe4a8" class="gl" style="animation-delay:{random.uniform(0,3):.2f}s"/>'
    for y in [random.randint(303,425) for _ in range(110)])
rays = "".join(
    f'<polygon points="{x},440 {x+w},440 {x+w+dx+180},{l} {x+dx},{l}" fill="url(#ray)" class="ry" style="animation-delay:{d}s"/>'
    for x,w,dx,l,d in [(120,60,140,1100,0),(330,40,160,1000,1.5),(560,90,120,1150,.8),(780,50,150,1050,2.2),(950,70,110,1120,1.1),(1100,40,90,980,3)])

def fish(x, y, s, col="#9cc7dc", op=.55):
    return f'<path transform="translate({x},{y}) scale({s})" d="M0,0 C8,-6 20,-6 26,0 L34,-6 L33,0 L34,6 L26,0 C20,6 8,6 0,0 Z" fill="{col}" opacity="{op}"/>'
def school_of(n, spread, sc, col="#9cc7dc", op=.55):
    return "".join(fish(random.randint(0,spread[0]), random.randint(-spread[1],spread[1]), random.uniform(*sc), col, op) for _ in range(n))

def reef_fish(kind, x, y, s, dur, delay, rev=False):
    if kind == "clown":
        body = '<path d="M0,0 C8,-10 24,-10 32,0 L40,-7 L39,0 L40,7 L32,0 C24,10 8,10 0,0 Z" fill="#ff7b25"/><path d="M9,-7 L9,7 M21,-8 L21,8" stroke="#fff" stroke-width="3"/><circle cx="5" cy="-1.5" r="1.4" fill="#111"/>'
    elif kind == "tang":
        body = '<path d="M0,0 C6,-16 26,-16 32,0 L42,-9 L40,0 L42,9 L32,0 C26,16 6,16 0,0 Z" fill="#2d7bf0"/><path d="M6,-3 C14,-10 24,-8 30,0" stroke="#0b1d4a" stroke-width="2.5" fill="none"/><path d="M38,-6 L41,0 L38,6" fill="#ffd23f"/><circle cx="6" cy="-2" r="1.6" fill="#111"/>'
    else:
        body = '<path d="M0,0 C6,-14 24,-14 30,0 L38,-8 L37,0 L38,8 L30,0 C24,14 6,14 0,0 Z" fill="#ffd23f"/><circle cx="6" cy="-2" r="1.6" fill="#111"/>'
    sx = 1 if rev else -1
    return f'<g transform="translate({x},{y})"><g class="patrol" style="animation-duration:{dur}s;animation-delay:-{delay}s"><g transform="scale({sx*s},{s})">{body}</g></g></g>'

def branch(x, y, ang, ln, depth, col, w):
    if depth == 0 or ln < 6: return ""
    x2 = x + ln*math.cos(ang); y2 = y - ln*math.sin(ang)
    out = f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w:.1f}" stroke-linecap="round"/>'
    for da in (-0.45, 0.4):
        out += branch(x2, y2, ang+da+random.uniform(-.12,.12), ln*random.uniform(.68,.8), depth-1, col, max(w*.72,1.2))
    return out
def seafan(x, y, col):
    return f'<g opacity=".85">{branch(x, y, math.pi/2, 46, 6, col, 4)}</g>'

def kelp(x, y, h, delay):
    pts = " ".join(f"{x + 10*math.sin(i*0.9):.1f},{y - i*h/12:.1f}" for i in range(13))
    leaves = "".join(f'<ellipse cx="{x + 10*math.sin(i*0.9) + (12 if i%2 else -12):.1f}" cy="{y - i*h/12:.1f}" rx="13" ry="4" fill="#4f8a3c" opacity=".8" transform="rotate({30 if i%2 else -30} {x + 10*math.sin(i*0.9):.1f} {y - i*h/12:.1f})"/>' for i in range(2,12))
    return f'<g class="kelp" style="transform-origin:{x}px {y}px;animation-delay:-{delay}s"><polyline points="{pts}" fill="none" stroke="#3f7432" stroke-width="4" stroke-linecap="round"/>{leaves}</g>'

def brain(x, y, r, col):
    grooves = "".join(f'<path d="M{x-r+6},{y-r*0.55+i*r*0.28:.1f} q{r*0.25:.1f},-8 {r*0.5:.1f},0 t{r*0.5:.1f},0 t{r*0.5:.1f},0 t{r*0.4:.1f},0" fill="none" stroke="#9c5a2a" stroke-opacity=".6" stroke-width="2"/>' for i in range(4))
    return f'<g><ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r*0.75}" fill="{col}"/>{grooves}</g>'

def tubes(x, y, col):
    return "".join(f'<rect x="{x+dx}" y="{y-h}" width="14" height="{h}" rx="7" fill="{col}"/><ellipse cx="{x+dx+7}" cy="{y-h+3}" rx="5" ry="3" fill="#5a2b10" opacity=".6"/>' for dx,h in [(0,54),(16,72),(32,46),(48,62)])

def anemone(x, y):
    t = "".join(f'<path d="M{x},{y} q{dx*0.5:.0f},{-30} {dx},{-50+abs(dx)*0.3:.0f}" stroke="#ff8fc8" stroke-width="5" stroke-linecap="round" fill="none"/>' for dx in range(-40,41,10))
    return f'<g class="anem" style="transform-origin:{x}px {y}px">{t}<ellipse cx="{x}" cy="{y}" rx="26" ry="9" fill="#d14f8f"/></g>'

reef = f"""
<path d="M540,1260 C600,1140 660,1070 740,1040 C800,1018 860,1000 930,1006 C1000,1012 1060,986 1120,980 C1160,976 1185,982 1200,986 L1200,1400 C1120,1360 1020,1380 920,1340 C780,1300 640,1330 540,1260 Z" fill="url(#rock)"/>
{kelp(1150, 990, 420, 0)}{kelp(1110, 985, 330, 1.2)}{kelp(640, 1110, 280, .6)}
{seafan(800, 1036, "#b45fd6")}
{tubes(860, 1012, "#f2a541")}
{brain(990, 1004, 44, "#e9a35f")}
{seafan(1060, 990, "#ff6f61")}
<g>{branch(720, 1060, math.pi/2+.2, 40, 5, "#ff9e7a", 5)}</g>
<g>{branch(930, 1010, math.pi/2-.15, 34, 5, "#f7d36b", 4.5)}</g>
{anemone(1120, 992)}{anemone(690, 1076)}
"""
reef_school = (reef_fish("clown", 1110, 955, 1.0, 9, 2) + reef_fish("clown", 1140, 940, .8, 11, 5, True) +
               reef_fish("tang", 860, 920, 1.2, 14, 3) + reef_fish("tang", 960, 900, 1.0, 12, 8, True) +
               reef_fish("yellow", 760, 960, 1.0, 10, 1) + reef_fish("yellow", 800, 940, .8, 13, 6, True) +
               reef_fish("yellow", 1040, 925, .9, 15, 4))

shark = """<g class="shark"><g transform="translate(0,1300) scale(1.15)"><g class="shk">
  <path d="M0,0 C20,-18 80,-30 150,-28 L176,-72 L196,-26 C240,-22 275,-12 300,-6 L350,-54 L334,0 L354,38 L298,6 C260,18 200,26 140,26 L118,54 L104,24 C60,20 20,12 0,0 Z" fill="#3b5466"/>
  <path d="M8,4 C40,14 90,22 140,24 C200,24 250,16 296,6 C250,14 200,20 140,20 C90,19 40,13 8,4 Z" fill="#b9c9d2" opacity=".55"/>
  <path d="M235,-14 L248,-28 L254,-12 Z" fill="#2c4352"/>
  <path d="M70,-6 l-3,14 M78,-6 l-3,14 M86,-6 l-3,14" stroke="#24394a" stroke-width="2"/>
  <circle cx="34" cy="-6" r="3" fill="#0b141a"/>
</g></g></g>"""

def squid(cx, cy):
    arms = ""
    for i, dx in enumerate([-24,-16,-8,0,8,16,24]):
        L = 170 + random.randint(-20,20)
        arms += f'<path d="M{dx},64 C{dx-14},{64+L*0.3:.0f} {dx+16},{64+L*0.6:.0f} {dx-6},{64+L}" fill="none" stroke="#7c1f2c" stroke-width="{7 if abs(dx)<20 else 6}" stroke-linecap="round"/>'
    tents = "".join(f'<path d="M{dx},64 C{dx-30},170 {dx+40},270 {dx-10},360" fill="none" stroke="#6a1a25" stroke-width="3" stroke-linecap="round"/><ellipse cx="{dx-10}" cy="368" rx="7" ry="16" fill="#8c2a35"/>' for dx in [-10,10])
    spots = "".join(f'<circle cx="{random.randint(-22,22)}" cy="{random.randint(-120,30)}" r="{random.uniform(2,4.5):.1f}" fill="#d9606c" opacity=".7"/>' for _ in range(22))
    photo = "".join(f'<circle cx="{random.randint(-26,26)}" cy="{random.randint(-110,40)}" r="1.6" fill="#9ff7ff" class="tw"/>' for _ in range(10))
    return f"""<g transform="translate({cx},{cy})"><g class="sq">
  <g class="arms">{tents}{arms}</g>
  <path d="M0,-170 L52,-118 L22,-104 Z" fill="#7c1f2c"/><path d="M0,-170 L-52,-118 L-22,-104 Z" fill="#7c1f2c"/>
  <path d="M0,-170 C34,-120 44,-20 34,44 C24,62 -24,62 -34,44 C-44,-20 -34,-120 0,-170 Z" fill="#8c2a35"/>
  <path d="M-8,-150 C-20,-90 -24,-20 -18,30" stroke="#b5444f" stroke-width="6" stroke-opacity=".5" fill="none"/>
  {spots}{photo}
  <ellipse cx="0" cy="58" rx="32" ry="18" fill="#8c2a35"/>
  <circle cx="-17" cy="56" r="8" fill="#0b0f12"/><circle cx="17" cy="56" r="8" fill="#0b0f12"/>
  <circle cx="-15" cy="53" r="2.4" fill="#e8fffb"/><circle cx="19" cy="53" r="2.4" fill="#e8fffb"/>
</g></g>"""

def lantern(x, y, s):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M0,0 C8,-6 20,-6 26,0 L34,-6 L33,0 L34,6 L26,0 C20,6 8,6 0,0 Z" fill="#1c3442"/><circle cx="5" cy="1" r="2.2" fill="#7ff5e3" class="tw"/><circle cx="14" cy="3" r="1.2" fill="#7ff5e3" class="tw"/><circle cx="20" cy="2.5" r="1.2" fill="#7ff5e3" class="tw"/></g>'
lanterns = "".join(lantern(random.randint(0,300), random.randint(-60,60), random.uniform(.7,1.1)) for _ in range(12))

snow = "".join(
    f'<circle cx="{random.randint(0,1200)}" cy="{random.randint(1150,2480)}" r="{random.choice([.8,1,1.3,1.6])}" fill="#cfe6f0" opacity="{random.uniform(.15,.5):.2f}" class="sn" style="animation-duration:{random.uniform(14,30):.0f}s;animation-delay:-{random.uniform(0,30):.0f}s"/>'
    for _ in range(200))

def jelly(cx, cy, s, hue):
    tent = "".join(
        f'<path d="M{x},4 C{x-8},30 {x+8},55 {x-4},85 C{x-12},110 {x+6},130 {x-2},{150+abs(x)}" fill="none" stroke="{hue}" stroke-opacity=".45" stroke-width="1.6"/>'
        for x in [-26,-14,-3,8,19,28])
    arms = "".join(f'<path d="M{x},4 C{x+6},25 {x-6},40 {x+3},62" fill="none" stroke="{hue}" stroke-opacity=".7" stroke-width="5" stroke-linecap="round"/>' for x in [-8,6])
    return f"""<g transform="translate({cx},{cy}) scale({s})">
  <circle r="70" fill="url(#jglow)"/>
  <g class="tent">{tent}{arms}</g>
  <path d="M-42,4 C-44,-46 44,-46 42,4 C32,12 22,0 12,8 C2,0 -8,12 -18,4 C-26,12 -36,0 -42,4 Z" fill="{hue}" fill-opacity=".38" stroke="{hue}" stroke-opacity=".8" stroke-width="1.5"/>
  <path d="M-26,-6 C-24,-30 24,-30 26,-6" fill="none" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>
</g>"""

def gauge_mark(y, depth):
    return f'<circle cx="70" cy="{y}" r="6" fill="#0d1117" stroke="#6fd3e8" stroke-width="2"/><text x="96" y="{y+5}" class="dep">▼ {depth}</text>'
ticks = "".join(f'<line x1="{64 if i%4 else 58}" y1="{y}" x2="70" y2="{y}" stroke="#6fd3e8" stroke-opacity=".35"/>' for i,y in enumerate(range(470,H-10,30)))

def item(y, head, desc):
    return f'<text x="96" y="{y}" class="it">{head}</text><text x="96" y="{y+28}" class="ds">{desc}</text>'


def fmt(n): return f"{n:,}"
def pl(n, one, many): return f"{fmt(n)} {one if n == 1 else many}"

year_lines = [
    f'{pl(ST["contributions"], "contribution", "contributions")} · {pl(ST["commits"], "commit", "commits")}',
    f'{pl(ST["prs"], "pull request", "pull requests")} · {pl(ST["contributed_to"], "repo", "repos")} contributed to',
]
tot = sum(ST["langs"].values()) or 1
top = sorted(ST["langs"].items(), key=lambda kv: -kv[1])[:6]
lang = [f"{n} {100*v/tot:.1f}%" for n, v in top]
lang_lines = [" · ".join(lang[:3]), " · ".join(lang[3:])]
all_lines = [
    f'{pl(ST["repos"], "public repo", "public repos")} · {pl(ST["stars"], "star", "stars")}',
    f'longest streak {pl(ST["longest"], "day", "days")} · current streak {pl(ST["current"], "day", "days")}',
]
def block(y, title, lines):
    out = f'<text x="96" y="{y}" class="it">{title}</text>'
    for i, l in enumerate(l for l in lines if l):
        out += f'<text x="96" y="{y + 30 + i*28}" class="ds">{l}</text>'
    return out
stats_year = block(1070, "GitHub, last 12 months", year_lines)
stats_lang = block(1690, "Languages", lang_lines)
stats_all  = block(2090, "GitHub, all time", all_lines)

def _lerp(c1, c2, t):
    a = [int(c1[i:i+2],16) for i in (1,3,5)]; b = [int(c2[i:i+2],16) for i in (1,3,5)]
    return "#" + "".join(f"{round(x+(y-x)*t):02x}" for x,y in zip(a,b))
_stops = [(0,"#fffef5"),(.42,"#fff8d2"),(.68,"#ffe691"),(.84,"#ffc04a"),(.94,"#ff9a2e"),(1,"#ff7a1f")]
def _col(t):
    for (t0,c0),(t1,c1) in zip(_stops,_stops[1:]):
        if t <= t1: return _lerp(c0,c1,(t-t0)/(t1-t0))
    return _stops[-1][1]
GLOW = "".join(f'<circle cx="-30" cy="173.5" r="{62 + 150*(1-i/70)**1.7:.1f}" fill="{_lerp("#f06a24", "#ffe08a", i/70)}" fill-opacity=".035"/>' for i in range(70))
SUN = "".join(f'<circle cx="-30" cy="173.5" r="{62*(1-i/60):.2f}" fill="{_col(1-i/60)}"/>' for i in range(60))

ocean = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#140202"/><stop offset=".5" stop-color="#6e1209"/><stop offset=".85" stop-color="#d63c12"/><stop offset="1" stop-color="#ff9a4d"/>
  </linearGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#fffbe6"/><stop offset=".45" stop-color="#fff1a8"/><stop offset=".78" stop-color="#ffd25a"/><stop offset=".93" stop-color="#ffa531"/><stop offset="1" stop-color="#ff7a1f"/></radialGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="#ff8a2a" stop-opacity=".55"/><stop offset=".5" stop-color="#e2400f" stop-opacity=".18"/><stop offset="1" stop-color="#e2400f" stop-opacity="0"/></radialGradient>
  <radialGradient id="halo2"><stop offset=".45" stop-color="#ffd27a" stop-opacity=".75"/><stop offset="1" stop-color="#ff9a3d" stop-opacity="0"/></radialGradient>
  <linearGradient id="deep" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1f5b7c"/><stop offset=".15" stop-color="#184d6e"/><stop offset=".33" stop-color="#113857"/><stop offset=".52" stop-color="#0c263c"/><stop offset=".72" stop-color="#09172a"/><stop offset=".88" stop-color="#0b1220"/><stop offset="1" stop-color="#0d1117"/>
  </linearGradient>
  <linearGradient id="rock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a3f5e"/><stop offset=".3" stop-color="#3a3556"/><stop offset=".75" stop-color="#183a58" stop-opacity="0"/></linearGradient>
  <linearGradient id="ray" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd9a8" stop-opacity=".12"/><stop offset="1" stop-color="#9fd6ff" stop-opacity="0"/></linearGradient>
  <radialGradient id="jglow"><stop offset="0" stop-color="#c79bff" stop-opacity=".35"/><stop offset="1" stop-color="#c79bff" stop-opacity="0"/></radialGradient>
  <filter id="ripples" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.0035 0.09" numOctaves="3" seed="4"/>
    <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 .72  0 0 0 0 .5  2.4 0 0 0 -1.35"/>
  </filter>
  <filter id="clouds" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.0025 0.025" numOctaves="4" seed="9"/>
    <feColorMatrix type="matrix" values="0 0 0 0 .35  0 0 0 0 .05  0 0 0 0 .03  1.9 0 0 0 -1.0"/>
  </filter>
  <clipPath id="sky-clip"><rect width="{W}" height="{HZ+3}"/></clipPath>
  <clipPath id="water-clip"><rect y="{HZ+2}" width="{W}" height="140"/></clipPath>
  <style>
    .wv {{ animation: drift linear infinite; }}
    @keyframes drift {{ to {{ transform: translateX(-1200px); }} }}
    .a1 {{ animation-duration: 60s; }} .a2 {{ animation-duration: 40s; }} .a3 {{ animation-duration: 28s; }} .a4 {{ animation-duration: 20s; }}
    .gl {{ animation: glint 2.2s ease-in-out infinite; opacity: .2; }}
    @keyframes glint {{ 50% {{ opacity: .95; }} }}
    .ry {{ animation: sway 7s ease-in-out infinite; transform-origin: 600px 440px; }}
    @keyframes sway {{ 0%,100% {{ opacity: .55; transform: skewX(-2deg); }} 50% {{ opacity: 1; transform: skewX(3deg); }} }}
    .sch {{ animation: swim 38s linear infinite; }} .sch2 {{ animation: swim 52s linear infinite; animation-delay: -20s; }}
    .sch3 {{ animation: swim 70s linear infinite; animation-delay: -35s; }}
    @keyframes swim {{ from {{ transform: translateX(-340px); }} to {{ transform: translateX(1300px); }} }}
    .wig {{ animation: wig .6s ease-in-out infinite alternate; }}
    @keyframes wig {{ to {{ transform: translateY(3px); }} }}
    .patrol {{ animation: patrol ease-in-out infinite alternate; }}
    @keyframes patrol {{ from {{ transform: translate(0,0); }} 50% {{ transform: translate(-40px,-8px); }} to {{ transform: translate(-80px,4px); }} }}
    .kelp {{ animation: kelp 6s ease-in-out infinite alternate; }}
    @keyframes kelp {{ from {{ transform: skewX(-4deg); }} to {{ transform: skewX(5deg); }} }}
    .anem {{ animation: anem 3s ease-in-out infinite alternate; }}
    @keyframes anem {{ from {{ transform: skewX(-8deg); }} to {{ transform: skewX(8deg); }} }}
    .shark {{ animation: cruise 48s linear infinite; animation-delay: -12s; }}
    @keyframes cruise {{ from {{ transform: translateX(1300px); }} to {{ transform: translateX(-500px); }} }}
    .shk {{ animation: shk 4s ease-in-out infinite; }}
    @keyframes shk {{ 50% {{ transform: translateY(-14px) rotate(-1deg); }} }}
    .sq {{ animation: jet 9s ease-in-out infinite; }}
    @keyframes jet {{ 0%,100% {{ transform: translateY(0); }} 20% {{ transform: translateY(-40px); }} 60% {{ transform: translateY(-10px); }} }}
    .arms {{ animation: arms 3s ease-in-out infinite alternate; transform-origin: 0 64px; }}
    @keyframes arms {{ from {{ transform: skewX(-7deg) scaleY(1.04); }} to {{ transform: skewX(7deg) scaleY(.94); }} }}
    .tw {{ animation: tw 3s ease-in-out infinite; }}
    @keyframes tw {{ 50% {{ opacity: .25; }} }}
    .bob {{ animation: bob 6s ease-in-out infinite; }} .bob2 {{ animation: bob 8s ease-in-out infinite; animation-delay: -3s; }}
    @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-26px); }} }}
    .tent {{ animation: tent 3s ease-in-out infinite alternate; transform-origin: 0 0; }}
    @keyframes tent {{ from {{ transform: skewX(-6deg); }} to {{ transform: skewX(6deg); }} }}
    .sn {{ animation: fall linear infinite; }}
    @keyframes fall {{ from {{ transform: translate(0,-60px); }} to {{ transform: translate(14px,60px); }} }}
    .num {{ font: 700 40px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #e3f4fb; }}
    .lbl {{ font: 500 15px 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; letter-spacing: 1px; fill: #8fb4c8; }}
    .lg {{ font: 500 17px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #b9d6e3; }}
    .sweep {{ animation: sweep 6s linear infinite; }}
    @keyframes sweep {{ from {{ transform: translateX(0); opacity: .7; }} to {{ transform: translateX(546px); opacity: .1; }} }}
    .name {{ font: 800 66px 'Segoe UI', Helvetica, Arial, sans-serif; letter-spacing: 12px; fill: #ffe9d6; }}
    .sub {{ font: 500 18px 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; letter-spacing: 3px; fill: #ffbe8f; }}
    .dep {{ font: 700 15px 'SFMono-Regular', Consolas, 'Liberation Mono', monospace; letter-spacing: 2px; fill: #6fd3e8; }}
    .h {{ font: 700 32px 'Segoe UI', Helvetica, Arial, sans-serif; letter-spacing: 2px; fill: #e3f4fb; }}
    .it {{ font: 600 21px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #d2ebf5; }}
    .ds {{ font: 400 19px 'Segoe UI', Helvetica, Arial, sans-serif; fill: #9cc0d2; }}
  </style>
</defs>

<rect width="{W}" height="{HZ+10}" fill="url(#sky)"/>
<rect width="{W}" height="{HZ-40}" filter="url(#clouds)" opacity=".8"/>
{GLOW}
{SUN}
<text x="1120" y="165" text-anchor="end" class="name">SAGAR KUMAR</text>
<text x="1116" y="205" text-anchor="end" class="sub">CS @ BITS PILANI</text>

<rect y="{HZ+60}" width="{W}" height="{H-HZ-60}" fill="url(#deep)"/>
{rays}

<g class="wv a1"><path d="{band(HZ, L1, HZ+60, C((0,600,0)))}" fill="#8f2a10"/></g>
<g clip-path="url(#water-clip)"><rect y="{HZ+2}" width="{W}" height="140" filter="url(#ripples)" opacity=".55"/></g>
{glitter}
<g class="wv a2"><path d="{band(HZ+22, L2, HZ+90, C((0,600,0)))}" fill="#5c160a" opacity=".92"/><path d="{line(HZ+22, L2)}" fill="none" stroke="#ff9d5c" stroke-opacity=".45" stroke-width="1.4" stroke-dasharray="40 14 8 22"/></g>
<g class="wv a3"><path d="{band(HZ+55, L3, HZ+120, C((0,600,0)))}" fill="#3a0d07"/><path d="{line(HZ+55, L3)}" fill="none" stroke="#ff8a4a" stroke-opacity=".35" stroke-width="1.6" stroke-dasharray="60 18 10 30"/></g>
<g class="wv a4"><path d="{band(HZ+95, L4, HZ+140, UNDER)}" fill="#1f0705"/><path d="{line(HZ+95, L4)}" fill="none" stroke="#ff7a3a" stroke-opacity=".3" stroke-width="2" stroke-dasharray="80 20 14 40"/><path d="{line(HZ+140, UNDER)}" fill="none" stroke="#ffb27a" stroke-opacity=".55" stroke-width="2.5"/></g>

<line x1="70" y1="470" x2="70" y2="{H-10}" stroke="#6fd3e8" stroke-opacity=".25" stroke-width="2"/>
{ticks}

<g class="sch"><g transform="translate(0,520)"><g class="wig">{school_of(30,(300,45),(.6,1.1))}</g></g></g>
{reef}
{reef_school}

{gauge_mark(600, "30 m")}
<text x="96" y="650" class="h">What I do</text>
{item(702, "Aura farmer", "full-time harvest, yields vary with the moon")}
{item(782, "Robot whisperer", "they never listen, I never stop talking")}
{item(862, "Bug breeder", "every fix hatches two more, sustainable farming")}
{item(942, "Sleep speedrunner", "any% under 4 hours, world record pending")}

<g class="sch2"><g transform="translate(0,1180)"><g class="wig">{school_of(18,(200,30),(.5,.8))}</g></g></g>
{shark}

<g class="bob">{jelly(1000, 1560, 1.25, "#c79bff")}</g>
<g class="bob2">{jelly(860, 1760, .8, "#8fd8ff")}</g>
{snow}

{stats_year}
{stats_lang}
{stats_all}
{gauge_mark(1500, "1,000 m")}
<text x="96" y="1550" class="h">Tools</text>
<text x="96" y="1598" class="it">Python · C++ · Java · ROS 2</text>
<text x="96" y="1632" class="it">PyTorch · Gazebo · OpenCV · Linux</text>

{squid(960, 2060)}
<g class="sch3"><g transform="translate(0,2230)"><g class="wig">{lanterns}</g></g></g>

{gauge_mark(1920, "2,000 m")}
<text x="96" y="1970" class="h">Off the clock</text>
<text x="96" y="2018" class="it">Tennis · horror films · building things that move</text>

{gauge_mark(2330, "4,000 m")}
</svg>"""
import hashlib, glob, re
h = hashlib.sha1(ocean.encode()).hexdigest()[:8]
name = f"ocean-{h}.svg"
for old in glob.glob(f"{out}/ocean*.svg"):
    if not old.endswith(name): os.remove(old)
open(f"{out}/{name}","w").write(ocean)
if os.path.exists("README.md"):
    r = open("README.md").read()
    open("README.md","w").write(re.sub(r"\./assets/ocean[^\"]*\.svg", f"./assets/{name}", r))
print("wrote", name)

