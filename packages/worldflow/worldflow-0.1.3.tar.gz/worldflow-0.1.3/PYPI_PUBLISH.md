# 📦 Publishing Worldflow to PyPI

Complete guide to publish Worldflow on PyPI (Python Package Index).

---

## 🎯 Why Publish to PyPI?

**Critical for adoption!** Most Python developers expect:

```bash
pip install worldflow
```

Without PyPI, you lose 80%+ of potential users who won't install from GitHub.

---

## ✅ Prerequisites

1. **PyPI Account**
   - Create account: https://pypi.org/account/register/
   - Verify email

2. **TestPyPI Account** (recommended for testing)
   - Create account: https://test.pypi.org/account/register/
   - Verify email

3. **API Tokens** (more secure than passwords)
   - PyPI: https://pypi.org/manage/account/token/
   - TestPyPI: https://test.pypi.org/manage/account/token/

---

## 🔧 Setup (One-Time)

### 1. Install Build Tools

```bash
pip install --upgrade build twine
```

### 2. Configure API Tokens

Create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_API_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
```

**Important**: Never commit `.pypirc`! It contains secrets.

---

## 🚀 Publishing Steps

### Step 1: Clean Previous Builds

```bash
cd /Users/putua1/Documents/_code/_integrations/worldflow

# Remove old builds
rm -rf dist/ build/ *.egg-info
```

### Step 2: Build Distribution

```bash
# Build wheel and source distribution
python -m build
```

This creates:
- `dist/worldflow-0.1.0-py3-none-any.whl` (wheel)
- `dist/worldflow-0.1.0.tar.gz` (source)

### Step 3: Test on TestPyPI (Recommended)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

Then test installation:

```bash
# Create fresh venv for testing
python -m venv test_env
source test_env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ worldflow

# Test it works
python -c "from worldflow import workflow, step; print('Success!')"

