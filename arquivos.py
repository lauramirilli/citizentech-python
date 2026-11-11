import json
import os
from collections.abc import Callable
from typing import Any

PASTA_BASE = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(PASTA_BASE, "dados")

def ler_json(nome_arquivo: str, padrao: Any) -> Any:
    """Lê um arquivo JSON e devolve seu conteúdo.

    Se o arquivo não existir (ex.: primeira execução), devolve `padrao`
    sem aviso. Se estiver corrompido, avisa o usuário e devolve `padrao`.
    """

    caminho = os.path.join(PASTA_DADOS, nome_arquivo)

    try:
        with open(caminho, "r",  encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
            return dados
    except FileNotFoundError:
        return padrao
    except json.JSONDecodeError:
        print(f"Aviso: {nome_arquivo} está corrompido. Usando valores padrão.")
        return padrao

def ler_lista(nome_arquivo: str, valido: Callable[[Any], bool]) -> list:
    """Lê uma lista de registros de um JSON, ignorando os inválidos.

    `valido` é uma função que recebe um registro e devolve True/False.
    Se o conteúdo não for uma lista, avisa e devolve []. Registros
    inválidos (ex.: arquivo editado à mão) são descartados com aviso.
    """

    dados = ler_json(nome_arquivo, [])

    if not isinstance(dados, list):
        print(f"Aviso: {nome_arquivo} não está no formato esperado. Usando lista vazia.")
        return []

    validos = []
    for registro in dados:
        if valido(registro):
            validos.append(registro)

    descartados = len(dados) - len(validos)
    if descartados > 0:
        print(f"Aviso: {descartados} registro(s) inválido(s) em {nome_arquivo} foram ignorados.")

    return validos

def salvar_json(nome_arquivo: str, dados: Any) -> bool:
    """Grava `dados` em um arquivo JSON (UTF-8, acentos preservados).

    Devolve True se salvou e False se houve erro (pasta inexistente,
    falta de permissão ou dados que não podem virar JSON), avisando o
    usuário. Se os dados forem inválidos, o arquivo antigo não é alterado.
    """

    caminho = os.path.join(PASTA_DADOS, nome_arquivo)

    try:
        texto = json.dumps(dados, ensure_ascii=False, indent=2)
    except TypeError:
        print(f"Aviso: dados inválidos para {nome_arquivo}.")
        return False

    try:
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(texto)
        return True
    except OSError:
        print(f"Aviso: não foi possível salvar {nome_arquivo}.")
        return False