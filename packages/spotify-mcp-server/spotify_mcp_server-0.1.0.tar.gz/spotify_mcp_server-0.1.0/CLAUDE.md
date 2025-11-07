# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that provides Spotify integration. The server exposes Spotify API functionality as MCP tools, allowing AI assistants to search artists, manage playlists, get album information, and access user data.

## Development Commands

### Running the Server

```bash
# Development mode with MCP inspector (recommended for testing)
mcp dev spotify_mcp_server.py

# Run directly
python spotify_mcp_server.py
```

### Package Management

This project uses `uv` for dependency management:

```bash
# Install dependencies
uv sync

# Add new dependency
uv add <package-name>
```

### Authentication

The server uses Spotify OAuth with credentials stored in `.env`:
- First run opens browser for authentication
- Token cached in `.spotify_cache`
- Clear cache file if encountering token issues

### Claude Desktop Configuration

#### For Development (Local Repository)

Add to your config file at `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "Spotify": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/nir.l/vsProjects/mcpCourse/spotify-mcp/",
        "mcp",
        "run",
        "spotify_mcp_server.py"
      ]
    }
  }
}
```

#### For Production (Published to PyPI)

Once published to PyPI, users can use `uvx` without cloning:

```json
{
  "mcpServers": {
    "Spotify": {
      "command": "uvx",
      "args": ["spotify-mcp-server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id",
        "SPOTIFY_CLIENT_SECRET": "your_client_secret",
        "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback"
      }
    }
  }
}
```

Note: When distributed via PyPI, users must provide their own Spotify API credentials in the config.

## Architecture

### Core Components

**spotify_mcp_server.py** - Main server file that:
- Initializes Spotify client with OAuth (SpotifyOAuth)
- Registers MCP tools using FastMCP
- Creates async wrapper functions that delegate to tool modules
- Requires scope: `playlist-modify-public playlist-modify-private user-library-read user-read-private user-top-read`

**mcp_tools/** - Tool modules organized by domain:
- `artist_tools.py` - Artist search, details, albums, top tracks
- `playlist_tools.py` - Create playlists, add tracks, get user playlists
- `albums.py` - Album details, tracks, new releases
- `user_tools.py` - User's top artists and tracks
- `__init__.py` - Exports all tools and Pydantic models

### Tool Pattern

Each tool module follows this pattern:

1. Define Pydantic models for complex request parameters
2. Implement async tool functions that:
   - Accept `spotify_client` as first parameter
   - Take request models or simple parameters
   - Return `Dict[str, Any]` with consistent structure:
     - `success: bool`
     - `message: str`
     - Result data (artists, playlists, etc.)
     - `error: str` if failed
3. Include detailed docstrings describing arguments and returns

In the main server:
- Create async wrapper functions that preserve names and docstrings
- Register wrappers with FastMCP using `app.tool()(function_name)`

### Adding New Tools

1. Add tool function to appropriate module in `mcp_tools/`
2. Export from `mcp_tools/__init__.py`
3. Import in `spotify_mcp_server.py`
4. Create wrapper function that calls the tool
5. Copy docstring: `wrapper.__doc__ = tool_function.__doc__`
6. Register: `app.tool()(wrapper)`

## Spotify API Integration

The codebase uses the `spotipy` library. Key integration points:

- OAuth flow handles authentication automatically
- Rate limits are managed by Spotify API (errors logged)
- All functions include try/except with error logging
- Market/country codes default to "US" for region-specific content
- Track URIs use format: `spotify:track:{track_id}`

## Environment Configuration

Required `.env` variables:
- `SPOTIFY_CLIENT_ID` - From Spotify Developer Dashboard
- `SPOTIFY_CLIENT_SECRET` - From Spotify Developer Dashboard
- `SPOTIFY_REDIRECT_URI` - Default: `http://localhost:8888/callback`

Redirect URI must be registered in Spotify app settings.

## Distribution

### Publishing to PyPI

See `PUBLISHING.md` for complete publishing guide. Quick steps:

1. Update version in `pyproject.toml`
2. Build: `uv build`
3. Publish: `python -m twine upload dist/*`

### Package Entry Point

The package defines a console script entry point:
- Script name: `spotify-mcp-server`
- Entry function: `spotify_mcp_server:main`
- Users run via: `uvx spotify-mcp-server`
