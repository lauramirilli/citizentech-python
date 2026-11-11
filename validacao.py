from datetime import datetime
from typing import Any

RISCOS_CHUVA = ("alagamento", "deslizamento")
TIPOS_PESSOA = ("familiar", "voluntario")


def eh_numero(valor: Any) -> bool:
    """True se `valor` for int ou float (bool não conta como número)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def eh_texto(valor: Any) -> bool:
    """True se `valor` for um texto não vazio."""
    return isinstance(valor, str) and valor.strip() != ""


def eh_horario(valor: Any) -> bool:
    """True se `valor` for um horário no formato ISO (ex.: 2026-11-11T10:00)."""
    if not isinstance(valor, str):
        return False
    try:
        datetime.fromisoformat(valor)
        return True
    except ValueError:
        return False


def tem_chaves(registro: Any, chaves: tuple[str, ...]) -> bool:
    """True se `registro` for um dicionário com todas as `chaves`."""
    if not isinstance(registro, dict):
        return False
    for chave in chaves:
        if chave not in registro:
            return False
    return True


def perfil_valido(perfil: Any) -> bool:
    return (tem_chaves(perfil, ("nome", "bairro", "risco_chuva", "mora_sozinho", "mobilidade_reduzida"))
            and eh_texto(perfil["nome"])
            and eh_texto(perfil["bairro"])
            and perfil["risco_chuva"] in RISCOS_CHUVA
            and isinstance(perfil["mora_sozinho"], bool)
            and isinstance(perfil["mobilidade_reduzida"], bool))


def leitura_valida(leitura: Any) -> bool:
    return (tem_chaves(leitura, ("temperatura", "umidade", "horario"))
            and eh_numero(leitura["temperatura"])
            and eh_numero(leitura["umidade"])
            and eh_horario(leitura["horario"]))


def previsao_valida(previsao: Any) -> bool:
    return (tem_chaves(previsao, ("mm_hora_max", "mm_dia"))
            and eh_numero(previsao["mm_hora_max"])
            and eh_numero(previsao["mm_dia"]))


def pessoa_valida(pessoa: Any) -> bool:
    if not (tem_chaves(pessoa, ("nome", "tipo", "telefone"))
            and eh_texto(pessoa["nome"])
            and eh_texto(pessoa["telefone"])
            and pessoa["tipo"] in TIPOS_PESSOA):
        return False
    return pessoa["tipo"] == "familiar" or eh_texto(pessoa.get("bairro"))


def abrigo_valido(abrigo: Any) -> bool:
    return (tem_chaves(abrigo, ("nome", "bairro", "tipos", "endereco", "acessibilidade", "horario"))
            and isinstance(abrigo["tipos"], list)
            and isinstance(abrigo["acessibilidade"], list))


def alerta_valido(alerta: Any) -> bool:
    return (tem_chaves(alerta, ("horario", "nivel", "tipo", "motivo", "resultado"))
            and eh_horario(alerta["horario"]))
