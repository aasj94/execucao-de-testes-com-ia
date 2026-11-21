# Anexo E: anexar evidências no work item (pela aba do ADO no Chrome)
1. Abra o TC no ADO numa aba do grupo (ex.: `https://dev.azure.com/<ORG>/<PROJETO>/_workitems/edit/<TC>`), com o QA logado no ADO.
2. Crie o input de arquivo na página:
```javascript
(() => { let i = document.getElementById('qa-up'); if (!i) { i = document.createElement('input'); i.type = 'file'; i.id = 'qa-up'; i.multiple = true; i.setAttribute('aria-label', 'qa-up upload'); i.style.cssText = 'position:fixed;top:4px;left:4px;z-index:2147483647;opacity:0.01;width:40px;height:20px'; document.body.appendChild(i); } return 'input pronto'; })()
```
3. Ache o input com `find` ("qa-up upload file input") e use `file_upload` com os caminhos em `/home/claude/qa-up/<card>/<TC>/` (até 10 MB por chamada). Nunca clique no input.
4. Suba e vincule ao work item (troque `<TC>`, `<ORG>`, `<PROJETO>` e o comentário):
```javascript
const wi = <TC>;
const comentario = 'Evidência do teste';
const base = (location.host.includes('dev.azure.com') ? location.origin + '/<ORG>' : location.origin) + '/<PROJETO>/_apis/wit';
const h = { 'X-TFS-FedAuthRedirect': 'Suppress' };
const files = [...document.getElementById('qa-up').files];
const ops = []; const ids = [];
for (const f of files) {
  const r = await fetch(base + '/attachments?fileName=' + encodeURIComponent(f.name) + '&api-version=7.1', { method: 'POST', credentials: 'include', headers: { ...h, 'Content-Type': 'application/octet-stream' }, body: f });
  const j = await r.json();
  ids.push(f.name + '|' + j.id);
  ops.push({ op: 'add', path: '/relations/-', value: { rel: 'AttachedFile', url: j.url, attributes: { comment: comentario } } });
}
const p = await fetch(base + '/workitems/' + wi + '?api-version=7.1', { method: 'PATCH', credentials: 'include', headers: { ...h, 'Content-Type': 'application/json-patch+json' }, body: JSON.stringify(ops) });
document.getElementById('qa-up').value = '';
(JSON.stringify(ids) + ' | anexos ' + ops.length + ' | patch ' + p.status).replace(/[?&=]/g, '_')
```
5. Confira o retorno: `patch 200` = anexado. Outro status: mostre ao QA e não repita às cegas.
6. O retorno lista `arquivo|id` de cada anexo: use esses ids nas imagens da Descrição (seção 3). O script já limpa o input para o próximo TC.
