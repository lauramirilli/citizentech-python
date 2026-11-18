## Equipe

| Nome | RM |
|------|----|
| Bruce Li | 569168 |
| Felipe Rorato | 570419 |
| Giovanna Andrade Parejas | 569041 |
| Laura Cardin Mirilli | 570841 |

# prompts.md — Uso de IA na aplicação Python do Amparo
 
## 1. Ferramentas utilizadas
 
| Ferramenta | Finalidade |
|---|---|
| Claude | Planejar a arquitetura da aplicação, pesquisar fontes para os limites de risco, revisar decisões de interface e de compatibilidade |
| Claude Code | Revisão de código e testes automatizados do fluxo completo do programa |
 
## 2. Registro de interações
 
### Entrada 1 — Esboço inicial da aplicação
**Finalidade:** planejar o que a aplicação faz antes de programar.
 
**Prompts:**
> Vamos começar a esboçar a aplicação de python.
 
**O que a IA sugeriu:** o papel do Python como "cérebro" do Amparo, um menu de funcionalidades, o cálculo do índice de calor e a classificação em três níveis, a estrutura em módulos e os arquivos JSON. Também sugeriu uma tabela que relaciona cada requisito da disciplina com o ponto do programa onde ele aparece.
 
**O que decidimos:**
- Aceitamos a estrutura modular e a persistência em JSON.
- Escolhemos uma pessoa atendida por execução, porque o dispositivo fica dentro da casa de uma pessoa só. Isso simplifica os dados: um `perfil.json` com um único dicionário.
- Previsão via API Open-Meteo (`requests`), com fallback para um JSON local se a rede falhar.
**Verificação:** conferimos a proposta contra o enunciado e cada requisito obrigatório aparece em pelo menos um ponto do programa.
 
---
 
### Entrada 2 — Fontes para os limites de risco
**Finalidade:** justificar com fontes os limites de "chuva forte" e de "subida rápida de temperatura". Os mesmos limites também são usados no Edge (ESP32) e no relatório de Cálculo.
 
**Prompt:**
> pesquise fontes para os dois limites
 
**O que a IA trouxe:**
- **Chuva:** a escala de avisos do INMET. Amarelo: 20–30 mm/h ou até 50 mm/dia. Laranja: 30–60 mm/h ou 50–100 mm/dia. Vermelho: acima de 60 mm/h ou acima de 100 mm/dia.
- **Subida de temperatura:** a IA informou que **não encontrou** limite oficial em °C/h para ambiente doméstico. Propôs usar a taxa para projetar o índice de calor 1 hora à frente, aproximação linear pela derivada, e antecipar as faixas da NOAA.
- Trouxe também a orientação da Health Canada (26 °C interno para idosos), sugerindo que fosse usada só como referência.
**O que decidimos:**
- Adotamos a escala do INMET: ≥ 20 mm/h = ATENÇÃO e ≥ 30 mm/h = PERIGO.

---
 
### Entrada 3 — Risco sempre visível (painel)
**Finalidade:** melhorar a experiência do usuário.
 
**Contexto:** no esboço da IA, "Avaliar risco agora" era uma opção do menu.
 
**Prompt (comentário nosso no esboço):**
> a avaliação do risco não deveria estar fora do menu? assim o usuário consegue ver a todo momento o risco
 
**O que a IA fez:** concordou e transformou o risco num painel fixo exibido acima do menu. Ela acrescentou dois cuidados: o painel usa a última leitura e uma previsão em cache, para não chamar a API a cada volta do loop, e a checagem "Você está bem?" só dispara quando o nível muda para PERIGO, e não a cada vez que o menu aparece.
 
**O que decidimos:** aceitamos. A mudança partiu da equipe: a IA não tinha considerado que a pessoa precisa ver o risco o tempo todo.

---

### Entrada 4 — Bairros e abrigos de exemplo
**Finalidade:** definir os dados de exemplo (bairros com coordenadas e abrigos fictícios) usados na demo.
 
**Prompt:**
> pesquise os bairros em São Paulo que são mais afetados por eventos climáticos e crie abrigos fictícios para o abrigo dos idosos em situações de risco.
 
**O que a IA propôs:**
- Três bairros, cada um com um cenário de risco diferente: Sapopemba (calor; um dos distritos com mais idosos), Jardim Pantanal (alagamento; várzea do Tietê) e Parque Brasilândia (deslizamento; moradias em área de altíssimo risco). Para cada um, uma fonte pública.
- Sete abrigos fictícios, com atributos de acessibilidade variados para que o filtro mostre resultados diferentes.
- Separar as recomendações de chuva entre alagamento e deslizamento.
- Colocar os abrigos de chuva em área alta, fora da várzea e da encosta.
**O que decidimos:** aceitamos a sugestão da IA.

