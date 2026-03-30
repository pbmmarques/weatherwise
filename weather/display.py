"""Módulo de apresentação do WeatherWise CLI.

Responsável por toda a camada visual: formatação simples,
tabelas, gráficos ASCII e mensagens de erro exibidas no terminal.

Autor: João
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from weather.models import WeatherData


# Console global reutilizado em todas as funções de exibição.
console = Console()

# Mapa de descrições climáticas para emojis.
WEATHER_ICONS: dict[str, str] = {
    "Céu limpo": "☀️",
    "Predominantemente limpo": "🌤️",
    "Parcialmente nublado": "⛅",
    "Nublado": "☁️",
    "Névoa": "🌫️",
    "Névoa com geada": "🌫️",
    "Garoa leve": "🌦️",
    "Garoa moderada": "🌦️",
    "Garoa intensa": "🌧️",
    "Garoa congelante leve": "🌧️",
    "Garoa congelante intensa": "🌧️",
    "Chuva leve": "🌧️",
    "Chuva moderada": "🌧️",
    "Chuva forte": "⛈️",
    "Chuva congelante leve": "🌧️",
    "Chuva congelante forte": "⛈️",
    "Neve leve": "🌨️",
    "Neve moderada": "❄️",
    "Neve forte": "❄️",
    "Grãos de neve": "❄️",
    "Pancadas de chuva leve": "🌦️",
    "Pancadas de chuva moderada": "🌧️",
    "Pancadas de chuva forte": "⛈️",
    "Pancadas de neve leve": "🌨️",
    "Pancadas de neve forte": "❄️",
    "Trovoada": "⛈️",
    "Trovoada com granizo leve": "⛈️",
    "Trovoada com granizo forte": "⛈️",
}


def _get_icon(description: str) -> str:
    """Retorna o emoji correspondente à descrição do clima.

    Args:
        description: Texto descritivo do clima.

    Returns:
        Emoji correspondente ou '🌡️' como fallback.
    """
    return WEATHER_ICONS.get(description, "🌡️")


# ---------------------------------------------------------------------------
# 1. EXIBIÇÃO SIMPLES (formato padrão)
# ---------------------------------------------------------------------------

def display_simple(city: str, forecasts: list[WeatherData]) -> None:
    """Exibe a previsão em formato simples, uma linha por dia.

    Args:
        city: Nome da cidade consultada.
        forecasts: Lista de previsões diárias.
    """
    console.print()
    console.print(Panel(f"[bold cyan]Previsão para {city}[/bold cyan]", expand=False))
    console.print()

    for day in forecasts:
        icon = _get_icon(day.description)
        console.print(
            f"  {icon}  [bold]{day.weekday}[/bold] {day.date}  │  "
            f"[blue]{day.temp_min:.0f}°C[/blue] – "
            f"[red]{day.temp_max:.0f}°C[/red]  │  "
            f"{day.description}"
        )

    console.print()


# ---------------------------------------------------------------------------
# 2. EXIBIÇÃO EM TABELA (--format table)
# ---------------------------------------------------------------------------

def display_table(city: str, forecasts: list[WeatherData]) -> None:
    """Exibe a previsão em uma tabela formatada com rich.

    Args:
        city: Nome da cidade consultada.
        forecasts: Lista de previsões diárias.
    """
    table = Table(
        title=f"Previsão para {city}",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )

    table.add_column("Dia", style="bold", min_width=4)
    table.add_column("Data", min_width=10)
    table.add_column("Mín (°C)", justify="right", style="blue")
    table.add_column("Máx (°C)", justify="right", style="red")
    table.add_column("Clima")

    for day in forecasts:
        icon = _get_icon(day.description)
        table.add_row(
            day.weekday,
            day.date,
            f"{day.temp_min:.1f}",
            f"{day.temp_max:.1f}",
            f"{icon}  {day.description}",
        )

    console.print()
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# 3. GRÁFICO ASCII (--chart)
# ---------------------------------------------------------------------------

CHART_BAR_WIDTH: int = 40


def display_chart(city: str, forecasts: list[WeatherData]) -> None:
    """Exibe um gráfico de barras ASCII com a variação de temperatura.

    Cada linha mostra a faixa entre a mínima e máxima do dia,
    posicionada proporcionalmente dentro da escala global.

    Args:
        city: Nome da cidade consultada.
        forecasts: Lista de previsões diárias.
    """
    if not forecasts:
        console.print("[red]Sem dados para exibir o gráfico.[/red]")
        return

    all_min = min(day.temp_min for day in forecasts)
    all_max = max(day.temp_max for day in forecasts)
    temp_range = all_max - all_min if all_max != all_min else 1.0

    console.print()
    console.print(
        Panel(
            f"[bold cyan]Temperaturas em {city}[/bold cyan]",
            expand=False,
        )
    )
    console.print()

    for day in forecasts:
        bar = _build_bar(day.temp_min, day.temp_max, all_min, temp_range)
        console.print(
            f"  [bold]{day.weekday}[/bold]  "
            f"[blue]{day.temp_min:5.1f}°C[/blue] – "
            f"[red]{day.temp_max:5.1f}°C[/red]  "
            f"{bar}"
        )

    console.print(
        f"\n  [dim]Escala: {all_min:.0f}°C"
        + " " * (CHART_BAR_WIDTH - 10)
        + f"{all_max:.0f}°C[/dim]\n"
    )


def _build_bar(
    temp_min: float,
    temp_max: float,
    global_min: float,
    temp_range: float,
) -> str:
    """Constrói uma barra ASCII representando a faixa de temperatura.

    Args:
        temp_min: Temperatura mínima do dia.
        temp_max: Temperatura máxima do dia.
        global_min: Menor temperatura de todo o período.
        temp_range: Amplitude térmica global.

    Returns:
        String com a barra (ex: '░░░░████████░░░░').
    """
    start = int((temp_min - global_min) / temp_range * CHART_BAR_WIDTH)
    end = int((temp_max - global_min) / temp_range * CHART_BAR_WIDTH)
    end = max(end, start + 1)

    bar = "░" * start + "█" * (end - start) + "░" * (CHART_BAR_WIDTH - end)
    return bar


# ---------------------------------------------------------------------------
# 4. EXPORTAÇÃO CSV (feature extra)
# ---------------------------------------------------------------------------

def export_csv(city: str, forecasts: list[WeatherData], filepath: str) -> None:
    """Exporta a previsão para um arquivo CSV.

    Args:
        city: Nome da cidade consultada.
        forecasts: Lista de previsões diárias.
        filepath: Caminho do arquivo de saída.
    """
    import csv

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Cidade", "Data", "Dia", "Mín (°C)", "Máx (°C)", "Clima"])

        for day in forecasts:
            writer.writerow([
                city,
                day.date,
                day.weekday,
                day.temp_min,
                day.temp_max,
                day.description,
            ])

    console.print(f"\n[green]✓ Relatório exportado para:[/green] {filepath}\n")


# ---------------------------------------------------------------------------
# 5. MENSAGENS DE ERRO
# ---------------------------------------------------------------------------

def display_error(message: str) -> None:
    """Exibe uma mensagem de erro formatada no terminal.

    Args:
        message: Texto descritivo do erro.
    """
    console.print(f"\n[bold red]✗ Erro:[/bold red] {message}\n")


def display_not_found(city: str) -> None:
    """Exibe mensagem quando a cidade não é encontrada.

    Args:
        city: Nome da cidade pesquisada.
    """
    display_error(
        f"Não foi possível encontrar a cidade '{city}'. "
        "Verifique o nome e tente novamente."
    )
