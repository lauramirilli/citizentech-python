def ler_numero(mensagem: str, minimo: float, maximo: float) -> float:
    """Pede um número entre `minimo` e `maximo` até receber um válido.

    Aceita vírgula ou ponto como separador decimal.
    """

    while True:
        try:
            numero = float(input(mensagem).replace(",", "."))
            if minimo <= numero <= maximo:
                return numero
            print(f"Digite um número entre {minimo} e {maximo}.")
        except ValueError:
            print(f"Digite apenas números entre {minimo} e {maximo}.")

def ler_texto(mensagem: str) -> str:
    """Pede um texto não vazio e devolve sem espaços nas pontas."""

    while True:
        texto = input(mensagem)
        if not texto.strip():
            print("O campo não pode estar vazio.")
        else:
            return texto.strip()

def ler_opcao(mensagem: str, opcoes: tuple[str, ...] | list[str]) -> str:
    """Pede uma resposta até que ela esteja na tupla `opcoes`."""

    while True:
        numero_opcao = input(mensagem).strip()
        if numero_opcao in opcoes:
            return numero_opcao
        else:
            print(f"Escolha uma das opções: {', '.join(opcoes)}.")

def ler_sim_nao(mensagem: str) -> bool:
    """Pede 's' ou 'n' e devolve True ou False."""
    
    while True:
        resposta = input(mensagem).strip().lower()
        if resposta == "s":
            return True
        elif resposta == "n":
            return False
        else:
            print("Digite 's' ou 'n'.")