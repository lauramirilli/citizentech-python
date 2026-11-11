# Amparo — Aplicação Python

Alerta climático e rede de apoio para idosos e pessoas com deficiência em São Paulo.

Esta pasta contém a aplicação em Python do Amparo, entregue para a disciplina **Computational Thinking with Python** da Global Solution (GS2 — CitizenTech). Ela é o "cérebro" da solução: recebe as leituras de temperatura e umidade da casa e a previsão de chuva, decide o nível de risco, orienta a pessoa e aciona a rede de apoio quando necessário.

---

## Ficha da CitizenTech

| | |
|---|---|
| **Nome** | Amparo |
| **Cidade e bairros** | São Paulo — Sapopemba, Jardim Pantanal e Parque Brasilândia (bairros de exemplo) |
| **Cidadão beneficiado** | Idosos e pessoas com deficiência, principalmente quem mora sozinho ou tem a família longe |
| **Problema, em uma frase** | Durante ondas de calor e chuvas fortes, idosos e pessoas com deficiência muitas vezes não recebem o alerta a tempo e, quando passam mal, nem sempre conseguem pedir ajuda. |
| **Como funciona** | Um dispositivo dentro de casa mede temperatura e umidade; o sistema combina essas leituras com a previsão de chuva, classifica o risco em NORMAL, ATENÇÃO ou PERIGO, orienta a pessoa e, se ela não responder ou pedir ajuda, avisa a família e os voluntários do bairro. |
| **O que cada parte faz** | **Python:** decisão de risco, recomendações, checagem e rede de apoio (esta pasta). **Edge:** dispositivo ESP32 que mede e alerta com luz e som. **Front-end / Web:** aplicação web acessível. **Cálculo:** relatório que justifica a fórmula e os limites. **Software Design:** jornada e requisitos. **Storytelling:** pitch. |
| **Link do repositório** | <!-- inserir link --> |
| **Indicador de impacto** | Percentual de alertas confirmados pela pessoa, número de pedidos atendidos pela rede, tempo entre o pedido de ajuda e a chegada de alguém e pessoas encaminhadas a abrigos durante eventos extremos. |
| **ODS conectados** | 3 (Saúde e bem-estar), 10 (Redução das desigualdades), 11 (Cidades e comunidades sustentáveis) e 13 (Ação contra a mudança global do clima) |

---

## Como executar

**Requisitos**
- Python **3.10 ou mais recente** (o programa usa `match/case`)
- Biblioteca `requests`, usada para buscar a previsão de chuva

**Como rodar**
1. Abra a pasta `python/` como projeto.
2. Instale o `requests`: no terminal, rode o comando de instalação abaixo para o seu sistema.
3. Abra o `main.py` e clique em **Run**.

**Pelo terminal**

| Sistema | Instalar o `requests` | Executar |
|---|---|---|
| Windows | `py -m pip install requests` | `py main.py` |
| macOS / Linux | `python3 -m pip install requests` | `python3 main.py` |

No Windows, se o comando `py` não existir, use `python` no lugar (`python -m pip install requests` e `python main.py`). Os comandos devem ser rodados dentro da pasta `python/`.

O programa pode ser executado a partir de qualquer pasta: os arquivos de dados são localizados a partir da pasta do próprio código.

Na primeira execução, o Amparo pede para configurar o perfil da pessoa atendida. Depois disso, o painel de risco aparece sempre acima do menu.

---

## Funcionalidades

Ao abrir o programa, o **painel de risco** mostra o nível atual (com cor, ícone e texto), as condições dentro de casa, a tendência da temperatura e a recomendação mais importante do momento.

| Opção | O que faz |
|---|---|
| 1. Ver recomendações completas | Lista todas as orientações para o risco atual |
| 2. Registrar leitura | Registra temperatura e umidade da casa, digitadas ou simuladas |
| 3. Atualizar previsão | Busca a previsão real de chuva (internet) ou simula uma previsão |
| 4. Pedir ajuda | Aciona a rede de apoio, com confirmação para evitar pedidos acidentais |
| 5. Abrigos próximos | Mostra abrigos do bairro para calor ou chuva, com informações de acessibilidade |
| 6. Rede de apoio | Ver, adicionar e remover familiares e voluntários |
| 7. Meu perfil | Ver e editar os dados da pessoa atendida |
| 8. Histórico de alertas | Lista os alertas e mostra quantos foram confirmados pela pessoa |
| 0. Sair | Encerra o programa e mostra os telefones de emergência |

**Checagem automática.** Quando o risco **passa** para PERIGO, o programa pergunta se a pessoa está bem. Se ela responder que não, ou não responder, a rede de apoio é acionada na ordem: família e cuidadores → voluntários do mesmo bairro → telefones de emergência (SAMU 192, Bombeiros 193, Defesa Civil 199).

---

## Como o risco é decidido

### Calor dentro de casa
O sistema calcula o **índice de calor** (sensação térmica) a partir da temperatura e da umidade, pelo critério da NOAA (fórmula simples de Steadman em condições amenas e regressão de Rothfusz em condições quentes).

| Índice de calor | Nível |
|---|---|
| menor que 32 °C | NORMAL |
| de 32 °C a menos de 39 °C | ATENÇÃO |
| 39 °C ou mais | PERIGO |

**Antecipação.** Com duas leituras, o sistema calcula a velocidade com que a temperatura está subindo e projeta a temperatura daqui a 1 hora (aproximação linear). Se a projeção cair num nível mais grave, o alerta sobe **um degrau** antes do previsto. Subir só um degrau evita que uma estimativa leve o sistema direto de NORMAL para PERIGO.

