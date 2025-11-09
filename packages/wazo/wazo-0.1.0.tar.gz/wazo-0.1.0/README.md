# WAZO

**The Docker of WebAssembly** — Build any codebase to WASM with zero setup.

[![PyPI version](https://badge.fury.io/py/wazo.svg)](https://badge.fury.io/py/wazo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Why WAZO?

**WAZO** stands for **W**eb**A**ssembly **Z**er**O** setup. The name reflects our core mission: making WebAssembly accessible to everyone by eliminating the traditional complexity of WASM compilation. Just like "Docker" became synonymous with containers, "WAZO" represents the simplicity of universal WASM builds — zero configuration, zero friction, zero barriers to entry.

## Quick Start

```bash
# Install
pip install wazo

# Build any project
cd my-python-project
wazo build .

# Run instantly
wazo run

# Or serve with auto-reload
wazo dev
```

Zero config. One command. Any language.

---

## Why WAZO?

Like Docker standardized containers, WAZO standardizes WebAssembly builds.

| Before WAZO | With WAZO |
|-------------|-----------|
| Install Rust, cargo-component, wasm32 | `wazo build .` |
| Install Node, npm, componentize-js | `wazo build .` |
| Configure WIT files manually | Auto-detected |
| Debug build errors | Clear fixes shown |
| Rebuild on every change | `wazo dev` auto-reloads |

One command. All languages. Zero config.

---

## Commands

### Build
```bash
wazo build .                    # Auto-detect and build
wazo build . --type standalone  # Build standalone binary
wazo build . -o output.wasm     # Custom output
```

### Run
```bash
wazo run                  # Run built component
wazo run -- --arg value   # Pass arguments
```

### Dev Server
```bash
wazo dev                  # Auto-rebuild on changes
wazo dev --port 3000      # Custom port
wazo dev --build-only     # Build mode only
```

Features:
- File watching with auto-rebuild
- HTTP server with hot-reload
- Terminal UI with build stats
- Error recovery

### Test
```bash
wazo test                 # Run component tests
wazo test --watch         # Watch mode
```

### Serve
```bash
wazo serve                # Serve on :8080
wazo serve --port 3000    # Custom port
```

### Init
```bash
wazo init python          # New Python project
wazo init javascript      # New JS project
wazo init rust            # New Rust project
```

---

## Supported Languages

### Python
```bash
cd my-python-project
wazo build .
```

**Requirements**: `pyproject.toml` or `requirements.txt`

### JavaScript/TypeScript
```bash
cd my-js-project
wazo build .
```

**Requirements**: `package.json`

### Rust
```bash
cd my-rust-project
wazo build .
```

**Requirements**: `Cargo.toml` with component metadata

### Go (TinyGo)
```bash
cd my-go-project
wazo build . --type standalone
```

**Requirements**: `go.mod` or `.go` files

### C/C++
```bash
cd my-cpp-project
wazo build . --type standalone
```

**Requirements**: `.c`/`.cpp` files

---

## Installation

```bash
pip install wazo
```

**Requirements:**
- Python 3.8+
- Docker (for builds)

Optional:
- `wasmtime` (for running components)
- `wasm-tools` (for WIT inspection)

---

## Build Caching

Builds are automatically cached based on source file hashes:

```bash
# First build
wazo build .  # ~30 seconds

# No changes - instant cache hit
wazo build .  # <1 second

# Change source - rebuild only
wazo build .  # ~30 seconds
```

Cache is stored in `~/.cache/wazo/builds/`

Disable caching: `wazo build . --no-cache`

---

## File Types

wazo uses clear extensions:

| Extension | Type | Use Case |
|-----------|------|----------|
| `.wasm` | Standalone | CLI tools, executables |
| `.wcmp` | Component | Libraries, composable modules |

**Both types run the same way:**
```bash
wazo run  # Handles both automatically
```

See [docs/STANDALONE_VS_COMPONENT.md](docs/STANDALONE_VS_COMPONENT.md) for details.

---

## Production Features

### Structured Logging
```python
from utils.structured_logger import logger

logger.info("Build started", project="my-app")
```

JSON output for production monitoring.

### Metrics Collection
```python
from utils.structured_logger import metrics

metrics.record_build(success=True, duration=1.5)
stats = metrics.get_metrics()
# Returns: build_success_rate, cache_hit_rate, etc.
```

### Security
- Path validation and sanitization
- Rate limiting for HTTP APIs
- Input validation
- Secure subprocess handling

---

## CI/CD

GitHub Actions workflows included:

- **test.yml**: Multi-platform testing (Ubuntu, macOS, Windows)
- **release.yml**: Automated PyPI publishing with multi-arch wheels

See [.github/workflows/README.md](.github/workflows/README.md) for details.

---

## Development

```bash
# Clone and setup
git clone https://github.com/wazo/wazo.git
cd wazo
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
ruff check src/
black --check src/
```

---

## Architecture

**Build Process:**
1. Detect language from config files
2. Select appropriate builder
3. Build in Docker (cached images)
4. Optimize with wasm-opt
5. Cache result by content hash

**Builders:**
- `PythonWasmBuilder` → componentize-py
- `JavaScriptWasmBuilder` → componentize-js
- `RustWasmBuilder` → cargo-component
- `GoWasmBuilder` → TinyGo
- `CppWasmBuilder` → WASI-SDK

All builders implement the same interface.

---

## Performance

### Build Times

| Language | First Build | Cached |
|----------|-------------|--------|
| Python | 1-2 min | 5-30s |
| JavaScript | 1-2 min | 5-30s |
| Rust | 5-10 min | 5-30s |

First build downloads and caches Docker images. Subsequent builds are much faster.

### Cache Performance
- Cache hit: <1 second
- Cache miss: Normal build time
- Cache storage: `~/.cache/wazo/`

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design
- [API](docs/API.md) - API reference
- [Contributing](docs/CONTRIBUTING.md) - Contribution guide
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues
- [Production Roadmap](docs/PRODUCTION_ROADMAP.md) - Production features

---

## Contributing

Contributions welcome! See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

**Adding a language:**
1. Create builder in `src/engine/builders/`
2. Implement `WasmBuilder` interface
3. Add Dockerfile in `docker/`
4. Update factory and detection logic

---

## License

MIT License - see [LICENSE](LICENSE).
