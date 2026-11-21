---
name: run-cenario-qa
description: "Executa os Test Cases de um card do Azure DevOps (User Story, Bug, Task ou Feature) no navegador, registra o passo a passo com prints e curls no TC, grava o outcome no Test Plans e abre bugs quando algo falha. Use sempre que o QA pedir para executar, rodar, iniciar, testar, retestar ou continuar a execução de um card ou de seus cenários/TCs, mesmo sem citar a skill. Exemplos: \"execute os testes do card X\", \"inicie os testes\", \"testa o card X\", \"reteste o TC Y\", \"continue a execução do card X\"."
---

# Execução de cenários de QA

Lê um card do Azure DevOps (ADO), executa os Test Cases filhos dele no navegador, registra o resultado de cada TC com evidências (prints e curls), grava o outcome no Test Plans e abre bugs quando algo falha. Funciona para qualquer QA: nada aqui depende de um usuário, pasta ou conta específicos. Fale em português, de forma direta.

## Antes de usar: configuração da sua organização
Este pacote é genérico. Os valores que variam de organização para organização (nome da organização e do projeto no ADO, nomes dos campos customizados, padrão de nome do Test Plan) ficam em `references/config.md`. Preencha esse arquivo uma vez e a skill passa a usá-lo. Onde o texto abaixo mostra `<ORG>`, `<PROJETO>` ou `<CAMPO_...>`, use o valor desse arquivo. Se algum valor estiver sem preenchimento, pergunte ao QA em vez de inventar.

## Regras que não podem ser quebradas
1. **Login é sempre do QA.** Nunca digite senha, nunca mostre nem grave token, cookie ou header Authorization. Em curls use `Authorization: Bearer <TOKEN>`. Em payloads, mascare segredos com `***`.
2. **Dados reais de clientes aparecem borrados nos prints** (nome, telefone, e-mail, documento).
3. **Confirme se o ambiente de teste usa dados reais.** Se usar (por exemplo, um staging ligado a um banco de produção), tudo que for criado é real: só crie, altere ou apague dados com o OK do QA e use nomes que identifiquem o teste (ex.: `QA Card <id> - <descrição>`).
4. **Nada que envie mensagem, e-mail, ligação ou notificação a pessoas reais** sem o OK explícito do QA para aquele envio.
5. **Estados do TC:**
   - antes de começar a analisar um TC, mova-o para **Em Andamento**. A **Data Início** só é gravada na primeira vez que o TC é tocado, naquele momento (não depois, não estimada). **Se ela já estiver preenchida, nunca altere**: em reteste, retomada depois de falha ou de bloqueio, ou continuação de outra sessão, ela continua mostrando quando o TC foi tocado pela primeira vez;
   - TC **aprovado sem ressalva** vai para **Concluído** com outcome `passed`, sem perguntar ao QA;
   - TC **reprovado** (falhou) vai para **Pendente** com outcome `failed`, sem perguntar ao QA;
   - **cenário bloqueado** (não pôde ser executado ou concluído por algo fora do teste: ambiente fora do ar, dependência de outro card, dado ou acesso indisponível, ou porque o QA disse que está bloqueado) vai para **Pendente** com outcome `blocked`, sem perguntar ao QA. Registre a justificativa num **comentário na aba Discussion do TC** (seção 3, passo 7) e no `resumo-execucao.md`;
   - **só no caso de Aprovado com ressalva quem decide é o QA**: pergunte se a ressalva vira bug e o que acontece com o TC. Não decida sozinho e não mova para Concluído sem o OK dele;
   - **cenário cancelado:** quando o QA decidir cancelar um TC (ou o TC já estiver Cancelado no ADO), o outcome no Test Plans vai para `notApplicable` (Not Applicable) e o estado para **Cancelado**. Não execute o cenário. Registre a justificativa que o QA der num **comentário na aba Discussion do TC** (seção 3, passo 7) e no `resumo-execucao.md`. Se o QA não disser o motivo, pergunte antes de comentar.