---

### Entrada 5 - Escrita de docstrings
**Finalidade:** analisar as funções de `risco.py` e escrever as docstrings de cada uma para que quem leia o código entenda.

**Prompt:**
> analise as funções de risco.py e escreva docstring para cada uma, descrevendo comportamento e retorno

**O que a IA propôs:** Escreveu corretamente sobre cada função.
**O que decidimos:** depois de ler cada uma, aceitamos a sugestão da IA.
 
### Entrada 6 — Dicionário de recomendações
**Finalidade:** definir o que o Amparo orienta a pessoa a fazer em cada situação de risco.

**Prompt:**
> o que é o dicionário de recomendações?

Na sequência:
> pode montar o rascunho

**O que a IA propôs/gerou:**
- Um dicionário com tupla `(tipo, nível)` como chave e lista de recomendações como valor; a primeira da lista aparece no painel.
- Tipos `"alagamento"` e `"deslizamento"` no lugar de `"chuva"`, porque a orientação muda entre os dois cenários (definido pelo `risco_chuva` do perfil).
- Uma mensagem geral para o nível NORMAL, para o painel nunca ficar vazio.
- Rascunho dos textos: uma ação por frase, a mais urgente primeiro e os telefones de emergência no nível PERIGO.

**O que decidimos:** aceitamos a sugestão da IA.

### Entrada 7 — Caminhos dos arquivos com o módulo `os`
**Finalidade:** fazer o programa encontrar a pasta `dados/` independentemente de onde ele é executado.
 
**Contexto:** ao testar o `arquivos.py`, a leitura de um JSON corrompido (`quebrado.json`) devolvia `None` sem mostrar o aviso esperado.
 
**Prompt:**
> o quebrado.json não tá funcionando
 
(enviado junto com uma captura do terminal mostrando a saída do teste)
 
**O que a IA explicou:** o arquivo não estava sendo encontrado, e por isso o código caía no `FileNotFoundError` em vez do `JSONDecodeError`. Um caminho relativo como `"quebrado.json"` é procurado a partir da pasta onde o terminal está (`gs-2/`), e não da pasta do script (`gs-2/python/`). A IA apontou que o mesmo problema poderia acontecer na correção, se o projeto fosse aberto a partir de outra pasta: o programa não encontraria a pasta `dados/` e começaria sem perfil e sem abrigos.
 
**O que decidimos:**
- Montar os caminhos a partir da localização do próprio `arquivos.py`, com `os.path.dirname(os.path.abspath(__file__))`, guardado na constante `PASTA_BASE`.
- Criar a constante `PASTA_DADOS = os.path.join(PASTA_BASE, "dados")`.
- `ler_json` e `salvar_json` passam a receber só o nome do arquivo e montam o caminho completo com `os.path.join`.
- As mensagens de aviso mostram só o nome do arquivo, e não o caminho completo.

### Entrada 8 — Registro de leituras (horário e simulação)
**Finalidade:** implementar a opção "Registrar leitura", com leitura manual ou simulada.

**Prompts:**
> me ajude a corrigir o formato do horário no cadastros.py e me dê uma ideia de como simular as temperaturas e umidade de maneira factível

**O que a IA propôs/gerou:**
- Identificou um problema de horário: na demonstração, as leituras são registradas com segundos de intervalo, o que faria a taxa de variação explodir e dispararia a antecipação à toa. Propôs simular o relógio do sensor, no qual a primeira leitura usa o horário atual e cada nova leitura, o da anterior + 10 minutos.
- Explicou como detectar a primeira leitura: a lista do `leituras.json` vem vazia (`ler_json` devolve `[]` quando o arquivo não existe).
- Propôs uma simulação realista: partir da última leitura e variar pouco (temperatura −0,3 a +0,8 °C, umidade +2%/-2%), em vez de sortear valores independentes que pulariam de 24 para 38 °C.
- Reescreveu parte da função `registrar_leitura()` no `cadastros.py`, com o horário salvo como texto (`isoformat`) para o JSON.

**O que decidimos:** aceitamos a função gerada pela IA.

**Verificação:**
- [x] Registrar três leituras simuladas e conferir os horários com 10 minutos de diferença.
- [x] Testar entrada inválida na leitura manual ("abc") e valor com vírgula ("31,5").
- [x] Conferir o `leituras.json` gerado.

