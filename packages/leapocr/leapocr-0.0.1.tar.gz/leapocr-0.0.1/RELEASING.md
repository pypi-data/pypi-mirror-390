# Release Process

This document describes how to release a new version of the LeapOCR Python SDK.

## Prerequisites

1. You have write access to the repository
2. You're on the `main` branch with all changes merged
3. All CI checks are passing
4. You have PyPI publishing access (or using trusted publishing)

## Release Steps

### 1. Update Version

Update the version in `pyproject.toml`:

```toml
[project]
version = "X.Y.Z"  # Update this
```

### 2. Update Changelog

Update `CHANGELOG.md`:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New feature A
- New feature B

### Changed
- Changed behavior of X

### Fixed
- Fixed bug in Y
```

### 3. Commit Changes

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

### 4. Create and Push Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release version X.Y.Z"

# Push tag to trigger release workflow
git push origin vX.Y.Z
```

### 5. Monitor Release

The GitHub Actions workflow will automatically:

1. **Build** the distribution packages (wheel and sdist)
2. **Verify** the version matches the tag
3. **Publish** to PyPI using trusted publishing
4. **Create** a GitHub release with auto-generated notes

Monitor the workflow at:
https://github.com/leapocr/leapocr-python/actions/workflows/release.yml

### 6. Verify Release

After the workflow completes:

1. **Check PyPI**: https://pypi.org/project/leapocr/
2. **Check GitHub Release**: https://github.com/leapocr/leapocr-python/releases
3. **Test installation**:
   ```bash
   pip install leapocr==X.Y.Z
   python -c "import leapocr; print(leapocr.__version__)"
   ```

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Incompatible API changes
- **MINOR** (0.Y.0): New functionality, backwards compatible
- **PATCH** (0.0.Z): Bug fixes, backwards compatible

### Examples

- `0.1.0` → `0.1.1`: Bug fix
- `0.1.0` → `0.2.0`: New feature
- `0.9.0` → `1.0.0`: Breaking change / stable API

## PyPI Trusted Publishing Setup

This project uses PyPI's trusted publishing (no API tokens needed).

### First-Time Setup

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **PyPI Project Name**: `leapocr`
   - **Owner**: `leapocr`
   - **Repository**: `leapocr-python`
   - **Workflow**: `release.yml`
   - **Environment**: `pypi`

3. The workflow will automatically publish when a tag is pushed

## Troubleshooting

### Version Mismatch Error

If you see "Tag version does not match package version":

1. Check `pyproject.toml` has the correct version
2. Ensure the tag format is `vX.Y.Z` (with 'v' prefix)
3. Delete and recreate the tag if needed:
   ```bash
   git tag -d vX.Y.Z
   git push origin :refs/tags/vX.Y.Z
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

### Build Failure

If the build fails:

1. Run locally: `uv build`
2. Check for import errors or missing files
3. Verify `pyproject.toml` is correct
4. Ensure all dependencies are specified

### Publish Failure

If PyPI publish fails:

1. Check PyPI trusted publishing is configured
2. Verify the workflow has `id-token: write` permission
3. Ensure the version doesn't already exist on PyPI
4. Check PyPI status: https://status.python.org/

### Manual Release (Emergency)

If automated release fails, you can publish manually:

```bash
# Build locally
uv build

# Publish with twine (requires PyPI API token)
uv run twine upload dist/*
```

## Post-Release

After a successful release:

1. **Announce** the release (if major/minor version):
   - Update documentation site
   - Post on social media
   - Email users (if applicable)

2. **Update** `main` branch:
   - Bump version to next dev version in `pyproject.toml`
   - Add `[Unreleased]` section to `CHANGELOG.md`

3. **Monitor** for issues:
   - Watch GitHub issues
   - Check PyPI download stats
   - Monitor error tracking (if configured)

## Release Checklist

Use this checklist for each release:

- [ ] All tests passing on `main`
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with changes
- [ ] Commit and push version bump
- [ ] Create and push git tag `vX.Y.Z`
- [ ] Monitor GitHub Actions workflow
- [ ] Verify package on PyPI
- [ ] Verify GitHub release created
- [ ] Test installation from PyPI
- [ ] Announce release (if major/minor)
- [ ] Update documentation (if needed)
