# TestIO MCP Server

**AI-first Model Context Protocol server for TestIO Customer API**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.12+-green.svg)](https://github.com/jlowin/fastmcp)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License: Proprietary](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

Query TestIO test status, bugs, and activity metrics through AI tools like Claude and Cursor—no UI required.

> **⚠️ Disclaimer:** This software is provided "AS IS" with no warranty or support obligations. See [License & Disclaimer](#license--disclaimer) for details.

---

## What Is This?

TestIO MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that provides read-only access to the TestIO Customer API. It enables non-developer stakeholders (CSMs, PMs, QA leads) to query test information using natural language through AI assistants like Claude Desktop or Cursor.

**Key Features:**
- 🔍 **9 MCP Tools** - Health check, test status, bug filtering, activity analysis, status reports, cache monitoring
- 🏗️ **Service Layer Architecture** - Framework-agnostic business logic, reusable across transports
- 🔒 **Security-First** - Token sanitization, strict input validation, comprehensive secret scanning
- ⚡ **Performance** - Smart caching (1h/5m/1m TTL), connection pooling, concurrency control
- 📊 **Strict Type Safety** - mypy --strict enforced, Pydantic v2 validation throughout

**Use Cases:**
- **CSMs:** "What's the status of test 109363?" → Get comprehensive test details in seconds
- **TLs:** "Show me critical functional bugs for test 109363" → Filter bugs by type, severity, status
- **CSMs:** "Generate a status report for tests 109363, 109364" → Export markdown/text/json summaries

---

## Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)
- TestIO Customer API token (staging or production)
- Claude Desktop or Cursor (AI client with MCP support)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/test-IO/customer-mcp.git
cd customer-mcp

# 2. Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# 3. Install pre-commit hooks (optional but recommended)
pre-commit install

# 4. Configure API credentials
cp .env.example .env
# Edit .env and set TESTIO_CUSTOMER_API_TOKEN=your-token-here

# 5. Verify installation
uv run pytest -m unit  # Run fast unit tests (no API needed)
uv run python -m testio_mcp  # Start the MCP server (should initialize successfully)
```

### MCP Client Configuration

All MCP clients use the same basic configuration format:

```json
{
  "mcpServers": {
    "testio-mcp": {
      "command": "/absolute/path/to/customer-mcp/.venv/bin/python",
      "args": ["-m", "testio_mcp"]
    }
  }
}
```

**Supported Clients:**
- **Claude Code (CLI)** - `~/.config/claude/code_config.json`
- **Claude Desktop** - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Cursor** - `~/.cursor/mcp.json` or `.cursor/mcp.json`
- **Gemini** - CLI: `gemini mcp add testio-mcp /path/to/python -m testio_mcp`
- **Codex** - `~/.codex/config.toml` (TOML syntax)

**📖 For detailed setup instructions by client, see [MCP_SETUP.md](MCP_SETUP.md)**

### First Query

Restart Claude Desktop or Cursor, then try:

```
What's the status of test 109363?
```

You should see comprehensive test details including title, status, timeline, and bug summary.

---

## Features & API Reference

### Available Tools

| Tool | Description | Key Parameters | Example Query |
|------|-------------|----------------|---------------|
| **health_check** | Verify API authentication | None | "Check TestIO API health" |
| **get_test_status** | Get comprehensive test status | `test_id` (int) | "What's the status of test 109363?" |
| **list_tests** | List tests for a product | `product_id` (int), `statuses` (optional), `include_bug_counts` (bool) | "Show me all active tests for product 25073" |
| **list_products** | List available products | `search` (optional), `product_type` (optional) | "List all products" or "Find products with 'mobile' in name" |
| **get_test_bugs** | Filter bugs by type/severity/status | `test_id` (str), `bug_type`, `severity`, `status`, `page_size`, `continuation_token` | "Show me critical functional bugs for test 109363" |
| **generate_status_report** | Generate executive summaries | `test_ids` (list[str]), `format` (markdown/text/json) | "Generate a status report for tests 109363, 109364 in markdown" |
| **get_test_activity_by_timeframe** | Analyze activity across products | `product_ids` (list[str]), `start_date`, `end_date`, `date_field`, `include_bugs` | "Show test activity for product 25073 from 2024-10-01 to 2024-12-31" |
| **get_cache_stats** | Monitor cache performance metrics | None | "Show me cache statistics" or "What's the cache hit rate?" |
| **clear_cache** | Clear all cached data (admin tool) | None | "Clear the cache" or "Force refresh all data" |

### Performance Characteristics

- **Caching:** Smart TTL-based caching reduces API load
  - Products: 1 hour
  - Tests: 5 minutes
  - Bugs: 1 minute
- **Concurrency:** Max 10 concurrent API requests (configurable)
- **Response Times:** <5 seconds for 99% of queries
- **Connection Pooling:** Max 100 connections, 20 keep-alive

---

## Architecture Overview

TestIO MCP Server follows a **service layer architecture** that separates business logic from transport mechanisms:

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Tools (Thin Wrappers)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │health_   │ │get_test_ │ │list_     │ │get_test_ │  ...   │
│  │check     │ │status    │ │tests     │ │bugs      │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │            │            │            │              │
│       └────────────┴────────────┴────────────┘              │
│                          │                                  │
│            Extract deps, delegate, convert errors           │
│                          ▼                                  │
└─────────────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│              Service Layer (Business Logic)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │Test      │ │Bug       │ │Product   │ │Activity  │  ...   │
│  │Service   │ │Service   │ │Service   │ │Service   │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │            │            │            │              │
│       └────────────┴────────────┴────────────┘              │
│                          │                                  │
│       Domain operations, caching, orchestration             │
│                          ▼                                  │
└─────────────────────────────────────────────────────────────┘
                           │
┌────────────────────────────────────────────────────────────┐
│              Infrastructure (HTTP & Cache)                 │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │  TestIOClient       │  │  InMemoryCache      │          │
│  │  (httpx wrapper)    │  │  (TTL-based)        │          │
│  │  - Connection pool  │  │  - 1h/5m/1m TTL     │          │
│  │  - Concurrency      │  │  - Auto-expiration  │          │
│  │  - Token sanitize   │  │                     │          │
│  └──────────┬──────────┘  └─────────────────────┘          │
│             │                                              │
│             ▼                                              │
└────────────────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                  TestIO Customer API                         │
│              https://api.test.io/customer/v2                 │
└──────────────────────────────────────────────────────────────┘
```

**Key Architectural Decisions:**

- **Service Layer Pattern (ADR-006):** Business logic is framework-agnostic and can be reused across REST APIs, CLIs, or webhooks
- **FastMCP Context Injection (ADR-007):** Shared resources (client, cache) initialized via lifespan handler, injected into tools via context
- **Strict Type Safety:** mypy --strict enforced, Pydantic v2 for validation and schema generation
- **Security (SEC-002):** API tokens never appear in logs or error messages, event hooks sanitize httpx logging
- **Concurrency Control (ADR-002):** Global semaphore limits concurrent API requests to prevent rate limiting

**Technologies:**

- [FastMCP](https://github.com/jlowin/fastmcp) - Pythonic MCP framework with decorator-based API
- [Pydantic v2](https://docs.pydantic.dev/latest/) - Runtime validation with JSON Schema generation
- [httpx](https://www.python-httpx.org/) - Modern async HTTP client with connection pooling
- [mypy](http://mypy-lang.org/) - Static type checker in strict mode

For deep dive into architecture, see [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md).

---

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### Architecture & Design
- [ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md) - System architecture, data flow, testing strategy
- [SERVICE_LAYER_SUMMARY.md](docs/architecture/SERVICE_LAYER_SUMMARY.md) - Service pattern details
- [SECURITY.md](docs/architecture/SECURITY.md) - Security considerations and token sanitization
- [PERFORMANCE.md](docs/architecture/PERFORMANCE.md) - Performance targets and optimization strategies
- [adrs/](docs/architecture/adrs/) - Architecture Decision Records (7 ADRs covering key technical decisions)

### Development
- [CLAUDE.md](CLAUDE.md) - Comprehensive development guide for contributors
  - Development commands (testing, code quality, running server)
  - Architecture patterns (service layer, dependency injection)
  - Adding new tools (step-by-step guide)
  - Common pitfalls and best practices

### Project Planning
- [stories/](docs/stories/) - User story specifications with acceptance criteria (Stories 1-13)
- [epics/](docs/epics/) - Epic specifications
- [project-brief.md](docs/project-brief.md) - Original project vision and use cases

### Contributing Guide (Coming in v0.4.0)

The contributor guide for adding new tools will be enhanced after **Stories 012-013** are completed (~12.5 hours). These stories introduce:

- `BaseService` class for reducing boilerplate (~40% code reduction)
- `get_service()` helper for simplified tool creation
- FastMCP `ToolError` exception pattern

Until then, refer to [CLAUDE.md](CLAUDE.md) for current development patterns.

---

## Project Status

**Current Version:** v0.3.0 (Alpha)

**MVP Complete:**
- ✅ 7 MCP tools with comprehensive documentation
- ✅ Service layer architecture (framework-agnostic business logic)
- ✅ Strict type safety (mypy --strict, Pydantic v2)
- ✅ Security (token sanitization, secret scanning)
- ✅ Testing (~130 tests: unit, service, integration)
- ✅ Pre-commit hooks (ruff, mypy, detect-secrets)

**Pending (v0.4.0 - ~12.5 hours):**
- ⏳ **Story 012:** Extensibility Infrastructure
  - `BaseService` class for DI and caching patterns
  - `get_service()` context extraction helper
  - FastMCP `ToolError` adoption
  - Auto-discovery of tools via `pkgutil`
  - **Impact:** ~220-250 lines removed (~25% reduction in boilerplate)
- ⏳ **Story 013:** Usability Enhancements
  - Natural language date parsing ("last 30 days", "this quarter")
  - Filter validation with Pydantic enums
  - `get_valid_bug_filters` discovery tool
  - **Impact:** Improved UX for date-based queries

**Breaking Changes in v0.4.0:**

⚠️ **BREAKING:** `list_tests` default behavior changes:
- **Before (v0.3.0):** Default returns only `running` tests
- **After (v0.4.0):** Default returns ALL tests (no filtering)

See [CHANGELOG.md](CHANGELOG.md) for full version history.

**Roadmap:**

- v0.4.0: Extensibility & usability improvements (Stories 012-013)
- v0.5.0: Write operations (create tests, accept/reject bugs) - requires authentication strategy
- v0.6.0: Multi-tenant support (per-request tokens) - requires HTTP transport refactoring

---

## Development

### Running Tests

```bash
# Run all tests (unit + integration with API token)
uv run pytest

# Run specific test types
uv run pytest -m unit              # Fast unit tests (no API needed)
uv run pytest -m integration       # Integration tests (requires API credentials)

# Run with coverage
uv run pytest --cov=src/testio_mcp --cov-report=html
```

**Integration Tests:**

Some integration tests require `TESTIO_TEST_ID` environment variable for positive test cases:

```bash
export TESTIO_TEST_ID=109363  # Use a valid test ID from your account
uv run pytest -m integration
```

### Code Quality

```bash
# Run linter (auto-fix)
uv run ruff check --fix

# Run formatter
uv run ruff format

# Run type checker
uv run mypy src/testio_mcp

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Testing Tools via MCP Inspector

```bash
# List available tools
npx @modelcontextprotocol/inspector --cli uv run python -m testio_mcp --method tools/list

# Test health_check (no parameters)
npx @modelcontextprotocol/inspector --cli uv run python -m testio_mcp --method tools/call --tool-name health_check

# Test get_test_status (with parameter)
npx @modelcontextprotocol/inspector --cli uv run python -m testio_mcp --method tools/call --tool-name get_test_status --tool-arg 'test_id=109363'

# Interactive mode (opens web UI at localhost:6274)
npx @modelcontextprotocol/inspector uv run python -m testio_mcp
```

**Important:** Integer parameters must be passed as integers, not quoted strings.

For detailed development workflows, see [CLAUDE.md](CLAUDE.md).

---

## License & Disclaimer

**License:** Proprietary (see [LICENSE](LICENSE))

This software is provided by TestIO for use "AS IS" without warranty of any kind. By using this software, you agree to the following terms:

- ✅ **Free to Use:** Personal and commercial use permitted
- ❌ **No Warranty:** No guarantees of fitness, reliability, or accuracy
- ❌ **No Liability:** TestIO is not liable for any damages or issues arising from use
- ❌ **No Support:** TestIO has no obligation to provide support, updates, or bug fixes
- ❌ **No Modification/Redistribution:** You may not modify, adapt, or redistribute this software

For complete license terms, see the [LICENSE](LICENSE) file.

---

## Configuration

All configuration via environment variables in `.env` file:

```bash
# Required
TESTIO_CUSTOMER_API_TOKEN=your-token-here
TESTIO_CUSTOMER_API_BASE_URL=https://api.test.io/customer/v2

# Optional (defaults shown)
MAX_CONCURRENT_API_REQUESTS=10
CONNECTION_POOL_SIZE=100
CONNECTION_POOL_MAX_KEEPALIVE=20
HTTP_TIMEOUT_SECONDS=30
LOG_LEVEL=INFO
LOG_FORMAT=text  # or "json"

# Tool Control (optional)
ENABLED_TOOLS=health_check,list_products  # Allowlist: only these tools available
DISABLED_TOOLS=generate_status_report     # Denylist: all except these tools
# Note: Cannot use both ENABLED_TOOLS and DISABLED_TOOLS simultaneously
```

### Tool Enable/Disable

Control which MCP tools are available by using environment variables:

**Allowlist mode (ENABLED_TOOLS):**
```bash
# Only enable specific tools (all others disabled)
ENABLED_TOOLS=health_check,list_products,get_test_status
```

**Denylist mode (DISABLED_TOOLS):**
```bash
# Disable specific tools (all others enabled)
DISABLED_TOOLS=generate_status_report,get_test_activity_by_timeframe
```

**Available tool names:**
- `health_check` - Verify API authentication
- `get_cache_stats` - Cache performance metrics
- `clear_cache` - Clear cached data
- `list_products` - List all products
- `list_tests` - List tests for a product
- `get_test_status` - Get test status details
- `get_test_bugs` - Get bug details with filtering
- `generate_status_report` - Generate executive summary
- `get_test_activity_by_timeframe` - Query test activity by date range

**Format options:**
- Comma-separated: `ENABLED_TOOLS=tool1,tool2,tool3`
- JSON array: `ENABLED_TOOLS='["tool1", "tool2", "tool3"]'`

**Use cases:**
- **CSM workflow:** `ENABLED_TOOLS=health_check,get_test_status,list_tests`
- **QA workflow:** `ENABLED_TOOLS=get_test_bugs,generate_status_report,list_tests`
- **Minimal setup:** `DISABLED_TOOLS=generate_status_report,get_test_activity_by_timeframe`

See [.env.example](.env.example) for complete configuration options.

---
