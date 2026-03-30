"""Módulo de busca e parsing de dados climáticos.

Responsável por toda a comunicação com a Open-Meteo API:
geocodificação de cidades, busca de previsões e conversão
do JSON retornado em objetos WeatherData.

Autor: Pedro
"""

import locale
from datetime import datetime

import requests

from weather.models import WeatherData


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT = 10  # segundos

# Mapeamento dos códigos WMO para descrições em português.
# Referência: https://open-meteo.com/en/docs
WMO_DESCRIPTIONS: dict[int, str] = {
    0: "Céu limpo",
    1: "Predominantemente limpo",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Névoa",
    48: "Névoa com geada",
    51: "Garoa leve",
    53: "Garoa moderada",
    55: "Garoa intensa",
    56: "Garoa congelante leve",
    57: "Garoa congelante intensa",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    66: "Chuva congelante leve",
    67: "Chuva congelante forte",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve forte",
    77: "Grãos de neve",
    80: "Pancadas de chuva leve",
    81: "Pancadas de chuva moderada",
    82: "Pancadas de chuva forte",
    85: "Pancadas de neve leve",
    86: "Pancadas de neve forte",
    95: "Trovoada",
    96: "Trovoada com granizo leve",
    99: "Trovoada com granizo forte",
}

# Dias da semana abreviados em português.
WEEKDAYS_PT: list[str] = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


# ---------------------------------------------------------------------------
# Exceções customizadas
# ---------------------------------------------------------------------------

class CityNotFoundError(Exception):
    """Levantada quando a cidade não é encontrada pela API de geocodificação."""


class FetchError(Exception):
    """Levantada quando ocorre um erro na comunicação com a API."""


# ---------------------------------------------------------------------------
# Funções públicas
# ---------------------------------------------------------------------------

def geocode_city(city_name: str) -> tuple[float, float, str]:
    """Busca as coordenadas geográficas de uma cidade.

    Utiliza a API de geocodificação do Open-Meteo para converter
    o nome da cidade em latitude e longitude.

    Args:
        city_name: Nome da cidade (ex: 'São Paulo').

    Returns:
        Tupla com (latitude, longitude, nome_completo).

    Raises:
        CityNotFoundError: Se a cidade não for encontrada.
        FetchError: Se houver erro de rede ou resposta inválida.
    """
    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": city_name, "count": 1, "language": "pt"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise FetchError(
            "Sem conexão com a internet. Verifique sua rede."
        ) from exc
    except requests.Timeout as exc:
        raise FetchError(
            "A requisição excedeu o tempo limite. Tente novamente."
        ) from exc
    except requests.HTTPError as exc:
        raise FetchError(
            f"Erro HTTP {response.status_code} ao buscar a cidade."
        ) from exc

    data = response.json()
    results = data.get("results")

    if not results:
        raise CityNotFoundError(
            f"Cidade '{city_name}' não encontrada. Verifique o nome."
        )

    location = results[0]
    full_name = location.get("name", city_name)
    country = location.get("country", "")
    display_name = f"{full_name}, {country}" if country else full_name

    return location["latitude"], location["longitude"], display_name


def fetch_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
) -> dict:
    """Busca a previsão do tempo na Open-Meteo API.

    Args:
        latitude: Latitude da localidade.
        longitude: Longitude da localidade.
        days: Número de dias de previsão (1 a 16).

    Returns:
        Dicionário com os dados brutos (JSON) da API.

    Raises:
        FetchError: Se houver erro de rede ou resposta inválida.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone": "auto",
        "forecast_days": min(days, 16),
    }

    try:
        response = requests.get(
            FORECAST_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise FetchError(
            "Sem conexão com a internet. Verifique sua rede."
        ) from exc
    except requests.Timeout as exc:
        raise FetchError(
            "A requisição excedeu o tempo limite. Tente novamente."
        ) from exc
    except requests.HTTPError as exc:
        raise FetchError(
            f"Erro HTTP {response.status_code} ao buscar a previsão."
        ) from exc

    return response.json()


def parse_forecast(raw_data: dict) -> list[WeatherData]:
    """Converte o JSON bruto da API em uma lista de WeatherData.

    Args:
        raw_data: Dicionário retornado por fetch_forecast().

    Returns:
        Lista de objetos WeatherData, um por dia.

    Raises:
        FetchError: Se a estrutura do JSON for inesperada.
    """
    try:
        daily = raw_data["daily"]
        dates = daily["time"]
        temps_max = daily["temperature_2m_max"]
        temps_min = daily["temperature_2m_min"]
        codes = daily["weather_code"]
    except (KeyError, TypeError) as exc:
        raise FetchError(
            "Resposta da API em formato inesperado."
        ) from exc

    forecasts: list[WeatherData] = []

    for i, date_str in enumerate(dates):
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = WEEKDAYS_PT[dt.weekday()]
        code = codes[i]
        description = WMO_DESCRIPTIONS.get(code, f"Código {code}")

        forecasts.append(
            WeatherData(
                date=date_str,
                weekday=weekday,
                temp_min=temps_min[i],
                temp_max=temps_max[i],
                description=description,
                weather_code=code,
            )
        )

    return forecasts


def get_weather(city_name: str, days: int = 7) -> tuple[str, list[WeatherData]]:
    """Função principal que orquestra todo o fluxo de busca.

    Combina geocodificação, busca da previsão e parsing em um
    único ponto de entrada conveniente.

    Args:
        city_name: Nome da cidade.
        days: Número de dias de previsão.

    Returns:
        Tupla com (nome_da_cidade_formatado, lista_de_previsões).
    """
    latitude, longitude, display_name = geocode_city(city_name)
    raw_data = fetch_forecast(latitude, longitude, days)
    forecasts = parse_forecast(raw_data)
    return display_name, forecasts