### Entrada 9 — Consumo da API de previsão (Open-Meteo)
**Finalidade:** buscar a previsão real de chuva do bairro da pessoa atendida, mantendo o programa funcional sem internet.
 
**Prompt:**
> me ajude a construir a parte de consumir API
 
**O que a IA propôs/gerou:**
- Conferiu, em buscas na documentação da Open-Meteo e em exemplos de uso, o endereço da API (`/v1/forecast`), os parâmetros (`latitude`, `longitude`, `hourly=precipitation`, `timezone`, `forecast_days`) e que não é preciso chave de acesso.
- Escreveu a função `buscar_previsao_real(bairro)` no `previsao.py`: usa as coordenadas do dicionário `BAIRROS`, pede a chuva de cada hora do dia e calcula `mm_hora_max` (maior valor) e `mm_dia` (soma das 24 horas).
- Tratamento de erros com fallback para a última previsão salva: bairro sem coordenadas, falta de internet ou timeout (`requests.RequestException`), resposta em formato inesperado (`KeyError`, `ValueError`) e horas sem valor (`None`), ignoradas nas contas.
- `timeout=10` na requisição, para o programa não ficar travado esperando o servidor.

**O que decidimos:** modificamos a mensagem no terminal. A requisição era realizada com sucesso mas o usuário não recebia aviso no terminal.
 
**Verificação:**
- [x] Teste sem acesso à API (feito pela IA, cujo ambiente não alcança a Open-Meteo): o aviso "Sem conexão" aparece e a função devolve a previsão salva.
- [x] Teste com resposta simulada da API (feito pela IA): 35,1 mm/h de máximo e 55,8 mm no dia, salvos com `"fonte": "Open-Meteo"`.
- [x] Teste com resposta em formato inesperado e com bairro sem coordenadas (feito pela IA): avisos e fallback corretos.
- [x] Teste com internet de verdade, conferindo `"fonte": "Open-Meteo"` no `previsao.json`.
- [x] Teste com o Wi-Fi desligado.

### Entrada 10 — Visual do pedido de ajuda (`ajuda.py`)
**Finalidade:** deixar a checagem e o pedido de ajuda mais claros visualmente para o público do Amparo.

**Prompt:**
> no ajuda.py vc consegue deixar ele mais bonito visualmente?

**Contexto:** o `ajuda.py` já estava funcionando, com as correções da revisão anterior feitas por nós (loop infinito na checagem, `alertas.json` sendo sobrescrito por uma string, rede não acionada para quem não mora sozinho, falha quando o `rede.json` não existe).

**O que a IA propôs/gerou:** reescreveu o `ajuda.py` mantendo a mesma lógica, com mudanças de apresentação e organização:
- Função `titulo()` para os cabeçalhos de seção, com a mesma linha `─` do painel.
- Etapas numeradas no pedido de ajuda ("1º Família e cuidadores", "2º Voluntários no bairro"), deixando visível a ordem do escalonamento.
- Ícones sempre acompanhados de texto (📨 aviso enviado, ✅ sucesso, ⚠️ problema).
- Telefones de emergência alinhados em colunas com formatação de f-string (`{nome:<14}`).
- A checagem passou a mostrar as três respostas possíveis (s, n, Enter) antes de perguntar.
- A pergunta sobre o familiar ganhou o rótulo "(simulação)".
- A rede passou a ser separada em duas listas (familiares e voluntários do bairro) num único `for`, e surgiu a função `avisar_pessoas()`, reaproveitada nas duas etapas.
- Sem familiar cadastrado, o programa pula direto para os voluntários; no pedido manual cancelado, mostra "Pedido cancelado.".

**O que decidimos:** aceitamos.

### Entrada 10 — Arquivo de abrigos (`abrigos.json`)
**Finalidade:** criar os dados de abrigos e pontos de acolhimento usados na opção "Abrigos próximos".

**Prompt:**
> monte com dados fictícios o arquivo abrigos.json

**O que a IA propôs/gerou:**
- O arquivo `abrigos.json` com 7 abrigos fictícios distribuídos entre os três bairros (Sapopemba, Jardim Pantanal e Parque Brasilândia), seguindo a tabela do esboço.
- Endereços marcados como fictícios ("Rua Fictícia..."), para não serem confundidos com locais reais e para cumprir a regra de usar apenas dados simulados.
- Campo `"tipos"` como lista, porque alguns abrigos atendem calor e chuva ao mesmo tempo.
- Acessibilidade variada de propósito: cada bairro tem ao menos um abrigo totalmente acessível (rampa, banheiro adaptado e espaço para cadeira de rodas) e outros com acessibilidade parcial, para que o filtro mostre resultados diferentes.
- Abrigos de chuva em área alta, fora da várzea e da encosta (decisão já registrada na entrada 5).
- Horário "24h em alerta" reescrito como "24h durante alertas", mais claro para o usuário.

