# per-datasets

A Python package for loading reservoir datasets from API endpoints.

## Installation

```bash
pip install per-datasets
```

## Quick Start

### Option 1: Using Global API Key (Recommended)

First, set your API key globally:

```bash
# Set API key globally (works across all projects)
per-datasets set-key "your_api_key_here"

# Or use interactive setup
per-datasets interactive
```

Then use in your Python code:

```python
import per_datasets as pds

# Initialize without API key (uses global key)
pds.initialize()

# Load a random reservoir dataset
df_random = pds.reservoir.load_random()
print(f"Loaded dataset with shape: {df_random.shape}")
```

### Option 2: Using API Key in Code

```python
import per_datasets as pds

# Initialize with your API key
pds.initialize('your_api_key_here')

# Load a random reservoir dataset
df_random = pds.reservoir.load_random()
print(f"Loaded dataset with shape: {df_random.shape}")
```

## Command Line Interface

The package includes a CLI for managing API keys globally:

```bash
# Set API key globally
per-datasets set-key "your_api_key_here"

# Check configuration status
per-datasets status

# Get stored API key (masked)
per-datasets get-key

# Remove API key
per-datasets remove-key

# Interactive setup
per-datasets interactive

# Clear all configuration
per-datasets clear

# Show help
per-datasets --help
```

## Complete Usage Examples

```
import per_datasets as pds

# Initialize (uses global key if available)
pds.initialize()

# Load a random reservoir dataset
df_random = pds.reservoir.load_random()
print(f"Loaded dataset with shape: {df_random.shape}")

# Load a specific dataset by ID
df_specific = pds.reservoir.load('your_dataset_id')

# Get information about available datasets
info = pds.get_dataset_info()
```

## API Reference

### `initialize(api_key=None)`

Initialize the per_datasets module with API credentials.

**Parameters:**

- `api_key` (str, optional): The API key for authentication. If not provided, uses globally stored key.

**Note:** If no API key is provided and none is stored globally, raises a ValueError with instructions to set a global key.

### `load_random()`

Loads a random reservoir model from the API endpoint and returns as pandas DataFrame.

**Returns:**

- `pandas.DataFrame`: A DataFrame containing the dataset

## Configuration Management

The package stores configuration in `~/.per_datasets/config.json` by default:

```
{
  "api_key": "your_api_key_here"
}
```

### Benefits of Global Configuration:

- ✅ **No API key in code**: Keep sensitive keys out of your source code
- ✅ **Cross-project**: Use the same API key across multiple projects
- ✅ **Secure**: API keys are stored in user's home directory
- ✅ **Override**: Can still provide API key in code to override global setting
- ✅ **Easy management**: Use CLI commands to manage keys

### Security Notes:

- API keys are stored in plain text in your home directory
- Only you can access the configuration file
- Consider using environment variables for production deployments

## Dependencies

- requests>=2.25.1
- pandas>=1.3.0

## License

MIT

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Development

To set up the development environment:

```bash
git clone https://github.com/P-E-R-D/library-py.git
cd per-datasets
pip install -e .
```

## Building and Publishing

### Automatic Deployment (Recommended)

This package uses GitHub Actions for automatic deployment to PyPI:

1. **Make your changes** to the code
2. **Update version numbers** in `per_datasets/__init__.py` and `pyproject.toml`
3. **Create a git tag** with the new version:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. **GitHub Actions automatically** builds and uploads to PyPI!

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup instructions.

### Manual Publishing

```bash
python -m build
twine upload dist/*
```
