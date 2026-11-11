from datetime import datetime
from arquivos import ler_json
from risco import avaliar_risco, obter_recomendacoes, nivel_chuva, NIVEIS


ICONES = {"NORMAL": "🟢", "ATENÇÃO": "🟡", "PERIGO": "🔴"}
MARGEM_SETA = 0.1
LINHA = "─" * 40

LIMITE_EXIBICAO_SENSACAO = 54


def calcular_risco_atual(leituras: list[dict], previsao: dict) -> dict | None:
    """Avalia o risco a partir das duas últimas leituras e da previsão.

    Devolve o dicionário de avaliar_risco, ou None se não houver leitura.
    """

    if not leituras:
        nivel = nivel_chuva(previsao["mm_hora_max"], previsao["mm_dia"])
        if nivel == NIVEIS[0]:
            return None
        return {"nivel": nivel, "tipo": "chuva", "indice": None, "taxa": 0.0}

    atual = leituras[-1]

    if len(leituras) >= 2:
        anterior = leituras[-2]
        delta = (datetime.fromisoformat(atual["horario"])
                 - datetime.fromisoformat(anterior["horario"]))
        horas = delta.total_seconds() / 3600
    else:
        anterior = None
        horas = 0

    return avaliar_risco(atual, anterior, horas, previsao)


def escolher_seta(taxa: float) -> str:
    """Devolve ↑, ↓ ou → conforme a tendência da temperatura."""

    if taxa > MARGEM_SETA:
        return "↑"
    elif taxa < -MARGEM_SETA:
        return "↓"
    else:
        return "→"


def formatar_sensacao(indice: float) -> str:
    """Texto da sensação térmica, limitado a 'acima de 54 °C'."""

    if indice > LIMITE_EXIBICAO_SENSACAO:
        return f"acima de {LIMITE_EXIBICAO_SENSACAO} °C"
    return f"{indice} °C"


def exibir_painel(perfil: dict, leituras: list[dict], previsao: dict) -> dict | None:
    """Mostra o painel de risco acima do menu e devolve o risco calculado.
 
    O risco é devolvido para o main.py detectar a mudança para PERIGO.
    Sem leitura da casa, o painel ainda mostra o risco de chuva prevista.
    """
    risco = calcular_risco_atual(leituras, previsao)
 
    print(LINHA)
    print(f" AMPARO — {perfil['nome']} · {perfil['bairro']}")
 
    if risco is not None:
        nivel = risco["nivel"]
        linha_risco = f" RISCO: {ICONES[nivel]} {nivel}"
        if risco["tipo"] is not None:
            linha_risco += f" ({risco['tipo']})"
        print(linha_risco)
 
    if leituras and risco is not None:
        atual = leituras[-1]
        seta = escolher_seta(risco["taxa"])
        print(f" Dentro de casa: {atual['temperatura']} °C · {atual['umidade']}% · "
              f"sensação {formatar_sensacao(risco['indice'])} {seta}")
    else:
        print(" Sem leitura da casa — registre na opção 2.")
 
    if risco is not None:
        dicas = obter_recomendacoes(risco["tipo"], risco["nivel"], perfil["risco_chuva"])
        print(f" → {dicas[0]}")
 
    if leituras:
        horario = datetime.fromisoformat(leituras[-1]["horario"]).strftime("%H:%M")
        print(f" Última leitura: {horario}")
 
    print(LINHA)
    return risco