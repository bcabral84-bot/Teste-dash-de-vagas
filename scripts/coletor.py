#!/usr/bin/env python3
"""Coletor do Banco de Vagas.

Lê os quadros públicos de vagas (Greenhouse, Lever, Ashby, SmartRecruiters,
Recruitee, Teamtailor) das empresas em data/empresas.json e a busca do Himalayas, filtra por
função (data/funcoes.json) e por elegibilidade para quem mora no Brasil, e
grava candidatas em out/.

Uso:
  python3 scripts/coletor.py                      # coleta tudo
  python3 scripts/coletor.py --banco DIR          # compara com o banco exportado
                                                  # (pasta com jobs/*.json do ArtifactData)
  python3 scripts/coletor.py --so-fontes          # só quadros das empresas
  python3 scripts/coletor.py --so-himalayas       # só Himalayas

Saídas (out/):
  candidatas.json   vagas encontradas hoje que não estão no banco
  vistas.json       todas as vagas encontradas hoje (para conferir status)
  sumidas.json      vagas do banco com link de quadro oficial que não aparecem mais
  relatorio.txt     resumo legível

Nunca acessa o LinkedIn.
"""
import argparse, concurrent.futures as cf, datetime as dt, glob, hashlib, html, json, os, re, sys, time
import urllib.request, urllib.error, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "out")
UA = {"User-Agent": "Mozilla/5.0 (banco-de-vagas; contato via dono do repositorio)"}
TODAY = dt.date.today()

# ---------------------------------------------------------------- utilidades

def fetch_json(url, data=None, headers=None, tries=2):
    h = dict(UA); h.update(headers or {})
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None
            if e.code == 429:
                time.sleep(3 + 3 * i)
        except Exception:
            time.sleep(1 + i)
    return None

def load(name, default=None):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def iso(ts):
    """Aceita epoch (s ou ms) ou string ISO; devolve AAAA-MM-DD."""
    if ts in (None, ""):
        return ""
    if isinstance(ts, (int, float)):
        if ts > 1e12:
            ts = ts / 1000
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", str(ts))
    return m.group(1) if m else ""

def days_since(d):
    try:
        return (TODAY - dt.date.fromisoformat(d)).days
    except Exception:
        return None

