# MovieLens SDK - `hmoviessdk`

A simple Python SDK to interact with the MovieLens REST API.It is designed for **Data Analysts** and **Data Scientists**, with native support for **Pydantic**, **dictionnary** and **Pandas DataFrames**.

[![PyPI version](https://badge.fury.io/py/moviesdk.svg)](https://badge.fury.io/py/hmoviessdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

---

## Installation

```bash
pip install hmoviessdk
```

---

## Configuration

```python
from hmoviessdk import MovieClient, MovieConfig

# Configuration with your API URL (Render or local)
config = MovieConfig(movie_base_url="https://api-architecture.onrender.com")
client = MovieClient(config=config)
```

---

## Test the SDK

### 1. Health check

```python
client.health_check()
# Return: {"status": "ok"}
```

### 2. Retrieve a movie
```python
movie = client.get_movie(1)
print(movie.title)
```

### 3. List of movies in DataFrame format 

```python
df = client.list_movies(limit=5, output_format="pandas")
print(df.head())
```

---

## Output mode available

All list methods (`list_movies`, `list_ratings`, etc.) can return :

- **Pydantic** object (défaut)
- **dictionnary**
- **Pandas DataFrames**

Example :

```python
client.list_movies(limit=10, output_format="dict")
client.list_ratings(limit=10, output_format="pandas")
```

---

## Local test

You can also use local API :

```python
config = MovieConfig(movie_base_url="http://localhost:8000")
client = MovieClient(config=config)
```

---

## Target audience

- Data Analysts
- Data Scientists
- Students in Data
- Python Developers

---

## Licence

MIT License

---

## Useful Links

- API Render : [https://api-architecture.onrender.com](https://api-architecture.onrender.com)
- PyPI : [https://pypi.org/project/hmoviessdk/](https://pypi.org/project/hmoviessdk/)