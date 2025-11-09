# Publishing Guide for allmark

This guide explains how to publish new versions of `allmark` to PyPI.

## Prerequisites

Before publishing, ensure you have:

1. **GitHub Repository Setup**
   - Repository: `https://github.com/dcondrey/allmark`
   - Workflows in `.github/workflows/` are committed

2. **PyPI Trusted Publishing Setup**

   You need to configure PyPI's trusted publisher feature:

   a. Go to https://pypi.org/manage/account/publishing/

   b. Add a new trusted publisher with these settings:
      - **PyPI Project Name**: `allmark`
      - **Owner**: `dcondrey`
      - **Repository name**: `allmark`
      - **Workflow name**: `publish.yml`
      - **Environment name**: `pypi`

   c. (Optional) For TestPyPI, go to https://test.pypi.org/manage/account/publishing/ and add:
      - **PyPI Project Name**: `allmark`
      - **Owner**: `dcondrey`
      - **Repository name**: `allmark`
      - **Workflow name**: `publish.yml`
      - **Environment name**: `testpypi`

3. **GitHub Environments**

   Configure repository environments (Settings → Environments):

   a. Create environment named `pypi`:
      - (Optional) Add protection rules
      - (Optional) Add required reviewers

   b. Create environment named `testpypi` (optional for testing)

## Publishing Process

### Automated Publishing via GitHub Releases (Recommended)

1. **Update Version Number**

   Edit `pyproject.toml`:
   ```toml
   [project]
   name = "allmark"
   version = "0.5.0"  # Update this
   ```

2. **Commit and Push Changes**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.5.0"
   git push origin master
   ```

3. **Create a Git Tag**
   ```bash
   git tag -a v0.5.0 -m "Release version 0.5.0"
   git push origin v0.5.0
   ```

4. **Create a GitHub Release**

   Go to: https://github.com/dcondrey/allmark/releases/new

   - **Tag**: Select `v0.5.0` (or create new tag)
   - **Release title**: `v0.5.0`
   - **Description**: Add changelog/release notes
   - Click "Publish release"

   The GitHub Action will automatically:
   - Build the distribution packages
   - Publish to TestPyPI (optional)
   - Publish to PyPI

5. **Verify Publication**

   Check that the package is live:
   - PyPI: https://pypi.org/project/allmark/
   - TestPyPI: https://test.pypi.org/project/allmark/

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backwards compatible
- **PATCH** version (0.0.X): Bug fixes, backwards compatible

## Pre-Release Checklist

Before publishing a new version:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Update `README.md` if needed
- [ ] Run tests locally
- [ ] Test installation: `pip install -e .`
- [ ] Test CLI: `allmark --help`
- [ ] Commit all changes
- [ ] Create git tag
- [ ] Push tag to GitHub
- [ ] Create GitHub release

## Troubleshooting

### Workflow Fails with "Permission Denied"

- Verify PyPI trusted publishing is configured correctly
- Check that the environment name matches (`pypi` or `testpypi`)
- Ensure workflow has `id-token: write` permission

### Package Already Exists Error

- You cannot re-upload the same version to PyPI
- Bump the version number in `pyproject.toml`
- Create a new tag and release

### Workflow Doesn't Trigger

- Verify `.github/workflows/publish.yml` is on the master branch
- Check workflow is enabled in repository settings
- Ensure you created a "Release" not just a tag
