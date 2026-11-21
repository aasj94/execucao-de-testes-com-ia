#!/usr/bin/env python3
"""api_print.py - evidencia de chamada direta a API (visual de cliente de API, estilo Postman).

Uso:
  python3 api_print.py --req chamada.json --out 05_api_put_responsible.png

chamada.json:
{
  "tc": "1234", "passo": 3, "titulo": "Atendente tenta se promover via API",
  "metodo": "PUT",
  "url": "https://host/v1/responsibles/123",
  "headers": {"Content-Type": "application/json", "Authorization": "Bearer <TOKEN>"},
  "payload": {...} ou "texto" (opcional),
  "status": 403, "tempo_ms": 238, "tamanho_bytes": 412,   (tempo e tamanho medidos no fetch)
  "resposta": {...} ou "texto",
  "resposta_headers": {"content-type": "application/json"} (opcional)
}
Segredos (Authorization, token, senha, secret, cookie, JWT) viram *** antes de desenhar.
"""
import argparse, json, re
from urllib.parse import urlsplit, parse_qsl
from PIL import Image, ImageDraw, ImageFont

SEGREDO = re.compile(r"(authorization|token|senha|password|secret|apikey|api_key|cookie|private)", re.I)
BEARER = re.compile(r"(Bearer\s+)(?!<TOKEN>)[A-Za-z0-9\-_\.=+/]+", re.I)
JWT = re.compile(r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+")
STATUS_TXT = {200: "OK", 201: "Created", 202: "Accepted", 204: "No Content", 400: "Bad Request",
              401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 405: "Method Not Allowed",
              409: "Conflict", 413: "Payload Too Large", 415: "Unsupported Media Type",
              422: "Unprocessable Entity", 429: "Too Many Requests", 500: "Internal Server Error",
              502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout"}
COR_METODO = {"GET": (0, 127, 49), "POST": (173, 122, 3), "PUT": (9, 84, 182), "PATCH": (98, 52, 163),
              "DELETE": (142, 26, 16), "HEAD": (0, 127, 49), "OPTIONS": (166, 20, 111)}

FUNDO = (255, 255, 255)
FAIXA = (249, 249, 249)
BORDA = (230, 230, 230)
TEXTO = (33, 33, 33)
CINZA = (110, 110, 110)
CLARO = (166, 166, 166)
LARANJA = (255, 108, 55)
AZUL = (9, 105, 218)
J_CHAVE = (161, 21, 21)
J_TEXTO = (11, 116, 50)
J_NUM = (9, 84, 182)
J_LIT = (170, 13, 145)


def mascarar(v, chave=""):
    if isinstance(v, dict):
        return {k: mascarar(x, k) for k, x in v.items()}
    if isinstance(v, list):
        return [mascarar(x) for x in v]
    if isinstance(v, str):
        if SEGREDO.search(str(chave)):
            return "Bearer <TOKEN>" if v.lower().startswith("bearer") else "***"
        return JWT.sub("***", BEARER.sub(r"\1***", v))
    return v


def fonte(tam, mono=False, negrito=False):
    nomes = {(True, True): ["DejaVuSansMono-Bold.ttf", "consolab.ttf"],
             (True, False): ["DejaVuSansMono.ttf", "consola.ttf"],
             (False, True): ["DejaVuSans-Bold.ttf", "arialbd.ttf"],
             (False, False): ["DejaVuSans.ttf", "arial.ttf"]}[(mono, negrito)]
    for n in nomes:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            pass
    return ImageFont.load_default(size=tam)


def cor_status(s):
    if not isinstance(s, int):
        return CINZA
    return (0, 127, 49) if s < 300 else (173, 122, 3) if s < 400 else (196, 43, 28)


def tam_legivel(b):
    if b is None:
        return "-"
    return f"{b} B" if b < 1024 else f"{b / 1024:.2f} KB"


class Tela:
    def __init__(self, largura=1400, escala=1.4):
        self.W, self.e = largura, escala
        self.pad = int(16 * escala)
        self.f = fonte(int(13 * escala))
        self.fn = fonte(int(13 * escala), negrito=True)
        self.ft = fonte(int(15 * escala), negrito=True)
        self.fm = fonte(int(12.5 * escala), mono=True)
        self.lh = int(17 * escala)
        self.img = Image.new("RGB", (largura, 6000), FUNDO)
        self.d = ImageDraw.Draw(self.img)
        self.y = 0

    def larg(self, t, f):
        return self.d.textlength(t, font=f)

    def abas(self, nomes, ativa, direita=None):
        h = int(34 * self.e)
        x = self.pad
        for n in nomes:
            f = self.fn if n == ativa else self.f
            self.d.text((x, self.y + int(9 * self.e)), n, font=f, fill=TEXTO if n == ativa else CINZA)
            tw = self.larg(n, f)
            if n == ativa:
                self.d.line((x, self.y + h - 2, x + tw, self.y + h - 2), fill=LARANJA, width=max(2, int(2 * self.e)))
            x += tw + int(24 * self.e)
        if direita:
            xd = self.W - self.pad
            for txt, cor in reversed(direita):
                xd -= self.larg(txt, self.f)
                self.d.text((xd, self.y + int(9 * self.e)), txt, font=self.f, fill=cor)
                xd -= int(18 * self.e)
        self.d.line((0, self.y + h, self.W, self.y + h), fill=BORDA)
        self.y += h + int(8 * self.e)

    def json(self, v, numerar=True):
        if v in (None, "", [], {}):
            self.d.text((self.pad, self.y), "(sem corpo)", font=self.fm, fill=CLARO)
            self.y += self.lh + int(6 * self.e)
            return
        if isinstance(v, str):
            try:
                v = json.loads(v)
            except Exception:
                pass
        texto = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=4)
        tok = re.compile(r'("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+(?:\.\d+)?)')
        xg = self.pad + (int(40 * self.e) if numerar else 0)
        w = self.W - xg - self.pad
        for n, linha in enumerate(texto.split("\n"), 1):
            if numerar:
                num = str(n)
                self.d.text((xg - int(14 * self.e) - self.larg(num, self.fm), self.y), num, font=self.fm, fill=CLARO)
            pedacos, pos = [], 0
            for m in tok.finditer(linha):
                if m.start() > pos:
                    pedacos.append((linha[pos:m.start()], TEXTO))
                if m.group(1):
                    pedacos.append((m.group(1), J_CHAVE if m.group(2) else J_TEXTO))
                    if m.group(2):
                        pedacos.append((m.group(2), TEXTO))
                elif m.group(3):
                    pedacos.append((m.group(0), J_LIT))
                else:
                    pedacos.append((m.group(0), J_NUM))
                pos = m.end()
            pedacos.append((linha[pos:], TEXTO))
            x = xg
            for t, cor in pedacos:
                for ch in t:
                    cw = self.larg(ch, self.fm)
                    if x + cw > xg + w:
                        self.y += self.lh
                        x = xg + int(32 * self.e)
                    self.d.text((x, self.y), ch, font=self.fm, fill=cor)
                    x += cw
            self.y += self.lh
        self.y += int(6 * self.e)

    def tabela(self, pares):
        c2 = self.pad + int(260 * self.e)
        self.d.text((self.pad, self.y), "Key", font=self.fn, fill=CINZA)
        self.d.text((c2, self.y), "Value", font=self.fn, fill=CINZA)
        self.y += self.lh + int(4 * self.e)
        for k, v in pares:
            self.d.line((self.pad, self.y - 3, self.W - self.pad, self.y - 3), fill=BORDA)
            self.d.text((self.pad, self.y), str(k), font=self.fm, fill=TEXTO)
            self.d.text((c2, self.y), str(v), font=self.fm, fill=TEXTO)
            self.y += self.lh + int(4 * self.e)
        self.y += int(6 * self.e)


def montar(a):
    c = mascarar(json.load(open(a.req, encoding="utf-8")))
    t = Tela()
    e, pad, W = t.e, t.pad, t.W
    metodo = c.get("metodo", "GET").upper()
    url = c.get("url", "")
    # cabecalho
    h = int(40 * e)
    t.d.rectangle((0, 0, W, h), fill=FAIXA)
    t.d.line((0, h, W, h), fill=BORDA)
    partes = [p for p in (f"TC {c['tc']}" if c.get("tc") else "",
                          f"passo {c['passo']}" if c.get("passo") is not None else "",
                          c.get("titulo", "")) if p]
    t.d.text((pad, int(11 * e)), "Chamada direta à API", font=t.ft, fill=TEXTO)
    t.d.text((pad + t.larg("Chamada direta à API", t.ft) + int(14 * e), int(12 * e)), " · ".join(partes), font=t.f, fill=CINZA)
    t.y = h + int(14 * e)
    # barra de requisicao
    hb = int(40 * e)
    xb = W - pad - int(90 * e)
    t.d.rounded_rectangle((pad, t.y, xb - int(10 * e), t.y + hb), radius=int(4 * e), outline=BORDA, fill=FUNDO)
    t.d.rounded_rectangle((pad, t.y, pad + int(100 * e), t.y + hb), radius=int(4 * e), fill=FAIXA)
    t.d.line((pad + int(100 * e), t.y, pad + int(100 * e), t.y + hb), fill=BORDA)
    t.d.text((pad + int(12 * e), t.y + int(12 * e)), metodo, font=t.fn, fill=COR_METODO.get(metodo, TEXTO))
    url_txt = url
    while t.larg(url_txt, t.fm) > xb - pad - int(130 * e) and len(url_txt) > 10:
        url_txt = url_txt[:-4] + "..."
    t.d.text((pad + int(112 * e), t.y + int(12 * e)), url_txt, font=t.fm, fill=TEXTO)
    t.d.rounded_rectangle((xb, t.y, W - pad, t.y + hb), radius=int(4 * e), fill=AZUL)
    t.d.text((xb + int(24 * e), t.y + int(11 * e)), "Send", font=t.fn, fill=FUNDO)
    t.y += hb + int(10 * e)
    # requisicao
    headers = c.get("headers") or {}
    params = parse_qsl(urlsplit(url).query)
    tem_body = c.get("payload") not in (None, "", [], {})
    t.abas(["Params", "Authorization", f"Headers ({len(headers)})", "Body"],
           "Body" if tem_body else f"Headers ({len(headers)})")
    if params:
        t.d.text((pad, t.y), "Query Params", font=t.fn, fill=CINZA); t.y += t.lh + int(4 * e)
        t.tabela(params)
    if tem_body:
        t.d.text((pad, t.y), "raw · JSON", font=t.f, fill=CINZA); t.y += t.lh + int(6 * e)
        t.json(c["payload"])
    t.d.text((pad, t.y), "Headers", font=t.fn, fill=CINZA); t.y += t.lh + int(4 * e)
    t.tabela(headers.items() or [("(nenhum)", "")])
    # resposta
    t.d.rectangle((0, t.y, W, t.y + int(6 * e)), fill=FAIXA)
    t.y += int(6 * e)
    s = c.get("status")
    st = "(sem resposta)" if s is None else f"{s} {STATUS_TXT.get(s, '')}".strip()
    tempo = c.get("tempo_ms")
    t.abas(["Body", "Cookies", f"Headers ({len(c.get('resposta_headers') or {})})"], "Body",
           direita=[("Status:", CINZA), (st, cor_status(s)), ("Time:", CINZA),
                    (f"{tempo} ms" if tempo is not None else "-", (0, 127, 49)),
                    ("Size:", CINZA), (tam_legivel(c.get("tamanho_bytes")), (0, 127, 49))])
    t.d.text((pad, t.y), "Pretty · JSON", font=t.f, fill=CINZA); t.y += t.lh + int(6 * e)
    t.json(c.get("resposta"))
    t.y += int(10 * e)
    out = t.img.crop((0, 0, W, t.y))
    ImageDraw.Draw(out).rectangle((0, 0, W - 1, t.y - 1), outline=BORDA)
    out.save(a.out, optimize=True)
    print(f"ok {a.out} {out.width}x{out.height}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--req", required=True)
    p.add_argument("--out", required=True)
    montar(p.parse_args())
