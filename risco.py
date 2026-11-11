NIVEIS = ("NORMAL", "ATENÇÃO", "PERIGO")

LIMITE_CALOR_ATENCAO = 32
LIMITE_CALOR_PERIGO = 39

LIMITE_CHUVA_HORA_ATENCAO = 20
LIMITE_CHUVA_HORA_PERIGO = 30
LIMITE_CHUVA_DIA_ATENCAO = 50
LIMITE_CHUVA_DIA_PERIGO = 100

RECOMENDACOES = {
    ("calor", "ATENÇÃO"): [
        "Beba um copo de água agora.",
        "Use roupas leves e claras.",
        "Fique no cômodo mais fresco da casa.",
        "Feche as cortinas onde bate sol.",
    ],
    ("calor", "PERIGO"): [
        "Beba água agora, mesmo sem sede.",
        "Tome um banho fresco ou molhe pulsos e nuca.",
        "Não saia de casa entre 11h e 16h.",
        "Se sentir tontura, confusão ou falta de ar, ligue 192 (SAMU).",
    ],
    ("alagamento", "ATENÇÃO"): [
        "Coloque documentos e remédios em local alto.",
        "Deixe celular e lanterna carregados.",
        "Evite sair de casa se não for necessário.",
    ],
    ("alagamento", "PERIGO"): [
        "Não atravesse ruas alagadas, nem a pé nem de carro.",
        "Se a água entrar em casa, vá para o ponto mais alto.",
        "Não mexa em tomadas ou aparelhos com as mãos ou os pés molhados.",
        "Evite contato com a água da enchente.",
        "Em emergência, ligue 193 (Bombeiros) ou 199 (Defesa Civil).",
    ],
    ("deslizamento", "ATENÇÃO"): [
        "Observe rachaduras novas em paredes ou no chão.",
        "Fique atento a portas e janelas que começam a emperrar.",
        "Deixe documentos e remédios prontos para sair.",
    ],
    ("deslizamento", "PERIGO"): [
        "Se ouvir estalos ou ver a terra se mexer, saia de casa agora.",
        "Vá para um local seguro, longe da encosta.",
        "Não volte para buscar objetos.",
        "Ligue 199 (Defesa Civil).",
    ],
}

MENSAGEM_NORMAL = "Tudo certo por aqui. Lembre de beber água ao longo do dia."

def calcular_indice_calor(temp_c: float, umidade: float) -> float:
    """Calcula o índice de calor (sensação térmica) em graus Celsius.

    Segue o critério da NOAA, que trabalha em fahrenheit:
    1. Calcula a fórmula simples de Steadman.
    2. Se a média entre esse valor e a temperatura for menor que 80 °F,
       o índice é o valor da fórmula simples.
    3. Senão, usa a regressão de Rothfusz.
    Os ajustes finos da NOAA (umidade < 13% ou > 85%) ficam de fora.

    O valor é arredondado só na exibição.
    """

    temp_f = (temp_c * 1.8) + 32

    simples = 0.5 * (temp_f + 61 + (temp_f - 68) * 1.2 + umidade * 0.094)

    if (temp_f + simples) / 2 < 80:
        indice_calor_f = simples
    else:
        indice_calor_f = (
            -42.379
            + 2.04901523 * temp_f
            + 10.14333127 * umidade
            - 0.22475541 * temp_f * umidade
            - 0.00683783 * temp_f ** 2
            - 0.05481717 * umidade ** 2
            + 0.00122874 * temp_f ** 2 * umidade
            + 0.00085282 * temp_f * umidade ** 2
            - 0.00000199 * temp_f ** 2 * umidade ** 2
        )
    
    indice_calor_c = (indice_calor_f - 32) / 1.8

    return indice_calor_c


def nivel_calor(indice: float) -> str:
    """Classifica o índice de calor (graus Celsius) em um dos NIVEIS, pelas faixas da NOAA."""

    if indice < LIMITE_CALOR_ATENCAO:
        return NIVEIS[0]
    elif indice < LIMITE_CALOR_PERIGO:
        return NIVEIS[1]
    else:
        return NIVEIS[2]


def nivel_chuva(mm_hora: float, mm_dia: float) -> str:
    """Classifica a chuva prevista em um dos NIVEIS, pela escala do INMET.

    Basta um dos critérios (por hora ou por dia) para subir o nível.
    """

    if mm_hora >= LIMITE_CHUVA_HORA_PERIGO or mm_dia >= LIMITE_CHUVA_DIA_PERIGO:
        return NIVEIS[2]
    elif mm_hora >= LIMITE_CHUVA_HORA_ATENCAO or mm_dia >= LIMITE_CHUVA_DIA_ATENCAO:
        return NIVEIS[1]
    else:
        return NIVEIS[0]