6. **Texto no ADO:**
   - nos TCs, nenhum emoji além do ⚠️ (usado para ressalva);
   - nos bugs e nos comentários da Discussion, nenhum emoji, nem o ⚠️;
   - não escreva ambiente, produto nem horário no texto (já estão nos campos);
   - bugs ficam **sem dev responsável**.
7. **Só fatos.** Não invente comportamento, causa ou resultado. O que não foi confirmado fica escrito como "em aberto". Horário reconstruído depois é marcado como estimado.
8. **Em caso de falha, compare com produção** sem salvar nada lá. Se for igual, registre "mesmo comportamento em produção". Diferença só no console, igual em produção, não vira bug.
9. Não dispare alerts/confirms do navegador. Se um botão abrir diálogo nativo, avise o QA antes.

## 0. Configuração do QA (no início de cada sessão)
Descubra e confirme com o QA, uma vez por sessão, sem assumir valores de outra pessoa:
- **Quem é o QA:** e-mail do usuário da sessão. Ele vai no campo `<CAMPO_QA>` dos bugs.
- **Pasta de evidências:** veja as pastas conectadas (`get_device_info` → `connectedFolders`) e procure uma que já tenha subpastas de cards. Se achar, confirme com o QA. Se não, pergunte o caminho e peça acesso com `device_request_folder_access`. Sem pasta, as evidências vão só para o ADO e o chat.
- **Ambiente e URL:** pergunte em qual ambiente o QA vai testar (dev, staging etc.) e a URL, se ela não estiver no card nem num `contexto-continuacao.md` da pasta.
- **Contas de teste:** quais logins/perfis o QA vai usar. Nunca peça a senha; peça que ele faça o login na aba aberta. Se o teste exigir dois perfis ao mesmo tempo, combine com o QA em qual navegador (ou janela) fica cada login, para que as sessões não se sobreponham.
- **Ferramentas da sessão:** antes do primeiro print, confirme que `python3 -c "import PIL"` funciona (se faltar: `pip install pillow --break-system-packages`) e que `<pasta-da-skill>/scripts/painel.py` e `<pasta-da-skill>/scripts/api_print.py` existem (`<pasta-da-skill>` é o caminho base informado quando a skill foi carregada). Os scripts vêm no pacote da skill: rode-os de lá, sem reescrevê-los. Se a pasta não estiver acessível, avise o QA em vez de recriar os scripts de memória.
- **Continuação:** se existir `<pasta>/<card>/contexto-continuacao.md`, leia antes de tudo e continue de onde parou.

## 1. Leitura do card
1. Busque o card no projeto `<PROJETO>` com relações (`expand: All`) e os comentários (o "Como testar" do dev costuma estar no último comentário).
2. Liste os filhos do tipo **Test Case** e leia de cada um: título, estado, Gherkin (`<CAMPO_GHERKIN>`), Ambiente, Produto.
3. Ache o **Test Plan, a Suite e o Test Point** de cada TC (Anexo A, passo 1). **TC sem suite entra automaticamente na suite da sprint do card** (Anexo A, passos 2 e 3), sem perguntar: o plano é o da mesma iteration do card (`System.IterationPath`, seguindo o padrão de nome em `references/config.md`) e a suite é a suite raiz dele. Avise o QA em uma linha ("incluí os TCs X a Y na suite <id> do plano <nome>"). Só pergunte se não existir plano para a sprint do card ou se ele tiver mais de uma suite e não der para saber qual usar.
4. **Opcional:** se a sua organização tiver uma checagem de cobertura de cenários (por exemplo, outra skill que avisa quando o card toca módulos sensíveis), chame-a aqui, mostre os avisos ao QA e anote a decisão dele. Sem essa checagem, siga para o próximo passo.
5. Apresente ao QA: os TCs com estado atual, a ordem sugerida (maior risco primeiro), o que cada um precisa (perfil de usuário, dados, ação de outra pessoa) e o que fica para depois. **Espere a confirmação** de quais TCs executar.

