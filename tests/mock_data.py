"""Dados mockados para desenvolvimento e testes.

Fornece previsões fictícias para uso nos testes unitários e para
desenvolvimento da camada de display sem depender da API real.
"""

from weather.models import WeatherData


MOCK_CITY: str = "São Paulo, Brazil"

MOCK_FORECASTS: list[WeatherData] = [
    WeatherData(
        date="2025-06-16", weekday="Seg",
        temp_min=16.2, temp_max=25.8,
        description="Parcialmente nublado", weather_code=2,
    ),
    WeatherData(
        date="2025-06-17", weekday="Ter",
        temp_min=17.0, temp_max=27.3,
        description="Céu limpo", weather_code=0,
    ),
    WeatherData(
        date="2025-06-18", weekday="Qua",
        temp_min=18.5, temp_max=30.1,
        description="Céu limpo", weather_code=0,
    ),
    WeatherData(
        date="2025-06-19", weekday="Qui",
        temp_min=19.0, temp_max=28.6,
        description="Parcialmente nublado", weather_code=2,
    ),
    WeatherData(
        date="2025-06-20", weekday="Sex",
        temp_min=15.3, temp_max=22.0,
        description="Chuva leve", weather_code=61,
    ),
    WeatherData(
        date="2025-06-21", weekday="Sáb",
        temp_min=14.0, temp_max=20.5,
        description="Chuva moderada", weather_code=63,
    ),
    WeatherData(
        date="2025-06-22", weekday="Dom",
        temp_min=15.8, temp_max=24.2,
        description="Nublado", weather_code=3,
    ),
]

# Resposta simulada da API para testes do fetcher.
MOCK_API_RESPONSE: dict = {
    "daily": {
        "time": [
            "2025-06-16", "2025-06-17", "2025-06-18",
            "2025-06-19", "2025-06-20", "2025-06-21",
            "2025-06-22",
        ],
        "temperature_2m_max": [25.8, 27.3, 30.1, 28.6, 22.0, 20.5, 24.2],
        "temperature_2m_min": [16.2, 17.0, 18.5, 19.0, 15.3, 14.0, 15.8],
        "weather_code": [2, 0, 0, 2, 61, 63, 3],
    }
}

MOCK_GEOCODING_RESPONSE: dict = {
    "results": [
        {
            "name": "São Paulo",
            "latitude": -23.5475,
            "longitude": -46.6361,
            "country": "Brazil",
        }
    ]
}
