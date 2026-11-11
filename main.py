from arquivos import ler_json, ler_lista
from validacao import perfil_valido, leitura_valida
from entradas import ler_opcao
from cadastros import registrar_leitura, mostrar_abrigos, gerenciar_rede, configurar_perfil, menu_perfil
from painel import exibir_painel
from risco import obter_recomendacoes
from previsao import simular_previsao, buscar_previsao_real
from ajuda import checar_pessoa, pedir_ajuda, mostrar_historico

MENU = """
1. Ver recomendações completas
2. Registrar leitura
3. Atualizar previsão
4. Pedir ajuda
5. Abrigos próximos
6. Rede de apoio
7. Meu perfil
8. Histórico de alertas
0. Sair
"""
OPCOES = ("1", "2", "3", "4", "5", "6", "7", "8", "0")
DESPEDIDA = "Até logo! Em caso de emergência, ligue 192 (SAMU), 193 (Bombeiros) ou 199 (Defesa Civil)."

def executar() -> None:
    """Loop principal: mostra o painel, o menu e executa a opção escolhida."""

    perfil = ler_json("perfil.json", None)

    if perfil is not None and not perfil_valido(perfil):
        print("Aviso: perfil.json está incompleto. Vamos configurar o perfil de novo.")
        perfil = None

    if perfil is None:
        print("Bem-vindo(a) ao Amparo! Vamos configurar o perfil da pessoa atendida.")
        perfil = configurar_perfil()

    previsao = buscar_previsao_real(perfil["bairro"])
    nivel_anterior = None

    while True:
        leituras = ler_lista("leituras.json", leitura_valida)
        risco = exibir_painel(perfil, leituras, previsao)

        if risco is not None and risco["nivel"] == "PERIGO" and nivel_anterior != "PERIGO":
            checar_pessoa(perfil, risco)

        if risco is not None:
            nivel_anterior = risco["nivel"]
        else:
            nivel_anterior = None

        print(MENU)
        opcao = ler_opcao("Escolha uma opção: ", OPCOES)

        match opcao:
            case "1":
                if risco is None:
                    print("\nAinda não há leitura. Registre uma na opção 2.")
                else:
                    dicas = obter_recomendacoes(risco["tipo"], risco["nivel"], perfil["risco_chuva"])
                    print(f"\nRecomendações ({risco['nivel']}):")
                    for numero, dica in enumerate(dicas, start=1):
                        print(f"{numero}. {dica}")
            case "2":
                registrar_leitura()
            case "3":
                print("\n1. Buscar previsão real (internet)")
                print("2. Simular previsão (demonstração)")
                escolha = ler_opcao("Escolha: ", ("1", "2"))

                match escolha:
                    case "1":
                        previsao = buscar_previsao_real(perfil["bairro"])
                    case "2":
                        previsao = simular_previsao()
            case "4":
                pedir_ajuda(perfil, risco)
            case "5":
                mostrar_abrigos(perfil, risco)
            case "6":
                gerenciar_rede(perfil)
            case "7":
                bairro_antigo = perfil["bairro"]
                perfil = menu_perfil(perfil)
                if perfil["bairro"] != bairro_antigo:
                    previsao = buscar_previsao_real(perfil["bairro"])
            case "8":
                mostrar_historico()
            case "0":
                print(f"\n{DESPEDIDA}")
                break

        input("\nPressione Enter para voltar ao menu...")

def main() -> None:
    """Roda o programa; Ctrl+C ou Ctrl+D encerram sem mostrar erro."""
    try:
        executar()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\nPrograma encerrado. {DESPEDIDA}")

if __name__ == "__main__":
    main()