## 2. Execução de cada TC
Para cada TC confirmado, um de cada vez:
1. **Início:** leia antes o TC no ADO. Numa única atualização, mova para Em Andamento e, **só se a Data Início (`<CAMPO_DATA_INICIO>`) estiver vazia**, grave-a com o horário atual em UTC. Se ela já tiver valor (reteste, TC que falhou ou ficou bloqueado e foi retomado, continuação de outra sessão), não inclua esse campo na atualização.
   - **Início do ciclo:** anote o horário em que começou este ciclo só na sessão (e no `contexto-continuacao.md`, se houver pausa), sem gravar no ADO. É dele que sai o esforço do ciclo (seção 3).
   - Se o seu processo do ADO exigir campos preenchidos para sair de Pendente, envie-os junto (os campos e os valores aceitos estão em `references/config.md`): módulo, tipo de teste, ciclo de teste e complexidade. O ciclo de teste é 1 na primeira execução; em reteste, some 1 ao valor atual. A complexidade se escolhe pela quantidade de cenários e de perfis envolvidos.
2. **Navegador:** use Claude in Chrome (`tabs_context_mcp` primeiro; abra aba própria). Se o QA precisar logar, abra a tela de login e espere ele avisar. Antes de cada login, diga ao QA qual perfil vai entrar em qual navegador e espere ele avisar. Ao agir, confira que está na sessão certa para o perfil do passo. A aba do ADO (Anexos A e E) fica no Chrome.
3. **Siga o Gherkin** cenário por cenário. O tipo de evidência depende do passo:
   - **Passo na tela** (o QA ou você agindo na interface): padrão **"tela + painel"** (Anexo D): print da tela à esquerda e, à direita, o painel com Network (chamadas do passo, a selecionada destacada), Response, Payload e Console. As quatro partes aparecem sempre, mesmo vazias.
   - **Chamada direta à API, sem tela** (passo 4): imagem no estilo de cliente de API (Anexo F), com requisição e resposta. **Não leva o painel nem o Console**, porque não houve tela envolvida.
   - Se o mesmo passo tiver as duas coisas (chamada direta e depois conferência do efeito na tela), gere as duas imagens: a da API e a "tela + painel" da conferência.

   Para cada passo de tela relevante:
   - tire o print com `computer` → `screenshot`, `scale: 1` e `save_to_disk: true` (print em escala menor deixa o painel ilegível);
   - leia as chamadas do passo. O `read_network_requests` às vezes deixa de capturar as chamadas da SPA depois de um `clear`; a fonte mais confiável é a lista do próprio navegador: `performance.getEntriesByType('resource').filter(e => e.name.includes('<host da API>')).map(e => [e.name, e.responseStatus])` (via `javascript_tool`). Para ter o corpo da resposta, refaça a mesma chamada GET com `fetch` e o token da sessão (Anexo C) e devolva só os campos relevantes. Chamadas que alteram dados (POST, PUT, DELETE) nunca são refeitas só para capturar: registre o que a tela mostrou e o status;
   - leia o console com `read_console_messages` (só erros e avisos da aplicação; mensagens de extensões do Chrome não contam; se não houver, o painel mostra "Nenhuma mensagem no console.");
   - **select nativo:** a lista aberta de um `<select>` não aparece no print. Para registrar as opções, leia-as pelo DOM (texto, `disabled`) e expanda o select só na tela antes do print (`select.size = <n>`), sem alterar dados. Diga isso no registro do TC;
   - monte o JSON do passo (formato no início de `scripts/painel.py`; uso em `references/evidencias.md`) e gere a evidência em `/mnt/user-data/outputs/qa/<card>/<TC>/NN_descricao.png` (NN sequencial, descrição curta sem espaço). Dados reais de cliente vão borrados com `--blur`;
   - monte também o curl de cada chamada relevante (Anexo B) em `/mnt/user-data/outputs/qa/<card>/<TC>/NN_curl_<metodo>_<recurso>.txt`;
   - grave os arquivos na pasta de evidências do QA com `device_commit_files` (`stagedPath` = arquivo em `/mnt/user-data/outputs/...`, `devicePath` = `<pasta>/<card>/evidencias/<TC>/<arquivo>`). Assim as evidências ficam na máquina do analista;
   - copie as mesmas evidências para `/home/claude/qa-up/<card>/<TC>/`: é de lá que o Chrome aceita subir para o ADO (Anexo E, em `references/upload-evidencias.md`).
