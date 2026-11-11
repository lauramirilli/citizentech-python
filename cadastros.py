import random
from datetime import datetime, timedelta
from arquivos import ler_lista, salvar_json
from entradas import ler_numero, ler_opcao, ler_texto, ler_sim_nao
from ajuda import titulo
from previsao import BAIRROS
from validacao import leitura_valida, abrigo_valido, pessoa_valida


TEMP_MIN, TEMP_MAX = 0, 50
UMID_MIN, UMID_MAX = 0, 100

INTERVALO_LEITURA = timedelta(minutes=10)

ACESSIBILIDADE = ("rampa", "banheiro_adaptado", "espaco_cadeira_rodas")

NOMES_ACESSIBILIDADE = {
    "rampa": "Rampa de acesso",
    "banheiro_adaptado": "Banheiro adaptado",
    "espaco_cadeira_rodas": "Espaço para cadeira de rodas",
}

REQUISITOS_MOBILIDADE = ("rampa", "espaco_cadeira_rodas")


def registrar_leitura() -> dict:
    """Registra uma leitura de temperatura e umidade, manual ou simulada.

    O horário simula o relógio do sensor: cada leitura recebe o horário
    atual, mas nunca menos que o da anterior + 10 minutos. Assim a taxa
    de variação faz sentido quando as leituras são registradas com
    segundos de diferença na demonstração, e uma leitura feita horas
    depois usa o horário real (sem inflar a taxa e gerar falso alarme).
    Salva em leituras.json e devolve a leitura registrada.
    """

    leituras = ler_lista("leituras.json", leitura_valida)
    agora = datetime.now().replace(second=0, microsecond=0)

    if not leituras:
        ultima = None
        horario = agora
    else:
        ultima = leituras[-1]
        minimo = datetime.fromisoformat(ultima["horario"]) + INTERVALO_LEITURA
        horario = max(agora, minimo)

    print("\n1. Digitar a leitura")
    print("2. Simular a leitura do sensor")
    opcao = ler_opcao("Escolha: ", ("1", "2"))

    match opcao:
        case "1":
            temperatura = ler_numero(f"Temperatura (°C, {TEMP_MIN} a {TEMP_MAX}): ",
                                     TEMP_MIN, TEMP_MAX)
            umidade = ler_numero(f"Umidade (%, {UMID_MIN} a {UMID_MAX}): ",
                                 UMID_MIN, UMID_MAX)
        case "2":
            if ultima is None:
                temperatura = random.uniform(26, 30)
                umidade = random.uniform(50, 70)
            else:
                temperatura = ultima["temperatura"] + random.uniform(-0.3, 0.8)
                umidade = ultima["umidade"] + random.uniform(-2, 2)
            temperatura = max(TEMP_MIN, min(TEMP_MAX, temperatura))
            umidade = max(UMID_MIN, min(UMID_MAX, umidade))

    leitura = {
        "temperatura": round(temperatura, 1),
        "umidade": round(umidade, 1),
        "horario": horario.isoformat(timespec="minutes"),
    }

    leituras.append(leitura)
    if salvar_json("leituras.json", leituras):
        print(f"Leitura registrada: {leitura['temperatura']} °C, "
              f"{leitura['umidade']}% às {horario.strftime('%H:%M')}.")
    return leitura

def filtrar_abrigos(abrigos: list[dict], bairro: str, tipo: str, requisitos: tuple[str, ...]) -> list[dict]:
    """Devolve os abrigos do bairro que atendem ao tipo e a todos os requisitos."""
    encontrados = []

    for abrigo in abrigos:
        atende = True
        for requisito in requisitos:
            if requisito not in abrigo["acessibilidade"]:
                atende = False

        if abrigo["bairro"] == bairro and tipo in abrigo["tipos"] and atende:
            encontrados.append(abrigo)

    return encontrados

def mostrar_abrigos(perfil: dict, risco: dict | None) -> None:
    """Mostra os abrigos do bairro, filtrando por tipo e por acessibilidade."""
    titulo("🏠 ABRIGOS PRÓXIMOS")

    if risco is not None and risco["tipo"] is not None:
        print(f" Risco atual: {risco['tipo']}\n")

    print(" 1. Calor")
    print(" 2. Chuva\n")
    opcao = ler_opcao(" Selecione o tipo de abrigo: ", ("1", "2"))

    match opcao:
        case "1":
            tipo = "calor"
        case "2":
            tipo = "chuva"

    if perfil["mobilidade_reduzida"]:
        requisitos: tuple[str, ...] = REQUISITOS_MOBILIDADE
        print("Mostrando apenas abrigos com rampa e espaço para cadeira de rodas.")
    else:
        requisitos = ()

    abrigos = ler_lista("abrigos.json", abrigo_valido)
    encontrados = filtrar_abrigos(abrigos, perfil["bairro"], tipo, requisitos)

    if not encontrados:
        print("Nenhum abrigo encontrado no seu bairro com esses critérios.")
        print("Em caso de emergência, ligue para a Defesa Civil (199)")
        return

    for abrigo in encontrados:
        print(f"\n   🏠 {abrigo['nome']}")
        print(f"      {abrigo['endereco']} · {abrigo['horario']}")

        itens = []
        for item in ACESSIBILIDADE:
            if item in abrigo["acessibilidade"]:
                itens.append(f"✔ {NOMES_ACESSIBILIDADE[item]}")
            else:
                itens.append(f"✘ {NOMES_ACESSIBILIDADE[item]}")
        print(f"      {'  '.join(itens)}")

