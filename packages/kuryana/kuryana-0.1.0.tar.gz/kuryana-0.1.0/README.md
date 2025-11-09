# kuryana

Python library for [Kuryana](https://github.com/tbdsux/kuryana) API.

## Install

```sh
# pip
pip install kuryana

# uv
uv add kuryana
```

## Development

```sh
# install deps
uv sync
```

## Usage

Clients are built on top of `httpx`

```python
from kuryana import Kuryana

client = Kuryana()


if __name__ == "__main__":
    response = client.get()
    print(response.message)

    assert "MDL Scraper API" in response.message

    print("\n\n")

    search = client.search("goblin")
    for drama in search.results.dramas:
        print(f"{drama.title} - {drama.year}")

```

### Async Client

```python
import asyncio

from kuryana import AsyncKuryana

client = AsyncKuryana()


async def main():
    response = await client.get()
    print(response.message)

    assert "MDL Scraper API" in response.message

    print("\n\n")

    search = await client.search("goblin")
    for drama in search.results.dramas:
        print(f"{drama.title} - {drama.year}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

&copy; 2025 | tbdsux