4. **Chamada direta ao servidor** (cenários de "via servidor", segurança, permissão): faça `fetch` no contexto da página com o token da sessão lido do armazenamento do app (Anexo C). Nunca devolva o token na saída da ferramenta.
   - Meça o tempo e o tamanho da resposta no próprio `fetch` (snippet no Anexo F) e devolva método, URL, headers enviados (com `Bearer <TOKEN>`), payload, status, tempo, tamanho e corpo da resposta.
   - Monte o JSON da chamada (formato no início de `scripts/api_print.py`) e gere a evidência com `python3 <pasta-da-skill>/scripts/api_print.py --req <chamada.json> --out /mnt/user-data/outputs/qa/<card>/<TC>/NN_api_<metodo>_<recurso>.png`.
   - Abra a imagem com `Read` e confira se o token e os segredos aparecem mascarados antes de subir.
   - Gere também o curl (Anexo B) e salve, grave na pasta do QA e copie para `/home/claude/qa-up/` como as demais evidências (passo 3).
5. **Resultado do TC:** Aprovado, Aprovado com ressalva (⚠️ + motivo), Reprovado ou Bloqueado. Se reprovado, compare com produção (regra 8) e siga para a seção 4. Se bloqueado, pare o TC, registre o que já foi feito e o motivo do bloqueio e siga para a seção 3.

## 3. Registro no TC
Ao terminar cada TC (não deixe para o fim do card):
1. **Anexos primeiro:** suba as evidências e os curls do TC pelo Anexo E. Guarde o id de cada anexo: ele vai na imagem do passo a passo.
2. **Passo a passo na Descrição do TC** (`System.Description`, HTML):
   - cabeçalho do ciclo: `<b>Ciclo <N> — <dd/mm/aaaa> — <Aprovado | Aprovado com ressalva | Reprovado | Bloqueado: motivo curto></b>`;
   - linha `Usuário/conta: <login e perfil> / <cliente>`;
   - para cada cenário do Gherkin: título do cenário em negrito, passos numerados (`<b>1.</b> Acessei ...`), `Resultado:` com o que aconteceu, a ressalva com ⚠️ quando houver e a evidência no texto: `<img src="https://dev.azure.com/<ORG>/<PROJECT_ID>/_apis/wit/attachments/<id>?fileName=<arquivo>" style="max-width:100%;">`;
   - no fim, dados criados no teste e observações (ex.: select expandido só na tela);
   - em reteste, coloque o novo ciclo **acima** do anterior e mantenha o histórico.
