# Distribution Guide

Complete guide for distributing `allmark` across different package managers.

## Package Manager Overview

| Package Manager | Repository | Installation Command | Auto-Update |
|----------------|------------|---------------------|-------------|
| **pip** | PyPI | `pip install allmark` | ✅ Yes (GitHub Actions) |
| **poetry** | PyPI | `poetry add allmark` | ✅ Yes (same as pip) |
| **conda** | conda-forge | `conda install -c conda-forge allmark` | ⚠️ Semi-automated |
| **pipx** | PyPI | `pipx install allmark` | ✅ Yes (same as pip) |

## Publishing Priority

Recommended order for publishing:

1. **PyPI** (via GitHub Actions) - AUTOMATED ✅
2. **conda-forge** - Manual submission, then automated updates
3. **Homebrew** (optional) - For macOS users
4. **Docker** (optional) - For containerized deployments

## 1. PyPI Publishing (Already Set Up!)

**Status**: ✅ Automated via GitHub Actions

**How it works**:
- Create a GitHub Release
- GitHub Actions automatically builds and publishes to PyPI
- Available to pip, poetry, pipx users immediately

**Documentation**: See [PUBLISHING.md](PUBLISHING.md)

**Users can install with**:
```bash
# Using pip
pip install allmark

# Using poetry
poetry add allmark

# Using pipx (for CLI tools)
pipx install allmark
```

## 2. conda-forge Publishing

**Status**: ⏳ Needs initial setup (one-time review process)

**How it works**:
1. Submit recipe to conda-forge (one-time, 1-7 day review)
2. After approval, updates are mostly automated
3. Bot watches PyPI and creates update PRs automatically

**Documentation**: See [CONDA_PUBLISHING.md](CONDA_PUBLISHING.md)

**Timeline**:
- Initial submission: 1-7 days for review
- Updates: Usually automated within 24 hours of PyPI release

**Users can install with**:
```bash
# Using conda
conda install -c conda-forge allmark

# Using mamba (faster)
mamba install -c conda-forge allmark
```

## 3. Homebrew Publishing (Optional)

**Status**: ⏳ Not yet set up

Homebrew is popular on macOS. If you want to support this:

### Quick Setup

1. After publishing to PyPI, create a formula:

```ruby
class Allmark < Formula
  include Language::Python::Virtualenv

  desc "Universal eBook to Markdown converter and cleaner"
  homepage "https://github.com/dcondrey/allmark"
  url "https://files.pythonhosted.org/packages/source/a/allmark/allmark-0.4.0.tar.gz"
  sha256 "REPLACE_WITH_PYPI_SHA256"
  license "MIT"

  depends_on "python@3.11"
  depends_on "pandoc"
  depends_on "poppler"

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/allmark", "--help"
  end
end
```

2. Submit to homebrew-core or create your own tap:

```bash
# Create a tap repository
gh repo create homebrew-allmark --public

# Add the formula
mkdir -p Formula
cp allmark.rb Formula/
git add Formula/allmark.rb
git commit -m "Add allmark formula"
git push origin main
```

**Users can install with**:
```bash
# From your tap
brew install dcondrey/allmark/allmark

# Or if accepted to homebrew-core
brew install allmark
```

## 4. Docker Publishing (Optional)

**Status**: ⏳ Not yet set up

Create a Dockerfile for containerized deployments:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pandoc \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Install allmark
RUN pip install --no-cache-dir allmark

# Set working directory
WORKDIR /data

# Default command
ENTRYPOINT ["allmark"]
CMD ["--help"]
```

Publish to Docker Hub:

```bash
# Build
docker build -t dcondrey/allmark:0.4.0 .
docker tag dcondrey/allmark:0.4.0 dcondrey/allmark:latest

# Push
docker push dcondrey/allmark:0.4.0
docker push dcondrey/allmark:latest
```

**Users can run with**:
```bash
docker run -v $(pwd):/data dcondrey/allmark --in /data/books --out /data/output
```

## Publishing Workflow

### For Each New Release

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md**
3. **Commit changes**
4. **Create GitHub Release** → Triggers PyPI publish automatically ✅
5. **conda-forge**: Bot usually creates PR automatically (approve it)
6. **Homebrew** (if using): Update formula and bump version
7. **Docker** (if using): Build and push new images

## Installation Statistics

After publishing, track adoption:

- **PyPI downloads**: https://pypistats.org/packages/allmark
- **conda-forge downloads**: Check feedstock repo
- **GitHub stars/forks**: Measure community interest

## Recommended: Just PyPI + conda-forge

For most users, **PyPI** and **conda-forge** cover 95%+ of the Python ecosystem:

- **PyPI**: pip, poetry, pipx users
- **conda-forge**: conda, mamba users

Homebrew and Docker are optional enhancements for specific use cases.

## Quick Reference

### To Publish a New Version:

```bash
# 1. Update version in pyproject.toml
vim pyproject.toml

# 2. Commit
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 0.5.0"
git push origin master

# 3. Tag and create GitHub Release
git tag -a v0.5.0 -m "Release version 0.5.0"
git push origin v0.5.0

# GitHub Release triggers:
# ✅ PyPI publish (automatic)
# ⚠️  conda-forge PR (usually automatic, approve it)
```

That's it! Both PyPI and conda-forge will be updated.

## Support Matrix

After publishing, your package will be available via:

| Install Method | Works? | Repository |
|---------------|--------|------------|
| `pip install allmark` | ✅ | PyPI |
| `poetry add allmark` | ✅ | PyPI |
| `pipx install allmark` | ✅ | PyPI |
| `conda install -c conda-forge allmark` | ✅ | conda-forge |
| `mamba install -c conda-forge allmark` | ✅ | conda-forge |
| `brew install allmark` | ⏳ | homebrew (optional) |
| `docker pull dcondrey/allmark` | ⏳ | Docker Hub (optional) |

## Next Steps

1. ✅ **PyPI**: Already set up! Just create a GitHub Release
2. ⏳ **conda-forge**: Follow [CONDA_PUBLISHING.md](CONDA_PUBLISHING.md) after PyPI release
3. ⏳ **Homebrew/Docker**: Optional, set up later if needed

## Questions?

- PyPI issues: See [PUBLISHING.md](PUBLISHING.md)
- conda issues: See [CONDA_PUBLISHING.md](CONDA_PUBLISHING.md)
- General questions: Open a GitHub issue
