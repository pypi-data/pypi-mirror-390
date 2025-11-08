# PyPI Trusted Publishing Setup

This project uses PyPI's trusted publishing feature to securely publish releases without needing API tokens.

## Initial Setup (One-Time)

### 1. Register the Package on PyPI (if not already registered)

If this is the first release:

1. Build the package locally:
   ```bash
   uv build
   ```

2. Manually upload the first version using an API token:
   ```bash
   # Create a PyPI API token at: https://pypi.org/manage/account/token/
   uv run twine upload dist/*
   ```

### 2. Configure Trusted Publishing

1. Go to https://pypi.org/manage/project/leapocr/settings/publishing/

2. Scroll to "Publishing" section

3. Click "Add a new pending publisher"

4. Fill in the form:
   - **PyPI Project Name**: `leapocr`
   - **Owner**: `leapocr` (GitHub organization/user)
   - **Repository name**: `leapocr-python`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

5. Click "Add"

### 3. Create PyPI Environment in GitHub

1. Go to https://github.com/leapocr/leapocr-python/settings/environments

2. Click "New environment"

3. Name it `pypi`

4. (Optional) Add protection rules:
   - Required reviewers (for manual approval before publish)
   - Deployment branches (limit to `main` branch only)

5. Click "Configure environment"

## How It Works

1. When you push a tag like `v0.1.0`:
   ```bash
   git tag -a v0.1.0 -m "Release v0.1.0"
   git push origin v0.1.0
   ```

2. GitHub Actions workflow triggers (`release.yml`)

3. The workflow:
   - Builds the package
   - Requests a short-lived token from PyPI via OIDC
   - Uses that token to publish to PyPI
   - Creates a GitHub release

4. No API tokens needed! ✨

## Security Benefits

- **No long-lived tokens**: Tokens are generated per-release
- **Scoped access**: Token only works for this specific project
- **Audit trail**: All releases tracked in GitHub Actions
- **Revocable**: Can be disabled/reconfigured at any time

## Troubleshooting

### Error: "Trusted publisher configuration does not match"

This usually means:
- The repository name is wrong
- The workflow name doesn't match (`release.yml`)
- The environment name doesn't match (`pypi`)
- The tag trigger isn't configured correctly

**Solution**: Double-check the PyPI publisher settings match your GitHub repository exactly.

### Error: "Insufficient permissions"

The workflow needs `id-token: write` permission:

```yaml
permissions:
  contents: read
  id-token: write  # Required for trusted publishing
```

This is already configured in `release.yml`.

### Error: "Package already exists"

If you're trying to upload a version that already exists on PyPI:

1. Bump the version in `pyproject.toml`
2. Create a new tag with the new version
3. Delete the old tag if needed:
   ```bash
   git tag -d v0.1.0
   git push origin :refs/tags/v0.1.0
   ```

## Testing Releases

To test the release process without publishing to PyPI:

1. Use TestPyPI for testing:
   - Configure a separate trusted publisher on TestPyPI
   - Create a test workflow that publishes to TestPyPI
   - Test with: `pip install -i https://test.pypi.org/simple/ leapocr`

2. Or run the build locally:
   ```bash
   make build
   # Check the dist/ folder
   ls -lh dist/
   ```

## References

- [PyPI Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [PyPA gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish)
