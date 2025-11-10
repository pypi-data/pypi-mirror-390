# Release Process

## Setup (One-time)

### Configure PyPI Trusted Publishing

This project uses PyPI's [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) for secure, token-free publishing from GitHub Actions.

1. **Create a PyPI account** if you don't have one: https://pypi.org/account/register/

2. **Add GitHub as a Trusted Publisher:**
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in:
     - **PyPI Project Name:** `devnarrate`
     - **Owner:** ``
     - **Repository:** `DevNarrate`
     - **Workflow name:** `publish.yml`
     - **Environment name:** `pypi`
   - Click "Add"

3. **Done!** No API tokens needed. GitHub Actions will automatically authenticate using OIDC.

## Making a Release

### 1. Update Version

Edit [`pyproject.toml`](pyproject.toml) and update the version:

**For pre-releases:**
- Alpha: `0.1.0a1`, `0.1.0a2`, etc.
- Beta: `0.1.0b1`, `0.1.0b2`, etc.
- Release Candidate: `0.1.0rc1`, `0.1.0rc2`, etc.

**For stable releases:**
- Stable: `0.1.0`, `0.2.0`, `1.0.0`, etc.

### 2. Commit and Push

```bash
git add pyproject.toml
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

### 3. Create and Push Tag

```bash
# For pre-release (e.g., 0.1.0a1)
git tag v0.1.0a1
git push origin v0.1.0a1

# For stable release (e.g., 0.1.0)
git tag v0.1.0
git push origin v0.1.0
```

### 4. GitHub Actions Does the Rest

The workflow will automatically:
1. Build the package
2. Publish to PyPI
3. Create a GitHub Release
4. Sign artifacts with Sigstore

### 5. Verify

Check that the release is live:
- PyPI: https://pypi.org/project/devnarrate/
- GitHub Releases: https://github.com/krishnamandanapu/DevNarrate/releases

## Version Numbering

We follow [PEP 440](https://peps.python.org/pep-0440/) versioning:

- **Pre-releases:** `X.Y.ZaN` (alpha), `X.Y.ZbN` (beta), `X.Y.ZrcN` (release candidate)
- **Stable releases:** `X.Y.Z`

Examples:
- `0.1.0a1` - First alpha of version 0.1.0
- `0.1.0b1` - First beta of version 0.1.0
- `0.1.0rc1` - First release candidate of version 0.1.0
- `0.1.0` - Stable release

Users can install pre-releases with:
```bash
pip install --pre devnarrate
```

Or pin to a specific pre-release:
```bash
pip install devnarrate==0.1.0a1
```

## Testing Before Release

To test the package locally before releasing:

```bash
# Build
uv run pyproject-build

# Test installation in a clean environment
cd /tmp
python -m venv test-env
source test-env/bin/activate
pip install /path/to/DevNarrate/dist/devnarrate-X.Y.Z-py3-none-any.whl

# Test the package
python -m devnarrate.server
```

## Troubleshooting

**Error: "Project name 'devnarrate' does not exist"**
- The first time you publish, the PyPI Trusted Publisher must be configured as a "pending publisher" before the project exists
- Follow the setup instructions above

**Error: "OIDC token verification failed"**
- Check that the repository, workflow name, and environment name match exactly in PyPI settings
- Ensure the workflow has `id-token: write` permission

**Error: "Version X.Y.Z already exists"**
- PyPI does not allow re-uploading the same version
- Increment the version number and create a new tag
