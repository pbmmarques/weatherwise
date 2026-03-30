"""Testes unitários para o módulo fetcher.

Executa com: pytest tests/test_fetcher.py -v

Autor: Pedro
"""

from unittest.mock import patch, MagicMock

import pytest

from weather.fetcher import (
    geocode_city,
    parse_forecast,
    CityNotFoundError,
    FetchError,
    WMO_DESCRIPTIONS,
)
from tests.mock_data import MOCK_API_RESPONSE, MOCK_GEOCODING_RESPONSE


# ---------------------------------------------------------------------------
# Testes para geocode_city
# ---------------------------------------------------------------------------

class TestGeocodeCity:
    """Testes para a função de geocodificação."""

    @patch("weather.fetcher.requests.get")
    def test_geocode_returns_coordinates(self, mock_get: MagicMock) -> None:
        """Deve retornar lat, lon e nome formatado."""
        mock_response = MagicMock()
        mock_response.json.return_value = MOCK_GEOCODING_RESPONSE
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        lat, lon, name = geocode_city("São Paulo")

        assert lat == pytest.approx(-23.5475)
        assert lon == pytest.approx(-46.6361)
        assert "São Paulo" in name

    @patch("weather.fetcher.requests.get")
    def test_geocode_city_not_found(self, mock_get: MagicMock) -> None:
        """Deve levantar CityNotFoundError para cidades inexistentes."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": None}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        with pytest.raises(CityNotFoundError):
            geocode_city("CidadeQueNaoExiste12345")

    @patch("weather.fetcher.requests.get")
    def test_geocode_connection_error(self, mock_get: MagicMock) -> None:
        """Deve levantar FetchError quando não há conexão."""
        import requests
        mock_get.side_effect = requests.ConnectionError("Sem rede")

        with pytest.raises(FetchError, match="conexão"):
            geocode_city("São Paulo")


# ---------------------------------------------------------------------------
# Testes para parse_forecast
# ---------------------------------------------------------------------------

class TestParseForecast:
    """Testes para a conversão de JSON em WeatherData."""

    def test_parse_returns_correct_count(self) -> None:
        """Deve retornar um WeatherData para cada dia."""
        result = parse_forecast(MOCK_API_RESPONSE)
        assert len(result) == 7

    def test_parse_first_day_values(self) -> None:
        """Deve mapear corretamente os valores do primeiro dia."""
        result = parse_forecast(MOCK_API_RESPONSE)
        first = result[0]

        assert first.date == "2025-06-16"
        assert first.weekday == "Seg"
        assert first.temp_min == pytest.approx(16.2)
        assert first.temp_max == pytest.approx(25.8)
        assert first.weather_code == 2

    def test_parse_maps_weather_code_to_description(self) -> None:
        """Deve traduzir weather_code para descrição em português."""
        result = parse_forecast(MOCK_API_RESPONSE)
        first = result[0]

        assert first.description == WMO_DESCRIPTIONS[2]

    def test_parse_invalid_structure_raises_error(self) -> None:
        """Deve levantar FetchError para JSON mal-formado."""
        with pytest.raises(FetchError, match="formato inesperado"):
            parse_forecast({"dados": "invalidos"})

    def test_parse_empty_daily_raises_error(self) -> None:
        """Deve levantar FetchError quando 'daily' está incompleto."""
        with pytest.raises(FetchError):
            parse_forecast({"daily": {"time": []}})
