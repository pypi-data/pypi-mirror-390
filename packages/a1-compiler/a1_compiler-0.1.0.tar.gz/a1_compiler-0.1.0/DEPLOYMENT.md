# PyPI Deployment Guide for a1

## Current Status

The `a1` package has been successfully built and is ready for deployment to PyPI.

### Built Artifacts

- **Wheel**: `dist/a1-0.1.0-py3-none-any.whl` (69 KB)
- **Source Distribution**: `dist/a1-0.1.0.tar.gz` (219 KB)

## Option 1: Manual Upload via Web Interface

1. Go to https://pypi.org/account/
2. Sign in with your PyPI account
3. Go to https://pypi.org/account/repositories/
4. Click on your project "a1" 
5. Click "Upload files"
6. Select and upload both `dist/a1-0.1.0-py3-none-any.whl` and `dist/a1-0.1.0.tar.gz`

## Option 2: Using twine (Recommended)

```bash
# Install twine if not already installed
pip install twine

# Upload to PyPI
twine upload dist/a1-0.1.0-py3-none-any.whl dist/a1-0.1.0.tar.gz

# You'll be prompted for your PyPI credentials
# Username: __token__
# Password: <your PyPI token>
```

## Option 3: Using uv with Valid Token

```bash
# Export the token and publish
export UV_PUBLISH_TOKEN="<your-pypi-token>"
uv publish
```

## Verifying Installation

After publishing, verify the package can be installed:

```bash
# Install from PyPI
pip install a1

# Verify import
python -c "import a1; print(a1.__version__)"
```

## Package Information

**Project Name**: a1  
**Version**: 0.1.0  
**Author**: Caleb Winston  
**License**: Apache 2.0  

**Description**: A modern agent compiler for building and executing LLM-powered agents

**Key Features**:
- Tool composition with Pydantic schemas
- AOT/JIT code generation
- RAG toolsets (FileSystem, SQL)
- OpenTelemetry integration
- LangChain compatibility
- SmartRAG for unified data access

## After Publication

1. The package will be available at https://pypi.org/project/a1/
2. Users can install with: `pip install a1`
3. The package documentation will be available on the PyPI page

## Next Steps

- Set up GitHub Actions for automated PyPI publishing on releases
- Create GitHub releases with version tags
- Set up a Trusted Publisher on PyPI for GitHub Actions
