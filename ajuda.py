from datetime import datetime

from arquivos import ler_lista, salvar_json
from entradas import ler_sim_nao
from validacao import pessoa_valida, alerta_valido

TELEFONES_EMERGENCIA = (("SAMU", "192"), ("Bombeiros", "193"), ("Defesa Civil", "199"))

LINHA = "─" * 40
LINHA_ALERTA = "!" * 40


def titulo(texto: str) -> None:
    """Imprime um título de seção entre linhas, para separar as etapas."""
    print()
    print(LINHA)
    print(f" {texto}")
    print(LINHA)


def mostrar_emergencia() -> None:
    """Mostra os telefones de emergência, alinhados em colunas."""
    titulo("📞 TELEFONES DE EMERGÊNCIA")
    for nome, numero in TELEFONES_EMERGENCIA:
        print(f"   {nome:<14} {numero}")


def registrar_alerta(risco: dict | None, motivo: str, resultado: str) -> None:
    """Acrescenta um alerta ao alertas.json (alimenta o histórico, opção 8).

    `risco` pode ser None, por exemplo num pedido manual sem leitura da casa.
    """
    if risco is None:
        nivel = "—"
        tipo = None
    else:
        nivel = risco["nivel"]
        tipo = risco["tipo"]

    alerta = {
        "horario": datetime.now().isoformat(timespec="minutes"),
        "nivel": nivel,
        "tipo": tipo,
        "motivo": motivo,
        "resultado": resultado,
    }

    alertas = ler_lista("alertas.json", alerta_valido)
    alertas.append(alerta)
    salvar_json("alertas.json", alertas)


def avisar_pessoas(pessoas: list[dict]) -> None:
    """Mostra o aviso de envio para cada pessoa da lista."""
    for pessoa in pessoas:
        print(f"   📨 Avisando {pessoa['nome']} ({pessoa['telefone']})...")


def acionar_rede(perfil: dict) -> None:
    """Aciona a rede de apoio em ordem: família → voluntários do bairro.

    No fim, sempre mostra os telefones de emergência.
    """
    titulo("🆘 PEDIDO DE AJUDA")

    if not perfil["mora_sozinho"]:
        print("   👥 Peça ajuda a quem está em casa com você.")

    pessoas = ler_lista("rede.json", pessoa_valida)

    familiares = []
    voluntarios = []
    for pessoa in pessoas:
        if pessoa["tipo"] == "familiar":
            familiares.append(pessoa)
        elif pessoa["tipo"] == "voluntario" and pessoa["bairro"] == perfil["bairro"]:
            voluntarios.append(pessoa)

    print("\n 1º Família e cuidadores")
    if familiares:
        avisar_pessoas(familiares)
        print()
        respondeu = ler_sim_nao(" (simulação) Algum familiar respondeu? (s/n) ")
    else:
        print("   Nenhum familiar cadastrado.")
        respondeu = False

    if respondeu:
        print("\n   ✅ Um familiar está a caminho.")
    else:
        print(f"\n 2º Voluntários em {perfil['bairro']}")
        if voluntarios:
            avisar_pessoas(voluntarios)
            print("\n   ✅ Pedido enviado aos voluntários do bairro.")
        else:
            print("   ⚠️  Não há voluntários no seu bairro. Procure ajuda por perto.")

    mostrar_emergencia()
    print(LINHA)


def checar_pessoa(perfil: dict, risco: dict) -> None:
    """Checagem automática quando o risco vira PERIGO.

    Resposta 's' encerra a checagem. Resposta 'n' ou Enter vazio (simula a
    pessoa que não consegue responder) aciona a rede de apoio.
    """
    print()
    print(LINHA_ALERTA)
    print(f" ⚠️  ALERTA: risco de {risco['nivel']} ({risco['tipo']})")
    print(LINHA_ALERTA)
    print()
    print(" Você está bem?")
    print("   s     → estou bem")
    print("   n     → preciso de ajuda")
    print("   Enter → não consigo responder")

    while True:
        status = input("\n Sua resposta: ").strip().lower()
        if status == "s":
            print("\n   ✅ Que bom! Siga as recomendações do painel.")
            registrar_alerta(risco, "checagem", "pessoa confirmou que está bem")
            return
        elif status == "n" or status == "":
            acionar_rede(perfil)
            registrar_alerta(risco, "checagem", "rede acionada")
            return
        else:
            print(" Digite s, n ou apenas pressione Enter.")


def pedir_ajuda(perfil: dict, risco: dict | None) -> None:
    """Pedido manual de ajuda (opção 4), com confirmação para evitar acionamento acidental."""
    titulo("🆘 PEDIR AJUDA")
    confirmacao = ler_sim_nao(" Confirma o pedido de ajuda? (s/n) ")

    if confirmacao:
        acionar_rede(perfil)
        registrar_alerta(risco, "pedido manual", "rede acionada")
    else:
        print("\n   Pedido cancelado.")

def mostrar_historico() -> None:
    """Mostra os alertas do mais recente ao mais antigo e um resumo dos resultados."""
    titulo("📋 HISTÓRICO DE ALERTAS")

    alertas = ler_lista("alertas.json", alerta_valido)
    if not alertas:
        print("Nenhum alerta registrado ainda.")
        return

    for alerta in reversed(alertas):
        horario = datetime.fromisoformat(alerta["horario"]).strftime("%d/%m %H:%M")
        risco = alerta["nivel"]
        if alerta["tipo"] is not None:
            risco += f" ({alerta['tipo']})"
        print(f"   {horario} · {risco} · {alerta['motivo']} → {alerta['resultado']}")

    confirmados = 0
    rede_acionada = 0

    for alerta in alertas:
        if alerta["resultado"] == "pessoa confirmou que está bem":
            confirmados += 1
        elif alerta["resultado"] == "rede acionada":
            rede_acionada += 1

    total = len(alertas)
    porcentagem = confirmados / total * 100

    print(f"\n Total de alertas: {total}")
    print(f" Pessoa confirmou que estava bem: {confirmados} ({porcentagem:.0f}%)")
    print(f" Rede de apoio acionada: {rede_acionada}")
        