**O que decidimos:** aceitamos as sugestões.

### Entrada 11 — Teste completo do fluxo com o Claude Code
**Ferramenta:** Claude Code (Anthropic)
**Finalidade:** testar o programa inteiro a partir do `main.py`, incluindo casos extremos, antes da entrega.

**Prompt:**
> quero que você teste todo o fluxo de main.py testando todos os edge cases.

**O que a IA fez:** rodou 56 cenários numa cópia isolada da pasta `python/`, simulando as respostas do usuário (`input()`) e a API Open-Meteo, sem alterar os arquivos originais. Resultado: 35 passaram e 21 falharam.

**Problemas encontrados no uso normal:**
- Falso alarme de PERIGO: a leitura recebe o horário "anterior + 10 min" mesmo quando a anterior é antiga, o que gera uma taxa de subida irreal e dispara a checagem.
- A leitura simulada pode passar do limite de 50 °C (só a umidade era limitada).
- No cadastro do perfil, o bairro é pedido com o texto "Bairro do voluntário:" (função reaproveitada da rede de apoio).
- Na remoção da rede, um número decimal (ex.: 1.9) é aceito e arredondado para baixo.
- Ctrl+C e Ctrl+D encerram o programa com traceback em vez de uma mensagem.
- Uma resposta inválida da API aparece como "Sem conexão", porque o erro de JSON do `requests` também é um `RequestException` e cai no primeiro `except`.
- Em valores extremos (ex.: 50 °C e 100%), a sensação térmica aparece como 206 °C: a fórmula de Rothfusz está sendo usada fora da faixa em que é válida.

**Problemas com arquivos ou respostas malformadas:** JSON editados à mão com estrutura errada (perfil vazio, leitura sem horário, abrigo sem acessibilidade, voluntário sem bairro etc.) e respostas da API em formato inesperado encerram o programa com erro.

**O que passou:** validação das entradas, primeira execução, falhas ao salvar, checagem disparando só na transição para PERIGO, ordem de acionamento da rede, fallbacks da API (erro HTTP, timeout, resposta vazia), abrigos com filtro de mobilidade, rede, histórico, edição do perfil e risco de chuva sem leitura.

**O que decidimos:** corrigimos os bugs apresentados. A questão dos valores extremos foi corrigida mostrando a mensagem: "acima de 54 °C".

### Entrada 12 — README do projeto
**Finalidade:** escrever o `README.md` com a descrição do projeto e as instruções de execução.

**Prompt:**
> escreva o readme

Na sequência:
> rodar python main.py funciona no windows tb? se nao, altera o readme

**O que a IA propôs/gerou:**
- O `README.md` completo, começando pela Ficha da CitizenTech pedida nas instruções da GS: nome, bairros, cidadão beneficiado, problema em uma frase, como funciona, o que cada parte faz, indicador de impacto e ODS.
- As seções de funcionalidades (as 8 opções do menu e a checagem automática), as regras de decisão do risco (faixas da NOAA, escala do INMET, antecipação de 1 hora, desempate pela chuva) e a estrutura dos arquivos e dos dados.
- Uma seção explicando as simulações do protótipo: leituras simuladas, relógio de 10 minutos do sensor, previsão simulada, Enter como "não consigo responder" e envio de avisos simulado.
- Uma tabela relacionando cada conceito da disciplina ao ponto do código onde ele aparece.
- As limitações conhecidas e o link para o `prompts.md`.
- Depois da segunda pergunta, a IA explicou que `python main.py` pode falhar no Windows e reescreveu a seção "Como executar": passos para o PyCharm, comandos por sistema (`py` no Windows e `python3` no macOS/Linux) e instalação com `-m pip`, para o `requests` ser instalado no mesmo Python que executa o programa.

**O que decidimos:** preenchemos com informações adicionais (integrantes, link do repositório).

**Verificação:**
- [x] Preencher o link do repositório e os nomes e RMs da equipe.

## 3. Funcionalidades desenvolvidas ou modificadas com auxílio da IA
 
