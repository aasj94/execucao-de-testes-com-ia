# Execução de testes com IA

Skill `run-cenario-qa`, para o Claude, que executa Test Cases de um card do Azure DevOps no navegador: segue o Gherkin, tira prints com painel de rede e console, gera curls, registra o passo a passo no TC, grava o outcome no Test Plans e abre bugs quando algo falha.

## O que ela faz
- Lê o card e os Test Cases filhos, e inclui na suite da sprint os TCs que estão sem suite.
- Executa cada cenário no navegador e gera evidências em dois formatos: "tela + painel" (print com Network, Response, Payload e Console) e "cliente de API" (requisição e resposta de chamadas diretas).
- Mascara tokens, senhas, cookies e JWT nas imagens e nos curls antes de qualquer upload.
- Registra cada ciclo na descrição do TC, calcula o esforço em horas e grava o outcome (`passed`, `failed`, `blocked`, `notApplicable`).
- Abre bugs só depois do OK do QA, com passos de reprodução, comportamento esperado e evidências.
- Permite pausar e continuar a execução em outra sessão.

## Estrutura
```
run-cenario-qa/SKILL.md                   instruções da skill
references/config.md          configuração da sua organização (preencha primeiro)
references/test-plans-api.md  chamadas REST do Test Plans
references/upload-evidencias.md  upload de anexos para o work item
references/evidencias.md      uso dos scripts de evidência
references/dicas-tecnicas.md  dicas de navegador, token e upload
scripts/painel.py             evidência "tela + painel"
scripts/api_print.py          evidência de chamada direta à API
```

## Como usar
1. Preencha `run-cenario-qa/references/config.md` com a organização, o projeto e os campos customizados do seu ADO.
2. Instale a skill no Claude e conecte o MCP do Azure DevOps e um navegador (Claude in Chrome).
3. Peça, por exemplo: "execute os testes do card 12345".

## Requisitos
- Python 3 com Pillow (`pip install pillow`) para os scripts de evidência.
- Conector do Azure DevOps (work items e test plans) e um navegador controlável pelo Claude.
