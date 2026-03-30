#!/usr/bin/env python3
"""WeatherWise CLI — ponto de entrada da aplicação.

Uso:
    python weather.py --city "São Paulo"
    python weather.py --city "Campinas" --days 5 --format table
    python weather.py --city "Rio de Janeiro" --chart
    python weather.py --city "Curitiba" --output previsao.csv

Autores: Pedro e João
"""

import argparse
import sys

from weather.fetcher import get_weather, CityNotFoundError, FetchError
from weather.display import (
    display_simple,
    display_table,
    display_chart,
    display_error,
    export_csv,
)


def build_parser() -> argparse.ArgumentParser:
    """Cria e configura o parser de argumentos da CLI.

    Returns:
        ArgumentParser configurado com todas as flags.
    """
    parser = argparse.ArgumentParser(
        prog="weatherwise",
        description="🌤️  WeatherWise CLI — Previsão do tempo direto no terminal.",
        epilog="Dados fornecidos pela Open-Meteo API (open-meteo.com).",
    )

    parser.add_argument(
        "--city", "-c",
        type=str,
        required=True,
        help="Nome da cidade para consulta (ex: 'São Paulo').",
    )

    parser.add_argument(
        "--days", "-d",
        type=int,
        default=7,
        choices=range(1, 17),
        metavar="[1-16]",
        help="Número de dias de previsão (padrão: 7, máximo: 16).",
    )

    parser.add_argument(
        "--format", "-f",
        type=str,
        default="simple",
        choices=["simple", "table"],
        help="Formato de exibição: 'simple' (padrão) ou 'table'.",
    )

    parser.add_argument(
        "--chart",
        action="store_true",
        help="Exibe gráfico ASCII de temperatura junto com a previsão.",
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        metavar="ARQUIVO.csv",
        help="Exporta o relatório para um arquivo CSV (feature extra).",
    )

    return parser


def main() -> None:
    """Função principal que orquestra o fluxo da aplicação."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        city_display, forecasts = get_weather(args.city, args.days)
    except CityNotFoundError as exc:
        display_error(str(exc))
        sys.exit(1)
    except FetchError as exc:
        display_error(str(exc))
        sys.exit(1)

    # Exibe a previsão no formato escolhido.
    if args.format == "table":
        display_table(city_display, forecasts)
    else:
        display_simple(city_display, forecasts)

    # Exibe o gráfico ASCII se solicitado.
    if args.chart:
        display_chart(city_display, forecasts)

    # Exporta para CSV se solicitado.
    if args.output:
        export_csv(city_display, forecasts, args.output)


if __name__ == "__main__":
    main()