3. **Campos:**
   - Payloads e curls: `<CAMPO_PAYLOADS>` (curls com `Bearer <TOKEN>`);
   - Data Fim: `<CAMPO_DATA_FIM>`;
   - Última execução: `<CAMPO_ULTIMA_EXECUCAO>`;
   - Esforço: `<CAMPO_ESFORCO>` e `Microsoft.VSTS.Scheduling.Effort` com o mesmo valor, **em horas inteiras** (cálculo abaixo).

   **Cálculo do esforço (sempre em minutos primeiro, depois em horas):**
   1. **Minutos do ciclo:** do **início do ciclo anotado na sessão** (seção 2, passo 1) até agora, os dois em UTC (`Math.round((Date.now() - Date.parse(inicioCicloISO)) / 60000)`). Não use a Data Início do ADO, porque ela guarda o primeiro toque no TC.
   2. **Minutos acumulados:** no primeiro ciclo, são os minutos do ciclo. Em reteste, some os minutos dos ciclos anteriores do mesmo TC, lidos na tabela "Esforço por ciclo" do `<pasta>/<card>/resumo-execucao.md`. **Nunca use as horas já gravadas no ADO para somar**, porque elas já foram arredondadas (28 min viram 1 h). Se os minutos anteriores não estiverem registrados, pergunte ao QA quantos minutos levou antes.
   3. **Horas:** `Math.max(1, Math.ceil(minutosAcumulados / 60))`. Até 60 min = 1; 61 a 120 min = 2; e assim por diante. Ex.: reteste com 28 min antes + 14 min agora = 42 min = 1.
   4. **Grave as horas, nunca os minutos.** O valor do campo é o número de horas (1, 2, 3...). Escrever os minutos no campo (ex.: 15 para 15 minutos) é erro.
   5. **Confira antes de gravar:** mostre ao QA, na mensagem de fim do TC, `início do ciclo HH:MM → fim HH:MM = N min (acumulado M min) → esforço X`. Se o resultado passar de 8 h ou o início do ciclo não estiver anotado, pare e pergunte ao QA em vez de gravar.
   6. Registre os minutos do ciclo e o acumulado na tabela "Esforço por ciclo" do `resumo-execucao.md` (TC, ciclo, início, fim, minutos, acumulado, horas gravadas), logo depois de gravar no ADO, para o próximo reteste ter a base certa.
4. **Outcome no Test Plans** (Anexo A, passo 4): `passed`, `failed`, `blocked` (cenário bloqueado) ou `notApplicable` (cenário cancelado pelo QA). O valor vai no mesmo corpo do PATCH do Anexo A: `{"id": <pointId>, "results": {"outcome": "blocked"}}`.
5. **Estado:** aplique a regra 5 (aprovado sem ressalva vai para Concluído com outcome `passed`; reprovado vai para Pendente com outcome `failed`; bloqueado vai para Pendente com outcome `blocked`; aprovado com ressalva segue a decisão do QA; cancelado pelo QA vai para Cancelado com outcome `notApplicable`).
6. Mostre ao QA, no chat, um resumo curto do TC (resultado + o que chamou atenção; se bloqueado ou cancelado, a justificativa) antes de seguir para o próximo.
7. **Comentário na Discussion (só bloqueado ou cancelado):** publique a justificativa na aba **Discussion** do TC, junto com a mudança de estado.
   - Texto curto, em primeira pessoa, como o QA escreveria, sem emoji e sem horário: `Cenário bloqueado: <motivo>.` ou `Cenário cancelado: <motivo>.` Se o bloqueio depende de outro card ou bug, cite-o com `#<id>` para virar link. Ex.: `Cenário bloqueado: o ambiente de staging está fora do ar desde o início do teste.` / `Cenário cancelado: o fluxo foi removido do escopo do card, conforme alinhado com o PO.`
   - Grave pelo MCP do ADO (`wit_work_item_comment_write`, ação de adicionar comentário no TC). Se ele não estiver disponível, use a aba do ADO no Chrome: `fetch('/<PROJETO>/_apis/wit/workItems/<TC>/comments?api-version=7.1-preview.4', {method: 'POST', credentials: 'include', headers: {'Content-Type': 'application/json', 'X-TFS-FedAuthRedirect': 'Suppress'}, body: JSON.stringify({text: '<comentário>'})})` e confira o status 200.
   - Um comentário por ocorrência. Em cancelamento, use a justificativa que o QA deu, sem reescrever o sentido.

