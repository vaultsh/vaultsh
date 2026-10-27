# Contributing to Vaultsh

Vaultsh is a pre-alpha security-sensitive project. Contributions should be small, reviewable, tested with synthetic data, and documented accurately. Do not claim a feature is implemented if it is only scaffolded or mocked.

## Development checks

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check .
ruff format --check .
mypy src/vaultsh
python -m compileall -q src tests
python -m build
```

Run all checks that are available. If a dependency/tool is missing or tests skip a standard vector, record that explicitly rather than reporting a complete pass.

## Changelog format

Use the release heading and categories in `CHANGELOG.md`:

```markdown
## 🚀 [0.6.0] - 2026-10-27

### ✨ Added
- Added ...

### 🔄 Changed
- Updated ...

### 🐛 Fixed
- Fixed ...

### 🔒 Security notes and limitations
- ...
```

New work goes under `## 🚧 [Unreleased]` until a release is cut. Keep entries user-visible, specific, and truthful. Include relevant security limitations; do not write “secure” or “audited” based only on tests.

## Emoji and commit-message guide

Use one leading emoji and an imperative English phrase. Emoji describe the primary intent of a change.

| Emoji | Use it for | Example |
|---|---|---|
| 🔄 | Update existing behavior/configuration | `🔄 Update configuration handling` |
| ✨ | Add a user-visible feature | `✨ Add Ethereum balance lookup` |
| 🐛 | Fix a defect | `🐛 Fix JSON-RPC response validation` |
| 🔒 | Security hardening | `🔒 Reject unverified RPC redirects` |
| ⚡ | Performance improvement | `⚡ Reduce startup overhead` |
| 📝 | Documentation-only change | `📝 Update network adapter guide` |
| ♻️ | Refactoring without intended behavior change | `♻️ Refactor network permission checks` |
| 🧪 | Add or improve tests | `🧪 Add Ethereum RPC client tests` |
| 🔥 | Remove obsolete code/functionality | `🔥 Remove deprecated network helper` |
| 🚀 | Release preparation | `🚀 Release Vaultsh 0.6.0` |

Examples of complete commit messages:

```text
✨ Add Ethereum Mainnet balance lookup
🧪 Add mocked JSON-RPC chain-ID tests
📝 Document Bitcoin address-history limits
🔒 Reject malformed Ethereum address checksums
🚀 Release Vaultsh 0.6.0
```

If a commit contains several distinct changes, split it when practical. Do not use `🚀 Release` for ordinary changes that do not cut a version.

## Pull-request checklist

- [ ] The change has a clear scope and does not silently enable network traffic.
- [ ] Chain-specific address, derivation, unit, and RPC rules stay in that chain's adapter.
- [ ] Tests cover valid, malformed, and hostile responses without calling public APIs.
- [ ] No real recovery phrase, password, private key, vault, backup, or endpoint token is included.
- [ ] Relevant README, CLI/configuration/security docs, and CHANGELOG are updated.
- [ ] `git diff --check` passes and generated caches/artifacts are excluded.
- [ ] Results accurately report skipped tests, unrun tools, and unverified platforms.

## Release checklist

1. Update version metadata in `pyproject.toml` and `src/vaultsh/__init__.py`.
2. Move the release notes from `Unreleased` into a dated version heading.
3. Install all runtime/dev dependencies and run the full suite with no unexpected skips.
4. Run Ruff, mypy, package build, and automated Windows/Linux CI.
5. Inspect the archive for caches, `.coverage`, local configs, vaults, backups, and other secrets.
6. Update test results and security limitations; do not equate test count with audit status.
