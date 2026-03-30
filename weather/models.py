"""Modelos de dados para o WeatherWise CLI.

Define as estruturas de dados compartilhadas entre a camada
de busca (fetcher) e a camada de apresentação (display).
"""

from dataclasses import dataclass


@dataclass
class WeatherData:
    """Representa a previsão do tempo para um único dia.

    Attributes:
        date: Data no formato 'YYYY-MM-DD'.
        weekday: Dia da semana abreviado (ex: 'Seg', 'Ter').
        temp_min: Temperatura mínima em °C.
        temp_max: Temperatura máxima em °C.
        description: Descrição textual do clima (ex: 'Céu limpo').
        weather_code: Código WMO original retornado pela API.
    """

    date: str
    weekday: str
    temp_min: float
    temp_max: float
    description: str
    weather_code: int
