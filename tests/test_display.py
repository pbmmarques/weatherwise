"""Testes unitários para o módulo de display.

Executa com: pytest tests/test_display.py -v

Autor: João
"""

import os
import tempfile

import pytest

from weather.display import (
    _build_bar,
    _get_icon,
    display_simple,
    display_table,
    display_chart,
    display_error,
    display_not_found,
    export_csv,
    CHART_BAR_WIDTH,
)
from tests.mock_data import MOCK_FORECASTS, MOCK_CITY


# ---------------------------------------------------------------------------
# Testes para _get_icon
# ---------------------------------------------------------------------------

class TestGetIcon:
    """Testes para o mapeamento de descrição para emoji."""

    def test_known_description(self) -> None:
        assert _get_icon("Céu limpo") == "☀️"

    def test_rain_description(self) -> None:
        assert _get_icon("Chuva leve") == "🌧️"

    def test_unknown_description_returns_fallback(self) -> None:
        assert _get_icon("Tornado de fogo") == "🌡️"

    def test_empty_string_returns_fallback(self) -> None:
        assert _get_icon("") == "🌡️"


# ---------------------------------------------------------------------------
# Testes para _build_bar
# ---------------------------------------------------------------------------

class TestBuildBar:
    """Testes para a construção da barra ASCII."""

    def test_bar_has_correct_length(self) -> None:
        bar = _build_bar(10.0, 20.0, 0.0, 40.0)
        assert len(bar) == CHART_BAR_WIDTH

    def test_full_range_bar(self) -> None:
        """Min=global_min e max=global_max → barra toda preenchida."""
        bar = _build_bar(0.0, 40.0, 0.0, 40.0)
        assert "░" not in bar

    def test_minimal_range_has_filled_block(self) -> None:
        """Mesmo com faixa mínima, deve ter ao menos um █."""
        bar = _build_bar(20.0, 20.5, 0.0, 40.0)
        assert "█" in bar

    def test_mid_range_bar_has_empty_sides(self) -> None:
        """Barra no meio deve ter ░ nas extremidades."""
        bar = _build_bar(10.0, 30.0, 0.0, 40.0)
        assert bar[0] == "░"
        assert bar[-1] == "░"

    def test_bar_with_zero_range(self) -> None:
        """Quando temp_range=1 (fallback), não deve dar ZeroDivisionError."""
        bar = _build_bar(20.0, 20.0, 20.0, 1.0)
        assert len(bar) == CHART_BAR_WIDTH


# ---------------------------------------------------------------------------
# Smoke tests — verificam que as funções rodam sem exceção
# ---------------------------------------------------------------------------

class TestDisplaySmoke:
    """Smoke tests para as funções de exibição."""

    def test_display_simple_runs(self) -> None:
        display_simple(MOCK_CITY, MOCK_FORECASTS)

    def test_display_table_runs(self) -> None:
        display_table(MOCK_CITY, MOCK_FORECASTS)

    def test_display_chart_runs(self) -> None:
        display_chart(MOCK_CITY, MOCK_FORECASTS)

    def test_display_chart_empty_list(self) -> None:
        """Lista vazia deve exibir mensagem, não dar crash."""
        display_chart(MOCK_CITY, [])

    def test_display_simple_single_day(self) -> None:
        """Deve funcionar com apenas um dia de previsão."""
        display_simple(MOCK_CITY, MOCK_FORECASTS[:1])

    def test_display_chart_single_day(self) -> None:
        """Gráfico com um único dia não deve quebrar."""
        display_chart(MOCK_CITY, MOCK_FORECASTS[:1])


# ---------------------------------------------------------------------------
# Testes para mensagens de erro
# ---------------------------------------------------------------------------

class TestErrorDisplay:
    """Testes para funções de exibição de erro."""

    def test_display_error_runs(self) -> None:
        display_error("Algo deu errado")

    def test_display_not_found_runs(self) -> None:
        display_not_found("CidadeInexistente")


# ---------------------------------------------------------------------------
# Testes para exportação CSV
# ---------------------------------------------------------------------------

class TestExportCSV:
    """Testes para a feature extra de exportação em CSV."""

    def test_csv_file_is_created(self) -> None:
        """O arquivo CSV deve ser criado no caminho indicado."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            filepath = tmp.name

        try:
            export_csv(MOCK_CITY, MOCK_FORECASTS, filepath)
            assert os.path.exists(filepath)
        finally:
            os.unlink(filepath)

    def test_csv_has_correct_row_count(self) -> None:
        """O CSV deve ter header + N linhas de dados."""
        with tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="r"
        ) as tmp:
            filepath = tmp.name

        try:
            export_csv(MOCK_CITY, MOCK_FORECASTS, filepath)

            with open(filepath, encoding="utf-8") as f:
                lines = f.readlines()

            # 1 header + 7 dias
            assert len(lines) == 8
        finally:
            os.unlink(filepath)

    def test_csv_header_columns(self) -> None:
        """O header do CSV deve conter as colunas esperadas."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            filepath = tmp.name

        try:
            export_csv(MOCK_CITY, MOCK_FORECASTS, filepath)

            with open(filepath, encoding="utf-8") as f:
                header = f.readline().strip()

            assert "Cidade" in header
            assert "Data" in header
            assert "Clima" in header
        finally:
            os.unlink(filepath)
