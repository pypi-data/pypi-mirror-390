# PyPI Upload Guide - Telugu Library v5.0.0

## The Issue
Your upload failed because PyPI credentials are not configured. Here's how to fix it.

## Solution 1: Create .pypirc File (Recommended)

### Step 1: Get Your Credentials
1. Go to https://pypi.org/manage/account/
2. Go to https://test.pypi.org/manage/account/ (for test PyPI)
3. Scroll down to "API tokens"
4. Create a new token with scope "Entire account" or just the project
5. **Copy the token** (starts with `pypi-` or `test-`)

### Step 2: Create Credentials File
Create `~/.pypirc` (Windows: `C:\Users\YourName\.pypirc`):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_REAL_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TEST_TOKEN_HERE
```

**Important:** Replace `pypi-YOUR_TEST_TOKEN_HERE` with your actual token!

### Step 3: Try Upload Again
```bash
python -m twine upload --repository testpypi dist/*
```

## Solution 2: Use Environment Variables

Set these environment variables:

**Windows (Command Prompt):**
```cmd
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-YOUR_TEST_TOKEN_HERE
set TWINE_REPOSITORY=testpypi
```

**Windows (PowerShell):**
```powershell
$env:TWINE_USERNAME="__token__"
$env:TWINE_PASSWORD="pypi-YOUR_TEST_TOKEN_HERE"
$env:TWINE_REPOSITORY="testpypi"
```

Then upload:
```bash
python -m twine upload dist/*
```

## Solution 3: Interactive Login

Use the `--interactive` flag:
```bash
python -m twine upload --repository testpypi --interactive dist/*
```

You'll be prompted for username and password.

## Solution 4: Quick Token Setup

For test.pypi.org, you can also use:
```bash
python -m twine upload --repository testpypi \
    --username __token__ \
    --password pypi-YOUR_TEST_TOKEN_HERE \
    dist/*
```

## Step-by-Step for Test PyPI

### 1. Create Account (if needed)
- Go to https://test.pypi.org/account/register/

### 2. Create API Token
```bash
# Go to: https://test.pypi.org/manage/account/
# Click "Add API token"
# Name: "Telugu Library v5.0"
# Scope: "Entire account" (or create project-specific)
# Click "Create token"
# COPY THE TOKEN (you won't see it again!)
```

### 3. Create Config File
Edit `C:\Users\srath\.pypirc`:
```ini
[distutils]
index-servers = testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TOKEN_HERE
```

### 4. Upload
```bash
python -m twine upload --repository testpypi dist/*
```

## Verification

After successful upload, you can install and test:

```bash
# Install from test PyPI
pip install -i https://test.pypi.org/simple/ telugu-language-tools==5.0.0

# Test it
python -c "from telugu_engine import __version__, translate_sentence; print(__version__); print(translate_sentence('I am going'))"
```

## Troubleshooting

### Error: "400 Bad Request"
- ✅ Check token is correct
- ✅ Check .pypirc file exists
- ✅ Check repository URL
- ✅ Check username is `__token__`

### Error: "403 Forbidden"
- ✅ Check token has correct scope
- ✅ Check token hasn't expired
- ✅ Check package name isn't taken

### Error: "File already exists"
- Upload with `--skip-existing`:
```bash
python -m twine upload --repository testpypi dist/* --skip-existing
```

## For Production PyPI

Once tested on test.pypi.org, upload to production:

### 1. Create Production Token
Go to https://pypi.org/manage/account/ and create a token

### 2. Upload
```bash
python -m twine upload dist/*
```

## Package Information

After upload, your package will be available at:
- **Test PyPI**: https://test.pypi.org/project/telugu-language-tools/5.0.0/
- **Production**: https://pypi.org/project/telugu-language-tools/5.0.0/

## What's in the Package

✅ telugu_engine v5.0.0
✅ Present continuous tense
✅ All v3.0 sections
✅ Modern pronouns
✅ 100% test coverage
✅ Comprehensive documentation

## Next Steps After Upload

1. Verify package on PyPI website
2. Test installation in fresh environment
3. Notify users of v5.0.0 release
4. Update version number for next release

---

**Need help?** Email: support@telugulibrary.org
