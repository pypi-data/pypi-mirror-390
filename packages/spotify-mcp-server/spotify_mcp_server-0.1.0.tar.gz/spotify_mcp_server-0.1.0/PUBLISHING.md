# Publishing to PyPI

This guide explains how to publish the Spotify MCP server to PyPI so users can use it without cloning the repository.

## Prerequisites

1. Python 3.10 or higher
2. Create a PyPI account at https://pypi.org/account/register/
3. Set up API token at https://pypi.org/manage/account/token/
4. Install build tools: `uv add --dev build twine`

## Update Before Publishing

1. **Update version** in `pyproject.toml` for new releases:
   ```toml
   version = "0.1.1"  # Increment as needed
   ```

3. **Ensure .env is in .gitignore** (credentials should never be published)

## Publishing Steps

### 1. Clean Previous Builds
```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Build the Package
```bash
uv build
# or
python -m build
```

This creates files in `dist/`:
- `spotify-mcp-0.1.0.tar.gz` (source distribution)
- `spotify_mcp-0.1.0-py3-none-any.whl` (wheel)

### 3. Test with TestPyPI (Optional but Recommended)
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
uvx --index-url https://test.pypi.org/simple/ spotify-mcp-server
```

### 4. Publish to PyPI
```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI credentials or API token.

### 5. Verify Publication
```bash
# Test that it works
uvx spotify-mcp-server --help
```

## User Installation & Usage

Once published, users can add to their Claude Desktop config without cloning:

**~/.config/Claude/claude_desktop_config.json** (Linux)
**~/Library/Application Support/Claude/claude_desktop_config.json** (macOS)

```json
{
  "mcpServers": {
    "Spotify": {
      "command": "uvx",
      "args": ["spotify-mcp-server"],
      "env": {
        "SPOTIFY_CLIENT_ID": "user_client_id_here",
        "SPOTIFY_CLIENT_SECRET": "user_client_secret_here",
        "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback"
      }
    }
  }
}
```

Note: Users must provide their own Spotify API credentials in the config.

## Version Management

Follow semantic versioning:
- **0.1.0** → **0.1.1**: Bug fixes
- **0.1.0** → **0.2.0**: New features (backward compatible)
- **0.1.0** → **1.0.0**: Breaking changes

Update version in `pyproject.toml` before each release.

## Automation (Optional)

Consider setting up GitHub Actions to automate releases:

1. Tag a release on GitHub: `git tag v0.1.0 && git push --tags`
2. GitHub Action builds and publishes to PyPI automatically

## Troubleshooting

**"Package already exists"**: You can't overwrite existing versions. Increment version number.

**Authentication fails**: Use API token instead of password. Create at https://pypi.org/manage/account/token/

**Import errors after install**: Ensure all dependencies are in `pyproject.toml` dependencies.
