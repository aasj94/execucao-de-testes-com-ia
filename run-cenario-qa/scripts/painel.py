#!/usr/bin/env python3
"""painel.py - evidencia padrao de QA: print da tela + painel de rede estilo DevTools.

Uso:
  python3 painel.py --print tela.png --req chamadas.json --out 03_evidencia.png [--blur x0,y0,x1,y1 ...]

chamadas.json:
{
  "tc": "1234", "passo": 1, "titulo": "Atendente tenta se promover",
  "selecionada": 0,                         indice da chamada detalhada (padrao: a ultima)
  "chamadas": [
    {"metodo": "PUT", "url": "https://host/v1/responsibles/123",
     "status": 403,                         ou omita e use "sd": "(nao enviado)"
     "payload": {...} ou "texto",           corpo enviado (opcional)
     "resposta": {...} ou "texto"}          corpo recebido (opcional)
  ],
  "console": "Mensagens da aplicacao: nenhuma."
}
Segredos (Authorization, token, senha, secret, cookie...) viram *** antes de desenhar.
"""
import argparse, json, re
from urllib.parse import urlsplit
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEGREDO = re.compile(r"(authorization|token|senha|password|secret|apikey|api_key|cookie|private)", re.I)
BEARER = re.compile(r"(Bearer\s+)[A-Za-z0-9\-_\.=+/]+", re.I)
JWT = re.compile(r"eyJ[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+")
STATUS_TXT = {200: "OK", 201: "Created", 202: "Accepted", 204: "No Content", 400: "Bad Request",
              401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 409: "Conflict",
              413: "Payload Too Large", 415: "Unsupported Media Type", 422: "Unprocessable Entity",
              429: "Too Many Requests", 500: "Internal Server Error", 502: "Bad Gateway",
              503: "Service Unavailable", 504: "Gateway Timeout"}

FUNDO = (31, 31, 31)
FAIXA = (41, 41, 41)
BORDA = (58, 58, 58)
AZUL_BORDA = (43, 111, 214)
SELEC = (25, 90, 180)
BRANCO = (235, 235, 235)
CINZA = (160, 160, 160)
TIT = (120, 170, 245)
J_CHAVE = (156, 220, 254)
J_TEXTO = (206, 145, 120)
J_VALOR = (86, 156, 214)


def mascarar(v):
    if isinstance(v, dict):
        return {k: ("***" if SEGREDO.search(str(k)) else mascarar(x)) for k, x in v.items()}
    if isinstance(v, list):
        return [mascarar(x) for x in v]
    if isinstance(v, str):
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
    return (78, 201, 128) if s < 300 else (240, 170, 60) if s < 500 else (235, 85, 85)


def rot_status(c):
    if c.get("sd"):
        return c["sd"]
    s = c.get("status")
    return "(sem resposta)" if s is None else f"{s} {STATUS_TXT.get(s, '')}".strip()


