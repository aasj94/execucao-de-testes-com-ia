# Anexos D e F: scripts de evidência

## Anexo D: painel.py (evidência "tela + painel")
Uso: `python3 <pasta-da-skill>/scripts/painel.py --print <print.jpg> --req <passo.json> --out <saida.png> [--blur x0,y0,x1,y1 ...]`
- `--blur` usa as coordenadas do print salvo (em `scale: 1`, iguais às da tela).
- O script mascara sozinho Authorization, token, senha, cookie e JWT, mas mesmo assim não coloque segredo no JSON.
- Resultado esperado: print à esquerda; à direita, "Chamadas capturadas no teste · TC · passo · título", aba Network com a tabela Name/Method/Status (selecionada em azul), a URL completa, Response com status e JSON colorido, Payload e, no rodapé, Console.


## Anexo F: api_print.py (evidência de chamada direta à API)
Uso: `python3 <pasta-da-skill>/scripts/api_print.py --req <chamada.json> --out <saida.png>`
- Resultado esperado: cabeçalho "Chamada direta à API · TC · passo · título"; barra com o método (cor por tipo) e a URL; abas Params, Authorization, Headers e Body com o payload e a tabela de headers; e a resposta com Body em JSON colorido e Status, Time e Size à direita. Sem Console e sem nome ou logo de ferramenta.
- O script mascara Authorization (sempre `Bearer <TOKEN>`), token, senha, cookie e JWT, mas mesmo assim não coloque segredo no JSON.

Medir a chamada no navegador (via `javascript_tool`, na aba do app testado; troque método, URL e corpo):
```javascript
const t = JSON.parse(localStorage.getItem('<CHAVE_DO_TOKEN>')).access_token; // ajuste: leia o token de onde o app o guarda (veja config.md e Anexo C)
const metodo = 'PUT', url = '<url completa>', corpo = {/* payload */};
const ini = performance.now();
const r = await fetch(url, { method: metodo, headers: { 'Accept': 'application/json, text/plain, */*', 'Authorization': 'Bearer ' + t, 'Content-Type': 'application/json' }, body: metodo === 'GET' ? undefined : JSON.stringify(corpo) });
const txt = await r.text();
JSON.stringify({ metodo, url, status: r.status, tempo_ms: Math.round(performance.now() - ini), tamanho_bytes: new Blob([txt]).size, resposta: txt.slice(0, 4000), resposta_headers: { 'content-type': r.headers.get('content-type') } }).replace(/[?&=]/g, m => ({ '?': '%3F', '&': '%26', '=': '%3D' })[m])
```
Desfaça a troca de `?`, `&` e `=` ao montar o JSON da evidência e coloque os headers enviados com `Authorization: Bearer <TOKEN>`.

