# Git Setup & GitHub Push Guide
## MySQL Chatbot Repository

---

## 🚀 Quick Setup

### 1. Initialize Git Repository

```bash
cd c:\Users\jamru\.gemini\antigravity\scratch\mysql-chatbot

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: MySQL Chatbot with Gemini AI"
```

### 2. Create GitHub Repository

**Option A: Via GitHub Website** (Recommended)
1. Go to https://github.com/new
2. Repository name: `mysql-chatbot`
3. Description: "Natural language interface for MySQL databases powered by AI"
4. Choose: ⭕ Public or 🔒 Private
5. ❌ DON'T initialize with README (we already have one)
6. Click "Create repository"

**Option B: Via GitHub CLI**
```bash
# Install GitHub CLI: https://cli.github.com/
gh repo create mysql-chatbot --public --source=. --remote=origin
```

### 3. Push to GitHub

```bash
# Add remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/mysql-chatbot.git

# Push to main branch
git branch -M main
git push -u origin main
```

---

## ✅ Checklist Before Pushing

**CRITICAL - Check these BEFORE git push:**

```bash
# 1. Verify .env is NOT tracked
git status | grep .env
# Should show: .env (untracked) or nothing

# 2. Check .gitignore is working
cat .gitignore | grep .env
# Should show: .env and variants

# 3. View what will be committed
git status

# 4. Ensure no sensitive files
git ls-files | grep -E "\.env|password|secret|key"
# Should return NOTHING
```

**If .env appears in tracked files:**
```bash
# Remove from git (keep local file)
git rm --cached .env
git commit -m "Remove .env from tracking"
```

---

## 📁 Files That WILL Be Pushed

✅ **Safe to commit:**
- Source code (*.py)
- Configuration templates (.env.example, .env.dev, .env.staging)
- Documentation (*.md)
- Docker files (Dockerfile, docker-compose.yml)
- Requirements (requirements.txt)
- Sample database (sample_db/*.sql)

❌ **NOT committed (in .gitignore):**
- .env (actual secrets)
- .env.production (production secrets)
- logs/
- cache/
- __pycache__/
- *.log
- temp files

---

## 🔒 Security Checks

### Before Pushing:

```bash
# 1. Check for API keys in code
rg "sk-" --type py
rg "api.*key.*=" --type py -i

# 2. Check for passwords
rg "password.*=" --type py -i

# 3. Verify .env.example has no real secrets
cat .env.example | grep -E "sk-|password|secret"
# Should only show placeholders like "your-api-key-here"
```

### After Pushing:

```bash
# Verify on GitHub
# Go to: https://github.com/yourusername/mysql-chatbot
# Check: .env should NOT appear in file list
```

---

## 📝 Git Workflow

### Daily Development:

```bash
# 1. Check status
git status

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "Add feature: query suggestions"

# 4. Push to GitHub
git push
```

### Feature Branches:

```bash
# Create feature branch
git checkout -b feature/new-llm-provider

# Make changes, commit
git add .
git commit -m "Add Claude provider support"

# Push feature branch
git push origin feature/new-llm-provider

# Merge to main (via Pull Request on GitHub)
```

---

## 🌿 Branch Strategy

```
main (production-ready)
  ├── develop (integration)
  │   ├── feature/query-caching
  │   ├── feature/new-ui
  │   └── fix/database-timeout
  └── hotfix/critical-security-fix
```

**Recommended:**
```bash
# Create develop branch
git checkout -b develop
git push origin develop

# Work on features
git checkout -b feature/my-feature develop
# ... make changes ...
git push origin feature/my-feature
```

---

## 📦 Release Process

```bash
# 1. Ensure develop is stable
git checkout develop
git pull

# 2. Create release branch
git checkout -b release/v1.0.0

# 3. Update version numbers, changelog
# Edit version in __init__.py, README, etc.

# 4. Commit and tag
git commit -m "Release v1.0.0"
git tag -a v1.0.0 -m "Version 1.0.0: Initial stable release"

# 5. Merge to main
git checkout main
git merge release/v1.0.0

# 6. Push with tags
git push origin main --tags
```

---

## 🏷️ Suggested Tags

```bash
# Create version tag
git tag -a v1.0.0 -m "First production release"
git push origin v1.0.0

# Create annotated tag
git tag -a beta-1.0 -m "Beta release for testing"
git push origin beta-1.0

# List all tags
git tag -l
```

---

## 📋 Commit Message Convention

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```bash
git commit -m "feat(llm): Add Ollama local LLM support"
git commit -m "fix(cache): Fix Redis connection timeout"
git commit -m "docs: Update deployment guide for PM2"
git commit -m "chore: Update dependencies to latest"
```

---

## 🔄 Clone & Setup (For Others)

**Instructions for team members:**

```bash
# 1. Clone repository
git clone https://github.com/yourusername/mysql-chatbot.git
cd mysql-chatbot

# 2. Setup environment
cp .env.example .env
# Edit .env with personal API keys

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python main.py  # Backend
streamlit run streamlit_app.py  # Frontend
```

---

## 🎯 GitHub Repository Settings

### After creating repo:

1. **Add Description**
   - "Natural language interface for MySQL databases powered by AI"

2. **Add Topics**
   - `mysql`, `chatbot`, `ai`, `gemini`, `fastapi`, `streamlit`, `nlp`, `sql`

3. **Add Website** (if deployed)
   - Your production URL

4. **Enable Issues**
   - Settings → Features → ✅ Issues

5. **Enable Discussions**
   - Settings → Features → ✅ Discussions

6. **Add LICENSE**
   - Create file: LICENSE
   - Choose: MIT License

7. **Branch Protection** (for teams)
   - Settings → Branches → Add rule
   - Branch name: `main`
   - ✅ Require pull request reviews

---

## ⚠️ Common Issues

### Issue: .env accidentally committed

**Solution:**
```bash
# Remove from git history
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch .env' \
--prune-empty --tag-name-filter cat -- --all

# Force push (CAUTION!)
git push origin --force --all

# Rotate all secrets immediately!
# Change API keys, passwords, etc.
```

### Issue: Large files rejected

**Solution:**
```bash
# Check file sizes
find . -size +50M

# Use Git LFS for large files
git lfs install
git lfs track "*.sql"
git add .gitattributes
git commit -m "Add Git LFS for large SQL files"
```

---

## 📊 GitHub Actions (CI/CD)

**Create:** `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
```

---

## ✅ Post-Push Checklist

After first push:
- [ ] Verify repo appears on GitHub
- [ ] Check .env is NOT visible
- [ ] README displays correctly
- [ ] Clone repo in new folder to test
- [ ] Update repo settings (description, topics)
- [ ] Add LICENSE file
- [ ] Enable GitHub Pages (if needed)
- [ ] Share repo link with team

---

## 🔗 Useful Commands

```bash
# View remote URL
git remote -v

# Change remote URL
git remote set-url origin https://github.com/newusername/mysql-chatbot.git

# Pull latest changes
git pull origin main

# View commit history
git log --oneline --graph --all

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- .
```

---

**Ready to push!** 🚀

```bash
git init
git add .
git commit -m "Initial commit: MySQL Chatbot with Gemini AI"
git remote add origin https://github.com/yourusername/mysql-chatbot.git
git push -u origin main
```