| Funcionalidade / arquivo | Papel da IA | O que a equipe fez |
|---|---|---|
| Arquitetura geral e menu | Propôs | Ajustou (uma pessoa por execução, painel fixo) |
| Limites de risco (`risco.py`) | Pesquisou as fontes e propôs a projeção | Escolheu os limites e decidiu não usar os 26 °C |
| Painel de risco (`painel.py`) | Implementou a ideia da equipe com cache e gatilho | Propôs a mudança |
| Dados de exemplo (`BAIRROS`, `abrigos.json`) | Escolheu os bairros com fonte e criou os abrigos fictícios | Revisamos e aceitamos as sugestões|
| Economizou tempo da equipe escrevendo docstring para as funções implementadas | Analisou cada função e descreveu corretamente | Revisamos e aceitamos as sugestões|
| Pedido de ajuda (`ajuda.py`) | Revisou o código e apontou os erros; depois reorganizou o visual a pedido da equipe | Escreveu a lógica, corrigiu os erros apontados e testou |
| Dados de exemplo (`BAIRROS`, `abrigos.json`) | Escolheu os bairros com fonte e criou o arquivo com os 7 abrigos fictícios | Revisou a sugestão e aceitou |
 
## 4. Análise crítica

### Benefícios

- **Planejamento mais rápido e mais completo.** A IA ajudou a transformar a ideia do Amparo numa arquitetura de módulos e a cruzar cada requisito da disciplina com um ponto do programa. Isso evitou descobrir, perto da entrega, que algum conceito obrigatório tinha ficado de fora.
- **Busca de fontes para as regras de decisão.** Os limites de chuva (INMET) e de calor (NOAA) vieram de pesquisas feitas com a IA, o que deu fundamento às regras do código e ligou o Python ao relatório de Cálculo.
- **Diagnóstico de erros.** Em vários momentos, a IA explicou a causa de um erro em vez de só corrigi-lo: o caminho relativo que fazia o programa não encontrar a pasta `dados/`, o `None` acessado antes de ser testado, a atualização do `nivel_anterior` no lugar errado. Entender a causa nos ajudou a não repetir o erro nos módulos seguintes.
- **Testes que não faríamos sozinhos.** O Claude Code rodou 56 cenários, incluindo casos extremos (arquivos editados à mão, respostas malformadas da API, Ctrl+C). Ele encontrou 21 falhas, entre elas um falso alarme de PERIGO que apareceria no uso normal.

### Limitações

- **As fontes precisaram ser conferidas.** A escala do INMET foi trazida a partir de notícias que a reproduziam, e não do site oficial. Para outros pontos, como um limite de subida de temperatura em °C/h, a IA informou que não existe valor oficial. A decisão de usar a projeção de 1 hora no lugar foi nossa.
- **O código gerado pela IA também tinha erros.** Algumas falhas encontradas nos testes estavam em trechos escritos pela própria IA: a leitura simulada podia passar de 50 °C, e a mensagem "Bairro do voluntário" aparecia no cadastro do perfil. A primeira versão do índice de calor também usava uma simplificação que criava um salto na fórmula, que só foi percebido na análise de limites do relatório de Cálculo e motivou a correção para o critério completo da NOAA.
- **A IA nem sempre considerou o usuário real.** Na primeira proposta, o risco era uma opção do menu. A mudança para um painel sempre visível partiu da equipe, pensando em quem precisa ver o risco o tempo todo.
- **A IA não testou tudo.** O ambiente da IA não acessava a API Open-Meteo. O teste com a previsão real foi feito por nós.

### Dificuldades

- **Entender o código antes de aceitá-lo.** Em alguns momentos pedimos à IA que escrevesse partes das funções. O risco nesses casos é aceitar código que funciona sem saber explicá-lo. Por isso, cada trecho gerado foi revisado e testado antes de entrar no projeto, e mantivemos as decisões de comportamento com a equipe (o desempate pela chuva, a subida de um nível por vez, a checagem só na mudança para PERIGO).
- **Manter o registro em dia.** Documentar cada interação no momento em que ela acontece exigiu disciplina, mas foi o que permitiu este arquivo refletir o uso real da IA e não uma reconstrução feita no final.

### Conclusão

A IA funcionou melhor como revisora, pesquisadora e testadora do que como autora. Os ganhos mais importantes vieram quando ela explicou um problema ou encontrou um erro, e não quando gerou código pronto. As decisões sobre o comportamento do Amparo, sobre o que priorizar para o cidadão e sobre o que ficava dentro do escopo da disciplina continuaram sendo da equipe.