def norm(s):
    s = (s or "").lower()
    s = re.sub(r"\[.*?\]|\(.*?\)", " ", s)
    s = re.sub(r"\b(op|job|vaga|req)\s*-?\s*\d+\b", " ", s)
    s = re.sub(r"[^a-z0-9áéíóúâêôãõç ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def job_key(company, title):
    return hashlib.sha1((norm(company) + "|" + norm(title)).encode()).hexdigest()[:12]

def clean_title(t):
    t = html.unescape(t or "").strip()
    t = re.sub(r"^\(\d+\)\s*", "", t)            # (1425) Lead ...
    t = re.sub(r"^\[\s*job\s*-\s*\d+\s*\]\s*", "", t, flags=re.I)  # [ Job - 31855] ...
    return re.sub(r"\s+", " ", t)

# ---------------------------------------------------------------- função e aderência

FUNCOES = load("funcoes.json")
ROLE_RULES = [(r["code"], re.compile(r["regex"], re.I)) for r in FUNCOES["roles"]]
EXCLUDE = re.compile(FUNCOES["exclude"], re.I)

def classify(title):
    if EXCLUDE.search(title):
        return None
    for code, rx in ROLE_RULES:
        if rx.search(title):
            return code
    return None

SENIOR = [("Diretoria", r"\b(director|diretor|head of|vp|vice president)\b"),
          ("Principal", r"\bprincipal\b"),
          ("Lead", r"\b(lead|l[ií]der)\b"),
          ("Sênior", r"\b(senior|sr\.?|s[eê]nior)\b"),
          ("Pleno", r"\b(mid|pleno|intermediate|ii)\b"),
          ("Júnior", r"\b(junior|jr\.?|j[uú]nior|associate|trainee|intern|estagi)")]

def seniority(title):
    for label, rx in SENIOR:
        if re.search(rx, title, re.I):
            return label
    return ""

FIT_LOW = re.compile(FUNCOES.get("fit_low", "$^"), re.I)

def fit_for(role, sen, title=""):
    base = FUNCOES["fit"].get(role, "baixa")
    order = ["baixa", "média", "alta"]
    i = order.index(base)
    if sen == "Júnior":
        i = max(0, i - 1)
    if FIT_LOW.search(title):
        i = 0
    return order[i]

# ---------------------------------------------------------------- elegibilidade

BR_CITY = r"s[aã]o paulo|rio de janeiro|belo horizonte|curitiba|porto alegre|florian[oó]polis|recife|campinas|fortaleza|bras[ií]lia|salvador|goi[aâ]nia|joinville|blumenau|uberl[aâ]ndia|londrina|maring[aá]|sorocaba|barueri|alphaville|manaus|natal|jo[aã]o pessoa|vit[oó]ria"
RX_BR = re.compile(r"\bbrazil\b|\bbrasil\b|\bBR\b|" + BR_CITY, re.I)
RX_LATAM = re.compile(r"latam|latin america|am[eé]rica latina|south america|latinoam", re.I)
RX_AMERICAS = re.compile(r"\bamericas\b|am[eé]ricas|north and south america|western hemisphere", re.I)
RX_ANY = re.compile(r"worldwide|anywhere|global|work from anywhere|fully remote, any", re.I)
RX_REMOTE = re.compile(r"remote|remoto|home ?office|work from home|anywhere|teletrabalho", re.I)
RX_HYBRID = re.compile(r"hybrid|h[ií]brido", re.I)

def eligibility(loc_text, workplace=""):
    """Devolve (elig, modelo, ok) a partir do texto de local."""
    t = " ".join(x for x in [loc_text or "", workplace or ""] if x)
    remote = bool(RX_REMOTE.search(t)) or (workplace or "").lower() == "remote"
    hybrid = bool(RX_HYBRID.search(t)) or (workplace or "").lower() == "hybrid"
    modelo = "Remoto" if remote and not hybrid else ("Híbrido" if hybrid else ("Presencial" if t.strip() else ""))
    if RX_BR.search(t):
        city = RX_BR.search(t).group(0)
        if modelo == "Remoto":
            return "Brasil, remoto", modelo, True
        if city.lower() in ("brazil", "brasil", "br"):
            return "Brasil" + (", " + modelo.lower() if modelo else ""), modelo, True
        return "Brasil (" + city.title() + ")" + (", " + modelo.lower() if modelo else ""), modelo, True
    if RX_LATAM.search(t):
        return "LATAM, remoto (Brasil não citado)", "Remoto", True
    if RX_AMERICAS.search(t):
        return "Américas, remoto (conferir Brasil)", "Remoto", True
    if RX_ANY.search(t) and remote:
        return "Qualquer país, remoto (conferir)", "Remoto", True
    return "", modelo, False

# ---------------------------------------------------------------- salário

def fx_rate():
    meta = load("meta.json", {})
    return (meta.get("fx") or {}).get("usdbrl")

def fmt_k(v):
    return ("%.1f" % (v / 1000)).replace(".", ",")

def salary_text(minv, maxv, cur, period):
    if not (minv or maxv):
        return "", ""
    cur = (cur or "USD").upper()
    sym = {"USD": "US$", "EUR": "€", "GBP": "£", "BRL": "R$"}.get(cur, cur + " ")
    per = (period or "year").lower()
    lo, hi = minv or maxv, maxv or minv
    def rng(a, b, f):
        return f(a) if a == b else f(a) + " a " + f(b)
    if per.startswith("hour") or per == "hourly":
        txt = f"{sym} " + rng(lo, hi, lambda x: f"{x:g}") + " por hora"; month = (lo * 160, hi * 160)
    elif per.startswith("month"):
        txt = f"{sym} " + rng(lo, hi, fmt_k) + " mil por mês"; month = (lo, hi)
    else:
        txt = f"{sym} " + rng(lo, hi, fmt_k) + " mil por ano"; month = (lo / 12, hi / 12)
    brl = ""
    r = fx_rate()
    if cur == "BRL":
        brl = "R$ " + rng(month[0], month[1], fmt_k) + " mil/mês"
    elif cur == "USD" and r:
        brl = "cerca de R$ " + rng(month[0] * r, month[1] * r, fmt_k) + " mil/mês"
    return txt, brl

# ---------------------------------------------------------------- referência salarial

REFS = load("referencias.json", {"pos": [], "us": []})

def bench_for(title, market):
    out = {"pos": None, "co": None, "us": None}
    for r in REFS.get("pos", []):
        if re.search(r["match"], title, re.I):
            if not r.get("skip"):
                out["pos"] = {k: v for k, v in r.items() if k not in ("match", "skip")}
            break
    if market != "br":
        for r in REFS.get("us", []):
            if re.search(r["match"], title, re.I):
                if not r.get("skip"):
                    out["us"] = {k: v for k, v in r.items() if k not in ("match", "skip")}
                break
    return out

# ---------------------------------------------------------------- leitores de quadro

RAW_IDS = set()        # ids de todas as vagas listadas nos quadros lidos com sucesso (sem filtro)
BOARDS_OK = set()      # hosts/slugs lidos com sucesso

def url_id(u):
    """Id estável de uma vaga a partir do link (número do Greenhouse, uuid do Lever/Ashby, id do SmartRecruiters)."""
    m = re.search(r"gh_jid=(\d+)", u or "")
    if m:
        return m.group(1)
    u = (u or "").split("?")[0].rstrip("/")
    m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", u, re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"/(\d{6,})(?:$|/)", u)
    if m:
        return m.group(1)
    m = re.search(r"/j/([0-9A-F]{10})", u)
    return m.group(1) if m else ""

def mark(url):
    i = url_id(url)
    if i:
        RAW_IDS.add(i)

BR_COUNT = {}          # vagas abertas a quem mora no Brasil, qualquer área, por empresa (quadros oficiais)

def rec(company, title, url, loc, workplace="", posted="", source="", salary=None, extra=None):
    title = clean_title(title)
    elig, modelo, ok = eligibility(loc, workplace)
    if ok and source in ATS and company.get("id"):
        BR_COUNT[company["id"]] = BR_COUNT.get(company["id"], 0) + 1
    role = classify(title)
    if not role or not ok:
        return None
    sen = seniority(title)
    r = {
        "title": title, "company": company["name"], "companyId": company.get("id", ""),
        "role": role, "fit": fit_for(role, sen, title), "seniority": sen,
        "elig": elig, "model": modelo, "location": loc,
        "market": company.get("market", "intl"), "region": company.get("markets", []),
        "posted": posted, "url": url, "source": source, "origin": "empresa" if source in ATS else "agregador",
        "key": job_key(company["name"], title),
    }
    if salary:
        txt, brl = salary_text(*salary)
        if txt:
            r["salary"], r["salaryBRL"] = txt, brl
    if extra:
        r.update(extra)
    return r

def read_greenhouse(c):
    d = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{c['slug']}/jobs")
    out = []
    if d: BOARDS_OK.add("greenhouse/" + c["slug"])
    for j in (d or {}).get("jobs", []):
        mark(j.get("absolute_url"))
        loc = (j.get("location") or {}).get("name", "")
        r = rec(c, j.get("title"), j.get("absolute_url"), loc, "", iso(j.get("first_published") or j.get("updated_at")), "greenhouse")
        if r: out.append(r)
    return out

CONTRATO = {"full time": "Tempo integral", "full-time": "Tempo integral", "fulltime": "Tempo integral", "permanent": "Tempo integral",
            "contract": "Contrato", "contractor": "Contractor", "part time": "Meio período", "part-time": "Meio período",
            "homeoffice": "", "remote": "", "temporary": "Temporário", "clt": "CLT", "pj": "PJ"}

def read_lever(c, eu=False):
    host = "api.eu.lever.co" if eu else "api.lever.co"
    d = fetch_json(f"https://{host}/v0/postings/{c['slug']}?mode=json")
    out = []
    if d is not None: BOARDS_OK.add("lever/" + c["slug"])
    for j in d or []:
        mark(j.get("hostedUrl"))
        cat = j.get("categories") or {}
        locs = cat.get("allLocations") or [cat.get("location", "")]
        loc = " / ".join(x for x in locs if x)
        if j.get("country") == "BR" and not RX_BR.search(loc):
            loc += " (Brazil)"
        sal = None
        sr = j.get("salaryRange") or {}
        if sr.get("min") or sr.get("max"):
            per = (sr.get("interval") or "per-year-salary").replace("per-", "").split("-")[0]
            sal = (sr.get("min"), sr.get("max"), sr.get("currency"), per)
        r = rec(c, j.get("text"), j.get("hostedUrl"), loc, j.get("workplaceType", ""), iso(j.get("createdAt")), "lever", sal,
                {"contract": CONTRATO.get((cat.get("commitment") or "").strip().lower(), cat.get("commitment", ""))})
        if r: out.append(r)
    return out

def read_ashby(c):
    d = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{c['slug']}?includeCompensation=true")
    out = []
    if d: BOARDS_OK.add("ashby/" + c["slug"])
    for j in (d or {}).get("jobs", []):
        mark(j.get("jobUrl"))
        loc = " / ".join([j.get("location") or ""] + [x.get("location", "") for x in j.get("secondaryLocations") or []])
        sal = None
        comp = j.get("compensation") or {}
        for t in comp.get("compensationTiers") or []:
            for comp_part in t.get("components") or []:
                if comp_part.get("compensationType") == "Salary":
                    sal = (comp_part.get("minValue"), comp_part.get("maxValue"), comp_part.get("currencyCode"),
                           (comp_part.get("interval") or "1 YEAR").split()[-1].lower())
                    break
        r = rec(c, j.get("title"), j.get("jobUrl"), loc, j.get("workplaceType", ""), iso(j.get("publishedAt")), "ashby", sal,
                {"contract": {"FullTime": "Tempo integral", "Contract": "Contrato", "PartTime": "Meio período"}.get(j.get("employmentType"), "")})
        if r: out.append(r)
    return out

def read_smartrecruiters(c):
    out = []
    offset = 0
    while True:
        d = fetch_json(f"https://api.smartrecruiters.com/v1/companies/{c['slug']}/postings?country=br&limit=100&offset={offset}")
        content = (d or {}).get("content", [])
        if d: BOARDS_OK.add("smartrecruiters/" + c["slug"])
        for j in content:
            mark(f"/{j.get('id')}/")
            l = j.get("location") or {}
            loc = l.get("fullLocation") or ", ".join(x for x in [l.get("city"), l.get("country")] if x)
            wp = "remote" if l.get("remote") else ("hybrid" if l.get("hybrid") else "")
            url = f"https://jobs.smartrecruiters.com/{c['slug']}/{j.get('id')}"
            r = rec(c, j.get("name"), url, loc + (" Brazil" if (l.get("country") == "br") else ""), wp, iso(j.get("releasedDate")), "smartrecruiters")
            if r: out.append(r)
        offset += 100
        if not content or offset >= (d or {}).get("totalFound", 0):
            break
    return out

def read_recruitee(c):
    d = fetch_json(f"https://{c['slug']}.recruitee.com/api/offers/")
    out = []
    if d: BOARDS_OK.add("recruitee/" + c["slug"])
    for j in (d or {}).get("offers", []):
        mark(j.get("careers_url"))
        loc = " ".join(x for x in [j.get("location"), j.get("country")] if x)
        wp = "remote" if j.get("remote") else ""
        r = rec(c, j.get("title"), j.get("careers_url"), loc, wp, iso(j.get("published_at") or j.get("created_at")), "recruitee")
        if r: out.append(r)
    return out

def read_teamtailor(c):
    """RSS público do Teamtailor; slug é a URL completa do jobs.rss."""
    url = c["slug"]
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            xml = r.read().decode("utf-8", "replace")
    except Exception:
        return []
    BOARDS_OK.add("teamtailor/" + url)
    out = []
    for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
        def tag(t):
            m = re.search(r"<%s[^>]*>(.*?)</%s>" % (t, t), item, re.S)
            return html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", m.group(1))).strip() if m else ""
        link = tag("link")
        mark(link)
        locs = " / ".join(html.unescape(x) for x in re.findall(r"<tt:(?:name|city|country)>(.*?)</tt:(?:name|city|country)>", item))
        remote = tag("remoteStatus") or tag("tt:remoteStatus")
        pub = tag("pubDate")
        try:
            posted = dt.datetime.strptime(pub[:16], "%a, %d %b %Y").date().isoformat()
        except Exception:
            posted = ""
        r = rec(c, tag("title"), link, locs + " " + remote, "remote" if "remote" in (remote or "").lower() or "fully" in (remote or "").lower() else "", posted, "teamtailor")
        if r: out.append(r)
    return out

ATS = {"teamtailor": read_teamtailor, "greenhouse": read_greenhouse, "lever": read_lever, "lever_eu": lambda c: read_lever(c, True),
       "ashby": read_ashby, "smartrecruiters": read_smartrecruiters, "recruitee": read_recruitee}

# ---------------------------------------------------------------- Himalayas

def read_himalayas(companies_by_name):
    keywords = FUNCOES["himalayas_queries"]
    seen, out = set(), []
    for q in keywords:
        for page in range(1, 8):
            url = "https://himalayas.app/jobs/api/search?" + urllib.parse.urlencode(
                {"q": q, "country": "BR", "exclude_worldwide": "true", "sort": "recent", "page": page})
            d = fetch_json(url)
            jobs = (d or {}).get("jobs", [])
            if not jobs:
                break
            for j in jobs:
                link = j.get("applicationLink") or j.get("guid")
                if link in seen:
                    continue
                seen.add(link)
                name = j.get("companyName", "")
                c = companies_by_name.get(norm(name)) or {"name": name, "id": "", "market": "intl", "markets": []}
                locs = j.get("locationRestrictions") or []
                loc = ", ".join(locs)
                if len(locs) > 6 and "Brazil" in locs:
                    loc = "LATAM incl. Brazil"
                elif 1 < len(locs) <= 6 and "Brazil" in locs:
                    loc = "Brazil, " + ", ".join(x for x in locs if x != "Brazil")
                sal = None
                if j.get("minSalary") or j.get("maxSalary"):
                    sal = (j.get("minSalary"), j.get("maxSalary"), j.get("currency") or "USD", j.get("salaryPeriod") or "annual")
                emp = {"Full Time": "Tempo integral", "Contractor": "Contractor", "Part Time": "Meio período", "Temporary": "Temporário"}.get(j.get("employmentType"), "")
                r = rec(c, j.get("title"), link, loc + " remote", "remote", iso(j.get("pubDate")), "himalayas", sal,
                        {"contract": emp, "excerpt": (j.get("excerpt") or "")[:280]})
                if r:
                    out.append(r)
            time.sleep(0.4)
    return out

# ---------------------------------------------------------------- termômetro por empresa

def termometro(fontes):
    """Quantas vagas cada empresa tem hoje abertas a quem mora no Brasil (qualquer área)."""
    out = {}
    def him_count(c):
        if not c.get("him"):
            return c["id"], None
        url = "https://himalayas.app/jobs/api/search?" + urllib.parse.urlencode(
            {"company": c["him"], "country": "BR", "exclude_worldwide": "true"})
        d = fetch_json(url)
        return c["id"], (d or {}).get("totalCount")
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for cid, n in ex.map(him_count, fontes):
            out[cid] = {"himalayas": n}
    for c in fontes:
        o = out.setdefault(c["id"], {})
        if any(b["ats"] in ATS for b in c.get("boards", [])):
            o["oficial"] = BR_COUNT.get(c["id"], 0)
        vals = [v for v in (o.get("oficial"), o.get("himalayas")) if isinstance(v, int)]
        o["brJobs"] = max(vals) if vals else None
        o["at"] = TODAY.isoformat()
    return out

# ---------------------------------------------------------------- principal

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--banco", help="pasta com o export do banco (jobs/*.json)")
    ap.add_argument("--so-fontes", action="store_true")
    ap.add_argument("--so-himalayas", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    fontes = load("empresas.json", [])
    by_name = {norm(c["name"]): c for c in fontes}
    for c in fontes:
        for alias in c.get("aliases", []):
            by_name[norm(alias)] = c

    found, erros = [], []
    if not a.so_himalayas:
        boards = [(c, b) for c in fontes for b in c.get("boards", [])]
        def run(cb):
            c, b = cb
            cc = dict(c); cc["slug"] = b["slug"]
            try:
                return c["name"], b, ATS[b["ats"]](cc)
            except Exception as e:
                return c["name"], b, e
        with cf.ThreadPoolExecutor(max_workers=10) as ex:
            for name, b, res in ex.map(run, boards):
                if isinstance(res, Exception):
                    erros.append(f"{name} ({b['ats']}/{b['slug']}): {res}")
                else:
                    found.extend(res)
    if not a.so_fontes:
        try:
            found.extend(read_himalayas(by_name))
        except Exception as e:
            erros.append(f"himalayas: {e}")

    # dedup: prefere quadro oficial a agregador
    best = {}
    for r in found:
        k = r["key"]
        if k not in best or (best[k]["origin"] == "agregador" and r["origin"] == "empresa"):
            if k in best and best[k]["origin"] == "agregador":
                r.setdefault("alsoAt", best[k]["url"])
            best[k] = r
    vistas = sorted(best.values(), key=lambda r: r.get("posted") or "", reverse=True)

    for r in vistas:
        r["bench"] = bench_for(r["title"], r["market"])
        age = days_since(r["posted"]) if r.get("posted") else None
        r["status"] = "ativa" if r["origin"] == "empresa" and (age is None or age <= 30) else "conferir"
        r["checkedAt"] = TODAY.isoformat()

    # comparação com o banco
    banco = {}
    if a.banco:
        for p in glob.glob(os.path.join(a.banco, "**", "*.json"), recursive=True):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            doc = d.get("data", d)
            if "title" in doc:
                banco[os.path.splitext(os.path.basename(p))[0]] = doc
    urls_banco = {d.get("url") for d in banco.values()} | {d.get("alsoAt") for d in banco.values()}
    keys_banco = {d.get("key") or job_key(d.get("company", ""), d.get("title", "")) for d in banco.values()}
    excluidas = set((load("ajustes.json", {}) or {}).get("excluir", {}).keys())
    novas = [r for r in vistas if r["url"] not in urls_banco and r["key"] not in keys_banco and r["key"] not in excluidas]

    keys_vistas = {r["key"] for r in vistas}
    def board_of(u):
        m = re.search(r"greenhouse\.io/([^/]+)/jobs|lever\.co/([^/]+)/|ashbyhq\.com/([^/]+)/|smartrecruiters\.com/([^/]+)/|//([^.]+)\.recruitee\.com", u or "")
        if not m:
            return ""
        kind = ["greenhouse", "lever", "ashby", "smartrecruiters", "recruitee"][[i for i, g in enumerate(m.groups()) if g][0]]
        return kind + "/" + [g for g in m.groups() if g][0]
    sumidas = []
    for i, d in banco.items():
        if d.get("status") == "encerrada":
            continue
        u = d.get("url") or ""
        b = board_of(u)
        k = d.get("key") or job_key(d.get("company", ""), d.get("title", ""))
        if b and b in BOARDS_OK and url_id(u) and url_id(u) not in RAW_IDS and k not in keys_vistas:
            sumidas.append({"id": i, "title": d.get("title"), "company": d.get("company"), "url": u, "board": b})
    # banco também casa por id de link (link mudou de host, mesmo id)
    ids_banco = {url_id(d.get("url")) for d in banco.values()} - {""}
    novas = [r for r in novas if url_id(r["url"]) not in ids_banco]

    termo = termometro(fontes) if not a.so_himalayas else {}
    json.dump(termo, open(os.path.join(OUT, "termometro.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sem_cadastro = sorted({r["company"] for r in vistas if not r.get("companyId")})
    json.dump(sem_cadastro, open(os.path.join(OUT, "empresas_sem_cadastro.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(novas, open(os.path.join(OUT, "candidatas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(vistas, open(os.path.join(OUT, "vistas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(sumidas, open(os.path.join(OUT, "sumidas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    by_role = {}
    for r in novas:
        by_role[r["role"]] = by_role.get(r["role"], 0) + 1
    lines = [f"Coleta de {TODAY.isoformat()}",
             f"Vagas vistas hoje: {len(vistas)} (quadro oficial: {sum(1 for r in vistas if r['origin']=='empresa')}, agregador: {sum(1 for r in vistas if r['origin']=='agregador')})",
             f"Novas (fora do banco): {len(novas)}  por função: {json.dumps(by_role, ensure_ascii=False)}",
             f"Do banco e sumidas do quadro oficial: {len(sumidas)}",
             "Erros:"] + ["  " + e for e in erros]
    open(os.path.join(OUT, "relatorio.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
