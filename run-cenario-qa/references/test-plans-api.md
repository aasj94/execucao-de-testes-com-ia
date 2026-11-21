# Anexo A: Test Plans
A ferramenta de Test Plans do MCP do ADO pode responder 401 (o acesso dela não cobre Test Plans). Nesse caso, ou por padrão, use a API REST com `javascript_tool` numa aba do ADO já logada (ex.: o próprio TC aberto em `https://dev.azure.com/<ORG>/<PROJETO>/_workitems/edit/<TC>`). Em todas as chamadas: `credentials: 'include'` e header `'X-TFS-FedAuthRedirect': 'Suppress'`. Base: `https://dev.azure.com/<ORG>/<PROJETO>/_apis`.
1. **Achar os points dos TCs** (todos de uma vez):
   - `POST <base>/test/points?api-version=7.1-preview.2` com corpo `{"PointsFilter": {"TestcaseIds": [<TC>, <TC>, ...]}}`.
   - Cada item de `points` traz `testCase.id`, `id` (point), `testPlan.id`, `suite.id` e `outcome`. TC que não aparece na lista não está em nenhuma suite.
2. **Achar o plano e a suite da sprint do card:**
   - `GET <base>/testplan/plans?filterActivePlans=false&includePlanDetails=true&api-version=7.1` e escolha o plano com `iteration` igual ao `System.IterationPath` do card (ex.: `Projeto\Sprint 12` → o plano da Sprint 12, conforme o padrão de nome em `config.md`). Se vier `x-ms-continuationtoken` no header, busque as próximas páginas.
   - `GET <base>/testplan/Plans/<plano>/suites?api-version=7.1` e use a suite raiz (`rootSuite.id` do plano). Se houver outras suites e uma delas for do produto ou do card, prefira essa; na dúvida, pergunte ao QA.
3. **Incluir os TCs sem suite:**
   - `POST <base>/testplan/Plans/<plano>/Suites/<suite>/TestCase?api-version=7.1` com `Content-Type: application/json` e corpo `[{"workItem": {"id": <TC>}}, ...]`.
   - A resposta traz `pointAssignments[].id` de cada TC: esse é o point para gravar o outcome.
4. **Gravar o outcome:**
   - `PATCH <base>/testplan/Plans/<plano>/Suites/<suite>/TestPoint?api-version=7.1` com `Content-Type: application/json` e corpo `[{"id": <pointId>, "results": {"outcome": "passed"}}]` (`failed`, `blocked` ou `notApplicable` conforme o caso).
   - Grave logo após registrar o TC e confira o status 200.