### Chuva prevista
Segue a escala de avisos do INMET:

| Chuva prevista | Nível |
|---|---|
| menos de 20 mm/h e menos de 50 mm/dia | NORMAL |
| 20 mm/h ou mais, **ou** 50 mm/dia ou mais | ATENÇÃO |
| 30 mm/h ou mais, **ou** 100 mm/dia ou mais | PERIGO |

### Nível final
É o mais grave entre calor e chuva. Em caso de empate, prevalece a chuva, porque ela exige ação **antes** do evento (sair de casa, proteger documentos). As recomendações de chuva dependem de onde fica a casa: **alagamento** (perto de rio ou rua que alaga) ou **deslizamento** (morro ou encosta).

A justificativa matemática desses limites, da fórmula e da projeção está no relatório da disciplina de Cálculo.

---

## Simulações usadas no protótipo

Para que o protótipo possa ser demonstrado sem o dispositivo físico e sem depender do clima do dia:

- **Leituras do sensor.** A opção 2 permite digitar ou simular uma leitura. A simulação varia pouco em relação à leitura anterior, como uma casa real.
- **Relógio do sensor.** O dispositivo lê a cada 10 minutos. Por isso, cada nova leitura recebe pelo menos o horário da anterior mais 10 minutos, mesmo quando é registrada segundos depois na demonstração. Assim a velocidade de aquecimento faz sentido.
- **Previsão simulada.** A opção 3 permite informar a chuva prevista, para demonstrar os alertas de chuva em qualquer dia.
- **Pessoa que não consegue responder.** Na checagem, apertar Enter sem digitar nada representa a pessoa que não responde. No dispositivo real, isso seria um tempo limite sem resposta.
- **Envio dos avisos.** O programa mostra a quem o aviso seria enviado, mas não envia mensagens de verdade. A resposta da família também é simulada com uma pergunta.

---

## Dados

Todos os dados são **fictícios** ou de fonte pública. Nenhuma informação pessoal real é usada.

`abrigos.json` e `rede.json` vêm com dados de exemplo; os demais arquivos são criados automaticamente durante o uso.

| Arquivo (`dados/`) | Conteúdo |
|---|---|
| `perfil.json` | Pessoa atendida |
| `leituras.json` | Leituras de temperatura e umidade |
| `previsao.json` | Última previsão de chuva (real ou simulada); usada também quando não há internet |
| `rede.json` | Familiares e voluntários |
| `abrigos.json` | Abrigos e pontos de acolhimento fictícios, com acessibilidade |
| `alertas.json` | Histórico de alertas |

A previsão real vem da API pública **Open-Meteo**, que não exige cadastro. Sem internet, o programa avisa e usa a última previsão salva.

---

## Estrutura do código

```
python/
├── main.py         # loop principal: painel → menu → ação
├── painel.py       # monta o painel de risco
├── risco.py        # índice de calor, taxa, projeção, níveis e recomendações
├── previsao.py     # previsão real (Open-Meteo), simulada e salva
├── ajuda.py        # checagem, pedido de ajuda, rede de apoio e histórico
├── cadastros.py    # leituras, abrigos, rede de apoio e perfil
├── entradas.py     # leitura de dados do usuário com validação
├── arquivos.py     # leitura e gravação dos arquivos JSON
├── validacao.py    # verificação dos registros lidos dos arquivos
├── dados/          # arquivos JSON
├── README.md
└── prompts.md      # registro do uso de inteligência artificial
```

### Conceitos da disciplina aplicados

| Conceito | Onde aparece |
|---|---|
| Menu de opções | `main.py` e submenus da previsão, rede e perfil |
| `if/elif/else` | classificação de risco (`risco.py`), checagem (`ajuda.py`) |
| `match/case` | menu principal, submenus e tradução de opções (tipo de abrigo, tipo de pessoa, local da casa) |
| `while` e `for` | loop do menu, repetição até entrada válida, percorrer leituras, abrigos, rede e alertas |
| Funções com parâmetros e retorno | todos os módulos (ex.: `avaliar_risco`, `filtrar_abrigos`, `buscar_previsao_real`) |
| Listas, tuplas e dicionários | registros em dicionários, coleções em listas, constantes em tuplas (níveis, telefones, acessibilidade, coordenadas) e recomendações num dicionário com tupla como chave |
| Validação de entradas | `entradas.py`: números em faixa, vírgula decimal, campos vazios, opções válidas |
| `try/except` | arquivos ausentes ou corrompidos, falha ao salvar, falta de internet, resposta inesperada da API, Ctrl+C |
| Arquivos JSON | leitura e gravação de todos os dados em `dados/` |

---

## Limitações conhecidas

- O protótipo atende uma pessoa por execução, como o dispositivo instalado numa casa.
- As leituras e o envio de avisos são simulados (ver seção acima).
- Os ajustes finos da NOAA para umidade abaixo de 13% ou acima de 85% não foram incluídos. Em valores extremos, a sensação térmica é exibida como "acima de 54 °C".
- Os abrigos, endereços e pessoas da rede são fictícios.

---

## Uso de inteligência artificial

O uso de ferramentas de IA no desenvolvimento está documentado em [`prompts.md`](prompts.md).

---

## Equipe

| Nome | RM |
|------|----|
| Bruce Li | 569168 |
| Felipe Rorato | 570419 |
| Giovanna Andrade Parejas | 569041 |
| Laura Cardin Mirilli | 570841 |