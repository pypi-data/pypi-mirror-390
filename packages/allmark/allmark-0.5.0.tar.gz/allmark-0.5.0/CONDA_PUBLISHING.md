# Publishing to conda-forge

This guide explains how to publish `allmark` to conda-forge.

## Overview

conda-forge is a community-driven package repository for conda. Unlike PyPI (which is automated via GitHub Actions), conda-forge requires a separate repository and goes through a review process.

## Prerequisites

1. **Package must be on PyPI first** - conda-forge recipes typically build from PyPI releases
2. GitHub account
3. conda-forge staging fork

## Initial Setup (One-time)

### Step 1: Wait for PyPI Publication

First, ensure your package is published to PyPI (see PUBLISHING.md). This is required because the conda recipe will download the source from PyPI.

### Step 2: Create a conda Recipe

Create a `meta.yaml` file that describes how to build your package for conda:

```yaml
{% set name = "allmark" %}
{% set version = "0.4.0" %}

package:
  name: {{ name|lower }}
  version: {{ version }}

source:
  url: https://pypi.io/packages/source/{{ name[0] }}/{{ name }}/allmark-{{ version }}.tar.gz
  sha256: CHECKSUM_HERE  # Get from PyPI

build:
  noarch: python
  number: 0
  script: {{ PYTHON }} -m pip install . -vv
  entry_points:
    - allmark = allmark.cli:main

requirements:
  host:
    - python >=3.7
    - pip
    - setuptools >=45
    - wheel
  run:
    - python >=3.7
    - pandoc
    - poppler

test:
  imports:
    - allmark
  commands:
    - allmark --help

about:
  home: https://github.com/dcondrey/allmark
  license: MIT
  license_file: LICENSE
  summary: Universal eBook to Markdown converter and cleaner
  description: |
    allmark is a universal eBook to Markdown converter that supports 25+ formats
    including EPUB, MOBI, PDF, DOCX, and more. It intelligently cleans converted
    text by removing frontmatter, backmatter, headers, footers, and OCR artifacts.
  doc_url: https://github.com/dcondrey/allmark
  dev_url: https://github.com/dcondrey/allmark

extra:
  recipe-maintainers:
    - dcondrey
```

### Step 3: Get the SHA256 Checksum

After publishing to PyPI, get the checksum:

```bash
# Method 1: From PyPI page
# Go to https://pypi.org/project/allmark/#files
# Click on the .tar.gz file
# Copy the SHA256 hash

# Method 2: Download and compute
pip download --no-deps allmark==0.4.0
sha256sum allmark-0.4.0.tar.gz
```

Update the `sha256` field in meta.yaml with this value.

### Step 4: Submit to conda-forge

There are two ways to submit to conda-forge:

#### Option A: Using staged-recipes (For New Packages)

1. Fork https://github.com/conda-forge/staged-recipes

2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/staged-recipes
   cd staged-recipes
   ```

3. Create a new branch:
   ```bash
   git checkout -b add-allmark
   ```

4. Create your recipe directory:
   ```bash
   mkdir -p recipes/allmark
   cp /path/to/meta.yaml recipes/allmark/
   ```

5. Commit and push:
   ```bash
   git add recipes/allmark/
   git commit -m "Add recipe for allmark"
   git push origin add-allmark
   ```

6. Create a Pull Request to conda-forge/staged-recipes

7. Wait for review:
   - conda-forge maintainers will review your recipe
   - They may request changes
   - Once approved, a feedstock will be created automatically

#### Option B: Using grayskull (Automated)

Install grayskull to auto-generate the recipe:

```bash
pip install grayskull
grayskull pypi allmark
```

This will create a `meta.yaml` file automatically from your PyPI package.

## Updating the Package (After Initial Submission)

Once your feedstock is created at `https://github.com/conda-forge/allmark-feedstock`:

### Manual Update

1. Fork the feedstock repository

2. Update `recipe/meta.yaml`:
   - Update `version`
   - Update `sha256`
   - Update `build: number` to 0

3. Create a PR to the feedstock

### Automated Update (Recommended)

conda-forge has bots that can auto-update when you release to PyPI:

1. The `regro-cf-autotick-bot` watches PyPI
2. When you release a new version to PyPI, it automatically creates a PR
3. You just need to approve and merge the PR

## Alternative: Publishing to Anaconda.org (Personal Channel)

If you want to publish quickly without waiting for conda-forge review:

### Step 1: Install conda-build

```bash
conda install conda-build anaconda-client
```

### Step 2: Build the Package

```bash
conda build .
```

### Step 3: Login to Anaconda

```bash
anaconda login
```

### Step 4: Upload to Your Channel

```bash
anaconda upload /path/to/allmark-0.4.0-py_0.tar.bz2
```

Users can then install with:
```bash
conda install -c YOUR_USERNAME allmark
```

## Installation Methods After Publishing

Once published to conda-forge:

```bash
# Using conda
conda install -c conda-forge allmark

# Using mamba (faster)
mamba install -c conda-forge allmark
```

If using personal Anaconda channel:

```bash
conda install -c YOUR_USERNAME allmark
```

## Best Practices

1. **Publish to PyPI first** - conda-forge recipes typically pull from PyPI
2. **Keep recipes minimal** - Let conda-forge bots handle updates
3. **Add system dependencies** - List pandoc, poppler, etc. in requirements
4. **Use noarch: python** - If package is pure Python
5. **Test thoroughly** - The conda-forge CI will test on multiple platforms

## Troubleshooting

### Recipe Rejected

- Check the conda-forge guidelines: https://conda-forge.org/docs/maintainer/adding_pkgs.html
- Ensure all dependencies are available on conda-forge
- Verify the package builds successfully

### Build Fails

- Check that all dependencies are listed
- Verify the entry point is correct
- Test locally with `conda build`

### Update PR Not Created

- Check that the bot is enabled in the feedstock
- Verify PyPI package is properly structured
- May need to trigger manually

## Resources

- conda-forge Documentation: https://conda-forge.org/docs/
- staged-recipes: https://github.com/conda-forge/staged-recipes
- grayskull: https://github.com/conda/grayskull
- Anaconda.org: https://anaconda.org/

## Timeline

- **PyPI**: Instant (via GitHub Actions)
- **conda-forge**: 1-7 days for initial review
- **conda-forge updates**: Usually automated within 24 hours of PyPI release
