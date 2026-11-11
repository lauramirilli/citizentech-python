from datetime import datetime
import requests
from arquivos import ler_json, salvar_json
from entradas import ler_numero
from validacao import previsao_valida

BAIRROS = {
    "Sapopemba": (-23.604, -46.511),
    "Jardim Pantanal": (-23.493, -46.426),
    "Parque Brasilândia": (-23.465, -46.690),
}

SEM_CHUVA = {"mm_hora_max": 0, "mm_dia": 0}

URL_OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
TEMPO_LIMITE = 10

def carregar_previsao() -> dict:
    """Devolve a última previsão salva, ou SEM_CHUVA se não houver nenhuma válida."""
    previsao = ler_json("previsao.json", SEM_CHUVA)
    if not previsao_valida(previsao):
        print("Aviso: previsao.json está incompleto. Considerando sem chuva.")
        return SEM_CHUVA
    return previsao

def simular_previsao() -> dict:
    """Pede valores de chuva para demonstração, salva em previsao.json e devolve."""
    
    mm_hora_max = ler_numero("Chuva máxima em 1 hora, em mm (ex.: 25 = atenção, 35 = perigo): ", 0, 200)
    mm_dia = ler_numero("Chuva total no dia, em mm (ex.: 50 = atenção, 100 = perigo): ", 0, 500)

    previsao = {
        "mm_hora_max": mm_hora_max,
        "mm_dia": mm_dia,
        "fonte": "simulada",
        "atualizado_em": datetime.now().isoformat(timespec="minutes")
    }
    salvar_json("previsao.json", previsao)
    return previsao

 
def buscar_previsao_real(bairro: str) -> dict:
    """Busca a previsão de chuva de hoje na API Open-Meteo para o bairro.
 
    Se o bairro não tiver coordenadas, se não houver internet ou se a
    resposta vier em formato inesperado, avisa e devolve a última
    previsão salva (fallback offline).
    """

    if bairro not in BAIRROS:
        print(f"Aviso: não há coordenadas para {bairro}. Usando a última previsão salva.")
        return carregar_previsao()
 
    latitude, longitude = BAIRROS[bairro]
    parametros = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "precipitation",
        "timezone": "America/Sao_Paulo",
        "forecast_days": 1,
    }
 
    try:
        resposta = requests.get(URL_OPEN_METEO, params=parametros, timeout=TEMPO_LIMITE)
        resposta.raise_for_status()
        chuva_por_hora = resposta.json()["hourly"]["precipitation"]

        valores = []
        for mm in chuva_por_hora:
            if mm is not None:
                valores.append(float(mm))
    except (KeyError, TypeError, ValueError):
        print("A previsão veio em formato inesperado. Usando a última previsão salva.")
        return carregar_previsao()
    except requests.RequestException:
        print("Sem conexão com o serviço de previsão. Usando a última previsão salva.")
        return carregar_previsao()

    if not valores:
        print("A previsão veio vazia. Usando a última previsão salva.")
        return carregar_previsao()
 
    previsao = {
        "mm_hora_max": max(valores),
        "mm_dia": round(sum(valores), 1),
        "fonte": "Open-Meteo",
        "atualizado_em": datetime.now().isoformat(timespec="minutes"),
    }
    salvar_json("previsao.json", previsao)

    print(f"Previsão atualizada: até {previsao['mm_hora_max']} mm em 1 hora, "
          f"{previsao['mm_dia']} mm no dia (Open-Meteo).")
    
    return previsao