def calcular_taxa(indice_atual: float, indice_anterior: float, horas: float) -> float:
    """Taxa de variação da temperatura em graus Celsius/h (derivada discreta).

    Se o intervalo for zero ou negativo, não há como medir tendência,
    então devolve 0.0, o que faz a projeção ficar igual ao valor atual.
    """
    
    if horas <= 0:
        return 0.0
    taxa = (indice_atual - indice_anterior) / horas
    return taxa

def projetar_valor(valor_atual: float, taxa: float, horas: float = 1) -> float:
    """Estima um valor daqui a x horas (aproximação linear)."""

    indice_projetado = valor_atual + taxa * horas
    return indice_projetado

    
def avaliar_risco(leitura_atual: dict, leitura_anterior: dict | None, horas: float, previsao: dict) -> dict:
    """Avalia o risco combinando o calor dentro de casa e a chuva prevista.

    Recebe a leitura atual e a anterior ({"temperatura", "umidade"}), o
    intervalo entre elas em horas e a previsão ({"mm_hora_max", "mm_dia"}).
    Sem leitura anterior (None), a taxa é 0.0 e não há antecipação.

    A taxa é medida na temperatura, não no índice. O índice de calor tem
    um pequeno salto na troca entre a fórmula simples e a de Rothfusz
    (até ~1,3 °C), que inflaria a taxa e geraria falso alarme. A projeção
    estima a temperatura daqui a 1 hora e aplica o índice sobre ela.

    O nível de calor sobe um degrau se a projeção for mais grave que o
    nível atual. O nível final é o mais grave entre calor e chuva; em
    empate, vence a chuva (exige ação antes do evento). Em NORMAL, o tipo
    é None.

    Devolve um dicionário com: nivel, tipo, indice, taxa,
    indice_projetado, nivel_calor e nivel_chuva (valores arredondados).
    """

    temp_atual = leitura_atual["temperatura"]
    umid_atual = leitura_atual["umidade"]
    indice_atual = calcular_indice_calor(temp_atual, umid_atual)

    if leitura_anterior is None:
        taxa = 0.0
    else:
        temp_anterior = leitura_anterior["temperatura"]
        taxa = calcular_taxa(temp_atual, temp_anterior, horas)

    nivel_calor_atual = nivel_calor(indice_atual)

    temp_projetada = projetar_valor(temp_atual, taxa)
    indice_calor_futuro = calcular_indice_calor(temp_projetada, umid_atual)
    nivel_calor_futuro = nivel_calor(indice_calor_futuro)

    posicao_atual = NIVEIS.index(nivel_calor_atual)
    posicao_futura = NIVEIS.index(nivel_calor_futuro)

    if posicao_futura > posicao_atual:
        nivel_calor_final = NIVEIS[posicao_atual + 1]
    else:
        nivel_calor_final = nivel_calor_atual

    nivel_chuva_final = nivel_chuva(previsao["mm_hora_max"], previsao["mm_dia"])

    if NIVEIS.index(nivel_chuva_final) >= NIVEIS.index(nivel_calor_final):
        nivel_final = nivel_chuva_final
        tipo: str | None = "chuva"
    else:
        nivel_final = nivel_calor_final
        tipo = "calor"

    if nivel_final == NIVEIS[0]:
        tipo = None

    return {
        "nivel": nivel_final,
        "tipo": tipo,
        "indice": round(indice_atual, 2),
        "taxa": round(taxa, 2),
        "indice_projetado": round(indice_calor_futuro, 2),
        "nivel_calor": nivel_calor_final,
        "nivel_chuva": nivel_chuva_final,
    }

def obter_recomendacoes(tipo: str | None, nivel: str, risco_chuva: str) -> list[str]:
    """Devolve a lista de recomendações para o tipo e o nível de risco.

    Sem risco (tipo None), devolve só a mensagem de NORMAL. Para chuva,
    usa o risco da casa da pessoa (alagamento ou deslizamento), vindo
    do perfil, para escolher as recomendações.
    """

    if tipo is None:
        return [MENSAGEM_NORMAL]

    if tipo == "chuva":
        tipo = risco_chuva

    return RECOMENDACOES[(tipo, nivel)]