## 4. Bugs
Antes de abrir, mostre ao QA o rascunho (título, passos, esperado, obtido, severidade) e espere o OK. Se o TC foi **reprovado**, ele já vai para Pendente (outcome `failed`), sem pergunta. Se o caso é **Aprovado com ressalva**, pergunte na mesma mensagem se a ressalva vira bug e o que acontece com o TC (regra 5). Se o QA preferir, registre como comentário em um bug existente em vez de abrir outro.
- Tipo **Bug**, projeto `<PROJETO>`, mesma Área e Sprint do card, mesmo Produto e Ambiente do TC.
- Título objetivo descrevendo o comportamento errado.
- Descrição (`System.Description`): o comportamento esperado em uma ou duas frases.
- Passos para reprodução: `<CAMPO_PASSOS_REPRO>`, no formato: linha `Usuário/conta`, passos numerados, `Resultado atual:`, comparação com produção (ou o motivo de não comparar) e as evidências no texto (`<img src=".../_apis/wit/attachments/<id>?fileName=<arquivo>">`; pode reaproveitar os anexos já enviados ao TC).
- Comportamento esperado: `<CAMPO_COMPORTAMENTO_ESPERADO>`.
- Payloads e curls: `<CAMPO_PAYLOADS>`.
- Time atuante (Backend, Frontend ou Backend + Frontend): `<CAMPO_TIME_ATUANTE>`.
- QA responsável: `<CAMPO_QA>`, com o e-mail do QA da sessão.
- `Microsoft.VSTS.Common.Severity` (`2 - High`, `3 - Medium`, `4 - Low`) e `Microsoft.VSTS.Common.Priority`: proponha no rascunho e use o que o QA confirmar.
- Sem dev responsável, sem emoji.
- Vínculos: filho do card testado e relacionado ao TC que falhou.
- Depois de abrir: se o TC foi reprovado, ele já vai para Pendente (outcome `failed`); se foi ressalva, aplique o destino que o QA escolheu. Grave o cabeçalho do ciclo na Descrição e cite o número do bug no cenário correspondente.

## 5. Pausa e fechamento
**Pausa** (o QA vai parar ou a sessão está longa): grave `<pasta>/<card>/contexto-continuacao.md` com URLs, contas usadas (sem senha) e em qual navegador cada uma está logada, Test Plan/Suite, situação de cada TC, onde parou o TC em execução (com o horário de início do ciclo dele), dados criados, bugs abertos e combinados com o QA. Diga ao QA para iniciar a próxima sessão com "continue a execução do card <id>".

**Fechamento** (todos os TCs confirmados foram executados):
1. Grave ou atualize `<pasta>/<card>/resumo-execucao.md`: tabela de TCs (resultado, outcome, início, fim, esforço), tabela "Esforço por ciclo" (seção 3), bugs, não executados e por quê, bloqueados e o motivo, cancelados e o motivo, dados criados, ressalvas.
2. **Opcional:** se a sua organização mantém um log de atividades de QA (outra skill ou rotina), registre nele, em silêncio, o que já foi levantado.
3. Liste para o QA os **cenários não mapeados** que surgiram durante os testes.
4. Mostre ao QA o resumo final em poucas linhas.

## Anexos
Os anexos citados acima ficam em arquivos da própria skill. Leia o arquivo quando o passo pedir.
- **Configuração da organização:** `references/config.md`
- **Anexo A (Test Plans via API REST):** `references/test-plans-api.md`
- **Anexo B (formato do curl):** logo abaixo.
- **Anexo C (dicas técnicas, token, upload):** `references/dicas-tecnicas.md`
- **Anexos D e F (uso e formato dos scripts de evidência):** `references/evidencias.md`
- **Anexo E (subir evidências para o work item):** `references/upload-evidencias.md`
- **Scripts:** `scripts/painel.py` (evidência "tela + painel") e `scripts/api_print.py` (chamada direta à API). Rode-os direto da pasta da skill, usando o caminho base informado quando a skill é carregada (`<pasta-da-skill>`).

## Anexo B: formato do curl
```
curl --location --request <MÉTODO> '<url completa>' \
  --header 'Accept: application/json, text/plain, */*' \
  --header 'Authorization: Bearer <TOKEN>' \
  --header 'Content-Type: application/json' \
  --data-raw '<corpo, com segredos trocados por ***>'
```
Acrescente abaixo a resposta (status e corpo resumido).