class Painel:
    def __init__(self, img, x0, largura, altura, escala):
        self.d = ImageDraw.Draw(img)
        self.x0, self.L, self.H, self.e = x0, largura, altura, escala
        self.pad = int(12 * escala)
        self.y = 0
        self.f = fonte(int(13 * escala))
        self.fn = fonte(int(13 * escala), negrito=True)
        self.fm = fonte(int(12.5 * escala), mono=True)
        self.lh = int(16.5 * escala)

    def larg(self, t, f):
        return self.d.textlength(t, font=f)

    def quebrar(self, t, f, w):
        out = []
        for bruta in str(t).split("\n"):
            atual = ""
            for ch in bruta:
                if self.larg(atual + ch, f) > w and atual:
                    corte = max(atual.rfind("/"), atual.rfind("-"), atual.rfind(" "))
                    if corte > len(atual) // 2:
                        out.append(atual[:corte + 1])
                        atual = atual[corte + 1:] + ch
                    else:
                        out.append(atual)
                        atual = ch
                else:
                    atual += ch
            out.append(atual)
        return out

    def aba(self, nome, fundo=FAIXA):
        h = int(26 * self.e)
        self.d.rectangle((self.x0, self.y, self.x0 + self.L, self.y + h), fill=fundo)
        tw = self.larg(nome, self.f)
        self.d.text((self.x0 + self.pad, self.y + int(5 * self.e)), nome, font=self.f, fill=BRANCO)
        self.d.line((self.x0 + self.pad - 4, self.y + h - 2, self.x0 + self.pad + tw + 4, self.y + h - 2),
                    fill=AZUL_BORDA, width=max(2, int(2 * self.e)))
        self.y += h

    def secao(self, nome):
        h = int(24 * self.e)
        self.d.line((self.x0, self.y, self.x0 + self.L, self.y), fill=BORDA)
        self.d.rectangle((self.x0, self.y + 1, self.x0 + self.L, self.y + h), fill=FAIXA)
        self.d.text((self.x0 + self.pad, self.y + int(4 * self.e)), nome, font=self.f, fill=CINZA)
        self.y += h + int(4 * self.e)

    def json_colorido(self, v, limite_y):
        texto = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, indent=2)
        tok = re.compile(r'("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+(?:\.\d+)?)')
        w = self.L - 2 * self.pad
        for linha in texto.split("\n"):
            pedacos, pos = [], 0
            for m in tok.finditer(linha):
                if m.start() > pos:
                    pedacos.append((linha[pos:m.start()], BRANCO))
                if m.group(1):
                    pedacos.append((m.group(1), J_CHAVE if m.group(2) else J_TEXTO))
                    if m.group(2):
                        pedacos.append((m.group(2), BRANCO))
                else:
                    pedacos.append((m.group(0), J_VALOR))
                pos = m.end()
            pedacos.append((linha[pos:], BRANCO))
            x = self.x0 + self.pad
            for t, cor in pedacos:
                for i, ch in enumerate(t):
                    cw = self.larg(ch, self.fm)
                    if x + cw > self.x0 + self.pad + w:
                        self.y += self.lh
                        x = self.x0 + self.pad + int(24 * self.e)
                    if self.y + self.lh > limite_y:
                        self.d.text((self.x0 + self.pad, self.y), "... (cortado)", font=self.fm, fill=CINZA)
                        self.y += self.lh
                        return
                    self.d.text((x, self.y), ch, font=self.fm, fill=cor)
                    x += cw
            self.y += self.lh

    def desenhar(self, dados):
        e, x0, L, pad = self.e, self.x0, self.L, self.pad
        chamadas = dados.get("chamadas", [])
        sel = dados.get("selecionada", len(chamadas) - 1 if chamadas else 0)
        # cabecalho
        self.y = int(8 * e)
        tit = "Chamadas capturadas no teste"
        self.d.text((x0 + pad, self.y), tit, font=self.fn, fill=TIT)
        partes = [p for p in (f"TC {dados['tc']}" if dados.get("tc") else "",
                              f"passo {dados['passo']}" if dados.get("passo") is not None else "",
                              dados.get("titulo", "")) if p]
        sub = " · ".join(partes)
        xs = x0 + pad + self.larg(tit, self.fn) + int(10 * e)
        for i, ln in enumerate(self.quebrar(sub, self.f, x0 + L - pad - xs)):
            self.d.text((xs, self.y + i * self.lh), ln, font=self.f, fill=CINZA)
        self.y += max(1, len(self.quebrar(sub, self.f, x0 + L - pad - xs))) * self.lh + int(10 * e)
        self.aba("Network")
        # tabela
        c_met = x0 + L - int(125 * e)
        c_st = x0 + L - int(58 * e)
        self.y += int(4 * e)
        for t, x in (("Name", x0 + pad), ("Method", c_met), ("Status", c_st)):
            self.d.text((x, self.y), t, font=self.f, fill=CINZA)
        self.y += self.lh + int(4 * e)
        largura_nome = c_met - x0 - pad - int(16 * e)
        for i, c in enumerate(chamadas):
            u = urlsplit(c.get("url", ""))
            nome = u.path + (("?" + u.query) if u.query else "")
            linhas = self.quebrar(nome, self.fm, largura_nome)
            h = len(linhas) * self.lh + int(6 * e)
            if i == sel:
                self.d.rectangle((x0 + 2, self.y, x0 + L, self.y + h), fill=SELEC)
            for j, ln in enumerate(linhas):
                self.d.text((x0 + pad, self.y + int(3 * e) + j * self.lh), ln, font=self.fm, fill=BRANCO)
            self.d.text((c_met, self.y + int(3 * e)), c.get("metodo", "").upper(), font=self.fm, fill=BRANCO)
            st = rot_status(c)
            st_curto = st if self.larg(st, self.fm) < x0 + L - c_st - pad else st.split(" ")[0]
            self.d.text((c_st, self.y + int(3 * e)), st_curto, font=self.fm,
                        fill=BRANCO if i == sel else cor_status(c.get("status")))
            self.y += h
        if not chamadas:
            self.d.text((x0 + pad, self.y), "Nenhuma chamada ao servidor neste passo.", font=self.f, fill=CINZA)
            self.y += self.lh
        # detalhe da selecionada
        console = dados.get("console") or "Nenhuma mensagem no console."
        h_console = int(26 * e) + int(8 * e) + len(self.quebrar(console, self.fm, L - 2 * pad)) * self.lh
        limite = self.H - h_console - int(6 * e)
        if chamadas:
            c = chamadas[sel]
            u = urlsplit(c.get("url", ""))
            linha = f"{c.get('metodo', '').upper()} {u.netloc}{u.path}" + (("?" + u.query) if u.query else "")
            self.y += int(4 * e)
            for ln in self.quebrar(linha, self.f, L - 2 * pad):
                self.d.text((x0 + pad, self.y), ln, font=self.f, fill=CINZA)
                self.y += self.lh
            self.y += int(4 * e)
            self.secao(f"Response · {rot_status(c)}")
            if c.get("resposta") not in (None, "", [], {}):
                self.json_colorido(c["resposta"], limite - int(60 * e))
            else:
                self.d.text((x0 + pad, self.y), "(sem corpo)", font=self.fm, fill=CINZA)
                self.y += self.lh
            self.y += int(6 * e)
            self.secao("Payload")
            if c.get("payload") not in (None, "", [], {}):
                self.json_colorido(c["payload"], limite)
            else:
                self.d.text((x0 + pad, self.y), "(sem corpo)", font=self.fm, fill=CINZA)
                self.y += self.lh
        # console no rodape (sempre presente)
        self.y = self.H - h_console
        self.aba("Console", fundo=FUNDO)
        self.y += int(6 * e)
        for ln in self.quebrar(console, self.fm, L - 2 * pad):
            self.d.text((x0 + pad, self.y), ln, font=self.fm, fill=BRANCO)
            self.y += self.lh

def montar(a):
    tela = Image.open(a.print).convert("RGB")
    for r in a.blur or []:
        caixa = tuple(int(n) for n in r.split(","))
        tela.paste(tela.crop(caixa).filter(ImageFilter.GaussianBlur(14)), caixa)
    dados = mascarar(json.load(open(a.req, encoding="utf-8")))
    escala = max(0.6, tela.height / 854)
    L = int(640 * escala)
    out = Image.new("RGB", (tela.width + L, tela.height), FUNDO)
    out.paste(tela, (0, 0))
    ImageDraw.Draw(out).line((tela.width, 0, tela.width, tela.height), fill=AZUL_BORDA, width=max(2, int(2 * escala)))
    Painel(out, tela.width + 2, L - 2, tela.height, escala).desenhar(dados)
    out.save(a.out, optimize=True)
    print(f"ok {a.out} {out.width}x{out.height}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--print", required=True)
    p.add_argument("--req", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--blur", nargs="*")
    montar(p.parse_args())
