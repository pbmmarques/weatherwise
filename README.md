# 🌤️ WeatherWise CLI

Ferramenta de linha de comando em Python para consulta e exibição de dados climáticos em tempo real, utilizando a [Open-Meteo API](https://open-meteo.com/).

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/weatherwise.git
cd weatherwise

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Uso

### Previsão padrão (7 dias)

```bash
python weather.py --city "São Paulo"
```

### Previsão em tabela formatada

```bash
python weather.py --city "Campinas" --days 5 --format table
```

### Com gráfico ASCII de temperatura

```bash
python weather.py --city "Rio de Janeiro" --chart
```

### Tabela + gráfico juntos

```bash
python weather.py --city "Curitiba" --days 10 --format table --chart
```

### Exportar para CSV (feature extra)

```bash
python weather.py --city "Belo Horizonte" --output previsao.csv
```

## Argumentos disponíveis

| Argumento       | Tipo    | Padrão   | Descrição                                  |
|-----------------|---------|----------|--------------------------------------------|
| `--city`, `-c`  | texto   | —        | Nome da cidade (obrigatório)               |
| `--days`, `-d`  | inteiro | 7        | Dias de previsão (1 a 16)                  |
| `--format`, `-f`| texto   | simple   | Formato: `simple` ou `table`               |
| `--chart`       | flag    | —        | Exibe gráfico ASCII de temperaturas        |
| `--output`, `-o`| texto   | —        | Caminho para exportar CSV                  |

## Estrutura do projeto

```
weatherwise/
├── weather/
│   ├── __init__.py
│   ├── fetcher.py      # Busca e parsing da API (Pedro)
│   ├── models.py       # Dataclass WeatherData (Pedro)
│   └── display.py      # Formatação e gráfico ASCII (João)
├── tests/
│   ├── mock_data.py    # Dados de teste compartilhados
│   ├── test_fetcher.py # Testes do módulo de dados
│   └── test_display.py # Testes do módulo de display
├── weather.py          # Entry point (ambos)
├── requirements.txt
└── README.md
```

## Testes

```bash
# Rodar todos os testes
pytest -v

# Rodar apenas testes do display
pytest tests/test_display.py -v

# Rodar apenas testes do fetcher
pytest tests/test_fetcher.py -v
```

## Tecnologias

- **Python 3.10+**
- **requests** — Comunicação HTTP com a API
- **rich** — Formatação de tabelas e cores no terminal
- **pytest** — Framework de testes
- **Open-Meteo API** — Dados climáticos gratuitos (sem cadastro)

## WeatherWise Web

Além da CLI, o projeto conta com uma interface web com chatbot de IA integrado:

- **Frontend:** hospedado no Netlify (PWA instalável)
- **Backend:** servidor Flask no Render
- **IA:** Google Gemini com dados climáticos em tempo real

## Autores

- **Pedro** — Módulo de dados e API (`fetcher.py`, `models.py`)
- **João** — Módulo de apresentação e CLI (`display.py`, `weather.py`)
