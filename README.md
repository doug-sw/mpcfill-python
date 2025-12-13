## MPCFill Python

Lightweight CLI and library to search and download high-quality MTG card images from community sources with simple caching.

### Installation
- Create a virtual environment and install in editable mode:
```
cd /home/doug/code/mpcfill-python
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -e .
```

### Quick Start
- Try the CLI without installing the console script:
```
source venv/bin/activate
python -c "from mpcfill.cli import main; main(['list','sources'])"
python -c "from mpcfill.cli import main; main(['search','Welcome to','--json'])"
python -c "from mpcfill.cli import main; main(['download','Opt','--dest','downloads','--threads','2'])"
```
- Or install the console script and use `mpcfill` directly:
```
source venv/bin/activate
pip install -e .
mpcfill --help
```

### CLI Usage
- Unified list commands:
```
mpcfill list sources
mpcfill list languages
mpcfill list tags
mpcfill list dfcs
```

- Search best candidates (use `t:` prefix for tokens):
```
mpcfill search "Shoot the Sheriff"
mpcfill search "t:Treasure" "Dragon Egg" --minimum-dpi 600 --no-backs
mpcfill search "Shoot the Sheriff" --json
mpcfill search "Welcome to..." --enable-sources MrTeferi JohnPrime --disable-sources Chilli_Axe
```

- Download best images:
```
mpcfill download "Welcome to..." --dest downloads
mpcfill download "Welcome to..." --dest downloads --enable-sources MrTeferi JohnPrime --disable-sources Chilli_Axe
mpcfill download "Welcome to..." --dest downloads --threads 4
```

### CLI Examples
- List catalogs:
```
mpcfill list sources
mpcfill list languages
mpcfill list tags | head -n 40
mpcfill list dfcs | head -n 20
```

Tip: Tokens use the `t:` prefix (e.g., `t:Treasure`).

- Search and view results:
```
mpcfill search "Shoot the Sheriff"
mpcfill search "t:Treasure" "Dragon Egg"
mpcfill search "Shoot the Sheriff" --json | jq
mpcfill search "Welcome to..." --enable-sources MrTeferi JohnPrime --disable-sources Chilli_Axe
```

- Download best images:
```
mpcfill download "Welcome to..." --dest downloads
mpcfill download "t:Treasure" "Dragon Egg" --dest downloads --no-backs
mpcfill download "Welcome to..." --dest downloads --threads 8
```

Notes:
- The CLI exits cleanly when piping (e.g., `| head`), suppressing BrokenPipe noise.
- Use `--threads` to download in parallel for higher throughput.
- Prefer or disable sources by name; order of `--prefer-sources` sets priority.
- Tokens use the `t:` prefix (e.g., `t:Treasure`).

### Library Usage
```
from mpcfill import search_cards, SearchSettings, CardType

queries = [
	{"query": "Welcome to...", "cardType": CardType.CARD},
	{"query": "Treasure", "cardType": CardType.TOKEN},
]

settings = SearchSettings(minimum_dpi=600, maximum_dpi=1500, maximum_size=30)
# Prefer sources by name (order = priority)
settings.enable_source("MrTeferi")
settings.set_source_priority("MrTeferi", 0)
settings.enable_source("JohnPrime")
settings.set_source_priority("JohnPrime", 1)
settings.disable_source("Bobungus")
groups = search_cards(queries, settings, fetch_backs=True)
best = [g[0] for g in groups]
for b in best:
	print(b.identifier, b.name, b.priority)
```

### Example Script
Run the included examples:
```
python examples/list_catalog.py
python examples/search_table.py
python examples/download.py
```

### Development
- Console script: `mpcfill`
- Cached catalog fetches (`sources`, `languages`, `tags`, `dfcs`) via `services.catalog`.
- HTTP client with rate limiting in `http/client.py`.