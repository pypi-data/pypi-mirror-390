# Publishing gri_resolver to PyPI / TestPyPI

## Prerequisites
- Python 3.9+
- Accounts on TestPyPI and/or PyPI
- API tokens created (`__token__` / `pypi-...`)
- Git repository with write access
- All changes committed and pushed

## Version Management

This project uses `setuptools_scm` for automatic version management. The version is derived from Git tags:
- Version is **automatically** generated from the latest Git tag
- No need to manually update version in `pyproject.toml` (it's marked as `dynamic`)
- Use semantic versioning tags: `v1.0.0`, `v1.1.0`, `v2.0.0`, etc.

Check the version that will be built:
```bash
make version
```

## Creating a Release

### Step 1: Prepare the Release

1. **Ensure all changes are committed:**
   ```bash
   git status
   git add .
   git commit -m "Your commit message"
   ```

2. **Run tests and linting:**
   ```bash
   make lint
   make test
   ```

3. **Verify CI/CD passes:**
   - Push to the repository and ensure the pipeline succeeds
   - Check that lint, test, and build stages pass

### Step 2: Create Git Tag

Create an annotated tag for the release (recommended):

```bash
# For a new release (e.g., v1.1.0)
git tag -a v1.1.0 -m "Release v1.1.0: Description of changes"

# Or for a patch release (e.g., v1.0.1)
git tag -a v1.0.1 -m "Release v1.0.1: Bug fixes"

# Push the tag to remote
git push origin v1.1.0
```

**Tag naming convention:**
- Use semantic versioning: `vMAJOR.MINOR.PATCH`
- Examples: `v1.0.0`, `v1.1.0`, `v2.0.0`, `v1.0.1`
- Always prefix with `v`

### Step 3: Verify Version

After creating the tag, verify the version:
```bash
make version
```

This should show the version derived from your tag (e.g., `1.1.0`).

### Step 4: Build and Test Locally

```bash
# Clean previous builds
make clean

# Build the package
make build

# Verify the built package
ls -lh dist/
```

### Step 5: Publish

**Option A: Test on TestPyPI first (recommended)**

```bash
# Upload to TestPyPI
make publish-test

# Test installation from TestPyPI
pip install -i https://test.pypi.org/simple/ gri_resolver==<version>
```

**Option B: Publish to PyPI**

```bash
# Upload to PyPI
make publish
```

**Option C: Publish to custom 'gael' repository**

```bash
# Upload to custom 'gael' repo (from ~/.pypirc)
make publish-gael
```

## One-time: Configure ~/.pypirc

```
[distutils]
index-servers=
    pypi
    testpypi
    gael

[pypi]
  repository = https://upload.pypi.org/legacy/
  username = __token__
  password = pypi-<your-token>

[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = pypi-<your-test-token>

[gael]
  repository = <YOUR-GAEL-INDEX-URL>
  username = <your-username-or-__token__>
  password = <your-token>
```

## Quick Reference: Complete Release Workflow

```bash
# 1. Prepare
make lint
make test
git add .
git commit -m "Prepare release v1.1.0"
git push

# 2. Create and push tag
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 3. Verify version
make version

# 4. Build
make clean
make build

# 5. Publish (choose one)
make publish-test    # TestPyPI
make publish         # PyPI
make publish-gael    # Custom 'gael' repo
```

## Install from TestPyPI

```bash
pip install -i https://test.pypi.org/simple/ gri_resolver
```

## Troubleshooting

### Version shows as "0.0.0" or development version
- Ensure you have created and pushed a Git tag
- Check that the tag follows semantic versioning: `v1.0.0` (with `v` prefix)
- Run `git tag --list` to see existing tags
- Run `make version` to see what version will be built

### Build fails with version error
- Make sure `setuptools-scm>=8` is installed
- Verify `pyproject.toml` has `dynamic = ["version"]` in `[project]`
- Check that you're in a Git repository with tags

### Tag already exists
- If you need to update a tag, delete it first:
  ```bash
  git tag -d v1.1.0              # Delete local tag
  git push origin :refs/tags/v1.1.0  # Delete remote tag
  # Then create a new tag
  ```

## Notes
- **Version is automatically derived from Git tags** - no need to update `pyproject.toml`
- Ensure README.md renders correctly on PyPI (we use Markdown by default)
- For private repositories (e.g., 'gael'), set the correct repository URL and credentials in `~/.pypirc`
- Always test on TestPyPI before publishing to PyPI
- Use annotated tags (`-a`) for releases to include release notes