def ver_rede() -> list[dict]:
    """Mostra a rede de apoio numerada e devolve a lista de pessoas."""
    pessoas = ler_lista("rede.json", pessoa_valida)

    if not pessoas:
        print("\n   Sua rede de apoio ainda está vazia. Adicione pessoas na opção 2.")
        return pessoas

    print()
    for numero, pessoa in enumerate(pessoas, start=1):
        linha = f"   {numero}. {pessoa['nome']} · {pessoa['tipo']}"
        if pessoa["tipo"] == "voluntario":
            linha += f" · {pessoa['bairro']}"
        linha += f" · {pessoa['telefone']}"
        print(linha)

    return pessoas

def escolher_bairro(mensagem: str) -> str:
    """Mostra os bairros atendidos numerados e devolve o nome do escolhido."""
    nomes = []
    opcoes = []
    for numero, nome in enumerate(BAIRROS, start=1):
        print(f"   {numero}. {nome}")
        nomes.append(nome)
        opcoes.append(str(numero))

    escolha = ler_opcao(mensagem, opcoes)
    return nomes[int(escolha) - 1]

def configurar_perfil() -> dict:
    """Pergunta os dados da pessoa atendida, salva em perfil.json e devolve o perfil."""
    print()
    nome = ler_texto(" Nome da pessoa atendida: ")

    print("\n Em qual bairro fica a casa?")
    bairro = escolher_bairro(" Bairro: ")

    print("\n Onde fica a casa?")
    print("   1. Perto de rio ou córrego, ou em rua que costuma alagar")
    print("   2. Em morro ou encosta")
    opcao = ler_opcao(" Escolha: ", ("1", "2"))
    match opcao:
        case "1":
            risco_chuva = "alagamento"
        case "2":
            risco_chuva = "deslizamento"

    print()
    mora_sozinho = ler_sim_nao(" Mora sozinho(a)? (s/n) ")
    mobilidade_reduzida = ler_sim_nao(" Usa cadeira de rodas ou tem dificuldade para andar? (s/n) ")

    perfil = {
        "nome": nome,
        "bairro": bairro,
        "risco_chuva": risco_chuva,
        "mora_sozinho": mora_sozinho,
        "mobilidade_reduzida": mobilidade_reduzida,
    }
    if salvar_json("perfil.json", perfil):
        print(f"\n   ✅ Perfil de {nome} salvo.")
    return perfil


def sim_ou_nao(valor: bool) -> str:
    """Converte True/False em "sim"/"não" para exibir na tela."""
    if valor:
        return "sim"
    return "não"


def ver_perfil(perfil: dict) -> None:
    """Mostra os dados do perfil em linguagem simples."""
    if perfil["risco_chuva"] == "alagamento":
        local = "perto de rio ou rua que alaga"
    else:
        local = "em morro ou encosta"

    print()
    print(f"   Nome: {perfil['nome']}")
    print(f"   Bairro: {perfil['bairro']}")
    print(f"   Casa: {local}")
    print(f"   Mora sozinho(a): {sim_ou_nao(perfil['mora_sozinho'])}")
    print(f"   Mobilidade reduzida: {sim_ou_nao(perfil['mobilidade_reduzida'])}")


def menu_perfil(perfil: dict) -> dict:
    """Submenu do perfil. Devolve o perfil, atualizado se foi editado."""
    print()
    print("─" * 40)
    print(" 👤 MEU PERFIL")
    print("─" * 40)
    ver_perfil(perfil)

    print("\n   1. Editar perfil")
    print("   0. Voltar")
    opcao = ler_opcao("\n Escolha: ", ("1", "0"))

    if opcao == "1":
        return configurar_perfil()
    return perfil


def adicionar_pessoa() -> None:
    """Cadastra um familiar ou voluntário na rede de apoio (rede.json)."""
    print()
    nome = ler_texto(" Nome: ")
    telefone = ler_texto(" Telefone: ")

    print("\n   1. Familiar ou cuidador")
    print("   2. Voluntário do bairro")
    opcao = ler_opcao(" Tipo: ", ("1", "2"))

    match opcao:
        case "1":
            tipo = "familiar"
            bairro = None
        case "2":
            tipo = "voluntario"
            print()
            bairro = escolher_bairro(" Bairro do voluntário: ")

    pessoa = {"nome": nome, "tipo": tipo, "telefone": telefone, "bairro": bairro}

    rede = ler_lista("rede.json", pessoa_valida)
    rede.append(pessoa)
    if salvar_json("rede.json", rede):
        print(f"\n   ✅ {nome} agora faz parte da sua rede.")

def remover_pessoa() -> None:
    """Remove uma pessoa da rede de apoio, com confirmação."""

    pessoas = ver_rede()
    if not pessoas:
        return

    opcoes = []
    for numero in range(1, len(pessoas) + 1):
        opcoes.append(str(numero))
    numero = int(ler_opcao(f"\n Número da pessoa a remover (1 a {len(pessoas)}): ", opcoes))
    pessoa = pessoas[numero - 1]

    if not ler_sim_nao(f" Remover {pessoa['nome']} da rede? (s/n) "):
        print("\n   Nada foi removido.")
        return

    pessoas.pop(numero - 1)
    if salvar_json("rede.json", pessoas):
        print(f"\n   ✅ {pessoa['nome']} foi removido(a) da sua rede.")

def gerenciar_rede(perfil: dict) -> None:
    """Submenu da rede de apoio: ver, adicionar e remover pessoas."""
    while True:
        titulo("👥 REDE DE APOIO")
        print("   1. Ver minha rede")
        print("   2. Adicionar pessoa")
        print("   3. Remover pessoa")
        print("   0. Voltar")
        opcao = ler_opcao("\n Escolha: ", ("1", "2", "3", "0"))

        match opcao:
            case "1":
                ver_rede()
            case "2":
                adicionar_pessoa()
            case "3":
                remover_pessoa()
            case "0":
                return