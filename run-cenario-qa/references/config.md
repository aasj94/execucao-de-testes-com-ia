# Configuração da organização

Preencha uma vez. Tudo que o `SKILL.md` mostra entre `<...>` vem daqui. Deixe em branco o que não existir no seu processo; a skill pergunta ao QA quando faltar.

## Azure DevOps
| Chave | Valor |
|---|---|
| `<ORG>` | _nome da organização no ADO_ |
| `<PROJETO>` | _nome do projeto, ex.: Engenharia_ |
| `<PROJECT_ID>` | _GUID do projeto (aparece nas URLs de anexos do work item)_ |

URL base usada nas chamadas REST: `https://dev.azure.com/<ORG>/<PROJETO>/_apis`. Se a sua organização usa o domínio antigo, troque por `https://<ORG>.visualstudio.com/<PROJETO>/_apis`.

## Padrão de nome do Test Plan
O Test Plan da sprint é o que tem a mesma iteration do card (`System.IterationPath`). Descreva aqui o padrão de nome usado, para a skill reconhecer o plano certo:

- Padrão: _ex.: "Test Plan Sprint <NN>"_

## Campos customizados do ADO
Os nomes de referência (`Custom.<...>`) dependem do processo de cada organização. Para descobri-los: abra um TC ou um Bug, chame `GET /_apis/wit/workitems/<id>?$expand=all&api-version=7.1` e procure o campo pelo rótulo.

| Chave | Para que serve | Referência no seu ADO |
|---|---|---|
| `<CAMPO_GHERKIN>` | Gherkin do TC | |
| `<CAMPO_DATA_INICIO>` | Data Início (primeiro toque no TC) | |
| `<CAMPO_DATA_FIM>` | Data Fim | |
| `<CAMPO_ULTIMA_EXECUCAO>` | Última execução | |
| `<CAMPO_ESFORCO>` | Esforço em horas (além de `Microsoft.VSTS.Scheduling.Effort`) | |
| `<CAMPO_PAYLOADS>` | Payloads e curls | |
| `<CAMPO_PASSOS_REPRO>` | Passos para reprodução (Bug) | |
| `<CAMPO_COMPORTAMENTO_ESPERADO>` | Comportamento esperado (Bug) | |
| `<CAMPO_TIME_ATUANTE>` | Time atuante (Bug) | |
| `<CAMPO_QA>` | QA responsável (Bug) | |

## Campos exigidos para sair de Pendente (opcional)
Se o seu processo só deixa o TC sair de Pendente com estes campos preenchidos, liste os campos e os valores aceitos:

| Campo | Valores aceitos / padrão |
|---|---|
| Módulo | |
| Tipo de teste | _ex.: Exploratório manual_ |
| Ciclo de teste | _1 na primeira execução; +1 a cada reteste_ |
| Complexidade | _ex.: 2 - Simples, 3 - Moderado_ |

## Token de sessão do app testado
Para chamadas diretas à API (seção 2, passo 4), a skill lê o token da sessão já logada, dentro do `fetch`, sem nunca devolvê-lo. Informe onde o app guarda esse token:

- Armazenamento: _ex.: `localStorage['<chave>']`, `sessionStorage` ou cookie_
- Formato: _ex.: `{access_token, token_type}`_
- Host da API por ambiente: _ex.: `https://api.<ambiente>.<seu-dominio>` (confirme na aba de rede)_
