# Contributing to Vaultsh

Thank you for helping improve Vaultsh. It is a pre-alpha security-sensitive project, so small, reviewable changes are preferred over broad, hard-to-audit patches.

## Before making a change

1. Read [README.md](README.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md).
2. Open an issue or write down the problem and the intended behavior before making a large change.
3. Keep chain-specific behavior inside the relevant network adapter. Do not assume that address derivation, signatures, key formats, or transaction rules are identical across chains.
4. Never put real recovery phrases, private keys, passwords, wallet files, or personal wallet data in code, tests, screenshots, logs, commits, or bug reports. Use synthetic test vectors only.
5. Add or update tests for behavioral changes. Cryptographic changes require standard vectors and careful review, not only tests that mirror the implementation.

## Development setup

```bash
python -m venv .venv
# Activate the environment for your shell, then:
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
ruff check .
mypy src/vaultsh
```

For Windows PowerShell, activate the environment with `\.venv\Scripts\Activate.ps1`. See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for more detail.

## Commit-message style

Use one emoji prefix followed by a short English imperative sentence. Keep each commit focused on one logical change. The following vocabulary is recommended:

| Emoji | Use it for | Example commit message |
|---|---|---|
| 🔄 | Changed or updated behavior/configuration | `🔄 Update configuration handling` |
| ✨ | A new feature | `✨ Add encrypted vault storage` |
| 🐛 | A bug fix | `🐛 Fix config validation` |
| 🔒 | Security hardening or security-related changes | `🔒 Harden encryption parameters` |
| ⚡ | Performance improvement | `⚡ Improve startup performance` |
| 📝 | Documentation-only change | `📝 Update README` |
| ♻️ | Refactoring without intended behavior change | `♻️ Refactor network policy helpers` |
| 🧪 | Tests or test infrastructure | `🧪 Add encryption unit tests` |
| 🔥 | Removal of obsolete or deprecated functionality | `🔥 Remove deprecated module` |
| 🚀 | Version release or release preparation | `🚀 Release MVP 0.1.0` |

Write in English so commit history remains consistent across contributors. Use imperative verbs such as `Add`, `Fix`, `Update`, `Harden`, `Refactor`, `Remove`, and `Release`. Do not use a vague message such as `changes`, `update`, or `fixed stuff`.

### Examples by task

```text
✨ Add Bitcoin wallet recovery command
🐛 Fix malformed vault document handling
🔒 Bound Scrypt parameters before key derivation
🧪 Add BIP-84 address derivation vectors
📝 Document encrypted vault schema v2
♻️ Extract wallet record validation helper
🔄 Update release metadata to 0.4.0
🚀 Release Vaultsh 0.4.0
```

## Changelog format

Keep `CHANGELOG.md` updated whenever user-visible behavior, dependencies, security posture, supported formats, or developer workflow changes. Add unreleased work under `## 🚧 [Unreleased]`, then use one or more matching subsections:

- `### ✨ Added` — new functionality.
- `### 🔄 Changed` — changed or updated behavior.
- `### 🐛 Fixed` — bug fixes.
- `### 🔒 Security` — security-relevant changes.
- `### ⚡ Performance` — performance improvements.
- `### ♻️ Refactored` — internal refactoring without intended behavioral changes.
- `### 🧪 Tests` — new tests or test infrastructure.
- `### 📝 Documentation` — documentation-only changes.
- `### 🔥 Removed` — removed functionality.
- `### 🛡️ Security notes and limitations` — release-specific caveats and known limitations.

Changelog entries describe what changed and why from a user's or maintainer's perspective. Do not put secrets or exploit details into the changelog. When cutting a release, move the relevant entries out of `[Unreleased]`, add the release version and date, update `pyproject.toml` and `src/vaultsh/__init__.py`, and verify all version strings agree.

## Local change workflow

```bash
git status --short
pytest
ruff check .
mypy src/vaultsh
git diff --check
git diff
```

After reviewing the diff, stage only the intended files and commit the change:

```bash
git add README.md docs/ CHANGELOG.md CONTRIBUTING.md
git commit -m "📝 Add complete project documentation"
```

Do not stage vaults, backups, seed phrases, credentials, generated caches, coverage reports, or build output. `.gitignore` excludes common sensitive and generated files, but always inspect `git status` before committing.

## Pull request checklist

- [ ] The problem and the intended behavior are described.
- [ ] Tests cover the change, including failure paths where relevant.
- [ ] Tests, Ruff, and mypy have been run or any limitation is clearly reported.
- [ ] Documentation and `CHANGELOG.md` are updated where needed.
- [ ] No secrets, real wallet data, generated caches, or unrelated files are included.
- [ ] Security-sensitive claims are accurate and do not imply an audit or production readiness.

## Security reports

Do not open a public issue containing a secret or an exploitable vulnerability. Follow [SECURITY.md](SECURITY.md) and use a private reporting channel configured by the repository maintainers.