# Clean up
deactivate
rm -rf test_env
```

### Step 4: Publish to Real PyPI

```bash
# Upload to real PyPI
python -m twine upload dist/*
```

**This is permanent!** You cannot delete or re-upload the same version.

### Step 5: Verify

```bash
# Install from PyPI
pip install worldflow

# Or with AWS support
pip install "worldflow[aws]"

# Test
python -c "from worldflow import workflow, step; print('Worldflow installed!')"
```

---

## 🎉 Post-Publication

### 1. Update README

Add badges to `README.md`:

```markdown
[![PyPI version](https://badge.fury.io/py/worldflow.svg)](https://badge.fury.io/py/worldflow)
[![Python versions](https://img.shields.io/pypi/pyversions/worldflow.svg)](https://pypi.org/project/worldflow/)
[![Downloads](https://pepy.tech/badge/worldflow)](https://pepy.tech/project/worldflow)
```

### 2. Announce on PyPI Page

Your package will be live at: https://pypi.org/project/worldflow/

Update project description on PyPI (if needed).

### 3. Update GitHub README

Change installation from:

```bash
pip install worldflow  # Coming soon
```

To:

```bash
pip install worldflow  # ✅ Now available!
```

### 4. Announce It!

**Twitter**:
```
🎉 Worldflow is now on PyPI!

Install with:
pip install worldflow

Start building durable workflows in Python with decorator-based API.

https://pypi.org/project/worldflow/

#Python #PyPI #OpenSource
```

**Reddit r/Python**:
```
Title: Worldflow 0.1.0 is now on PyPI!

You can now install Worldflow with:
pip install worldflow

Built a durable workflow framework with pluggable backends 
(SQLite for dev, AWS Lambda for production).

PyPI: https://pypi.org/project/worldflow/
GitHub: https://github.com/ptsadi/worldflow
```

---

## 📈 Monitoring

### PyPI Stats

- **Downloads**: https://pepy.tech/project/worldflow
- **Package page**: https://pypi.org/project/worldflow/
- **Release history**: https://pypi.org/project/worldflow/#history

### Track Adoption

Monitor:
- Daily/weekly downloads
- GitHub stars (usually correlates)
- Issues/questions
- Version adoption

---

## 🔄 Publishing Updates

For version 0.2.0 and beyond:

### 1. Update Version

Edit `pyproject.toml`:

```toml
version = "0.2.0"
```

### 2. Update CHANGELOG.md

```markdown
## [0.2.0] - 2025-XX-XX

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix A
- Bug fix B
```

### 3. Commit & Tag

```bash
git add pyproject.toml CHANGELOG.md
git commit -m "Bump version to 0.2.0"
git tag v0.2.0
git push origin main --tags
```

### 4. Build & Publish

```bash
rm -rf dist/
python -m build
python -m twine upload dist/*
```

### 5. Create GitHub Release

Go to: https://github.com/ptsadi/worldflow/releases/new

- Tag: `v0.2.0`
- Copy changelog section
- Publish

---

## 🐛 Troubleshooting

### Error: "File already exists"

**Problem**: You can't re-upload the same version.

**Solution**: 
- Bump version number
- Never overwrite published versions

### Error: "Invalid username/password"

**Problem**: API token not configured correctly.

**Solution**:
- Check `~/.pypirc` format
- Regenerate API token
- Use `__token__` as username

### Error: "Package name taken"

**Problem**: Another package uses "worldflow".

**Solution** (unlikely for you, but just in case):
- Check: https://pypi.org/project/worldflow/
- If taken, choose different name
- Update `pyproject.toml`

### Warning: "Long description failed"

**Problem**: README.md has formatting issues.

**Solution**:
- Test with: `python -m twine check dist/*`
- Fix markdown issues
- Rebuild

---

## 🎯 Versioning Strategy

Follow [Semantic Versioning](https://semver.org/):

- **0.1.0** → **0.1.1**: Bug fixes (patch)
- **0.1.0** → **0.2.0**: New features (minor)
- **0.x.x** → **1.0.0**: Stable API (major)

### When to bump?

- **Patch (0.1.x)**: Bug fixes, docs, no API changes
- **Minor (0.x.0)**: New features, backwards compatible
- **Major (x.0.0)**: Breaking changes, API redesign

---

## 📦 What Gets Published?

From `pyproject.toml` and `MANIFEST.in`:

**Included**:
- All Python files in `worldflow/`
- `README.md`
- `LICENSE`
- `CHANGELOG.md`
- `pyproject.toml`

**Excluded**:
- Tests
- Examples (optional - you can include if small)
- Infrastructure code
- Documentation (except README)
- `.git/`, `__pycache__/`, etc.

---

## 🎊 Success!

Once published:

1. ✅ Users can `pip install worldflow`
2. ✅ Package appears on PyPI.org
3. ✅ Automatic inclusion in:
   - PyPI search results
   - Library.io
   - Security scanners
   - Dependency bots

---

## 🚀 Quick Commands Reference

```bash
# Build
python -m build

# Test upload (TestPyPI)
python -m twine upload --repository testpypi dist/*

# Real upload (PyPI)
python -m twine upload dist/*

# Test installation
pip install worldflow

# With extras
pip install "worldflow[aws]"
pip install "worldflow[dev]"
```

---

## ⚠️ Important Notes

1. **You cannot delete** published versions from PyPI
2. **You cannot re-upload** the same version
3. **Yanking** a version is possible but discouraged
4. **Test on TestPyPI first** to catch issues
5. **Version numbers are permanent** - choose wisely

---

## 🎯 Recommended First Steps

1. **Now**: Test build locally
2. **Today**: Upload to TestPyPI and test
3. **After testing**: Upload to real PyPI
4. **After publishing**: Announce on social media
5. **Monitor**: Check download stats after 24h

---

## 💡 Pro Tips

1. **Always test on TestPyPI first**
2. **Keep CHANGELOG.md updated** (users love this)
3. **Use GitHub Actions** for automatic publishing (future)
4. **Monitor security** advisories (Dependabot helps)
5. **Respond to PyPI issues** quickly

---

**Ready to publish?** 🚀

Run these commands:

```bash
cd /Users/putua1/Documents/_code/_integrations/worldflow
pip install --upgrade build twine
python -m build
python -m twine upload --repository testpypi dist/*  # Test first!
# python -m twine upload dist/*  # Then real PyPI
```

Good luck! 🍀

