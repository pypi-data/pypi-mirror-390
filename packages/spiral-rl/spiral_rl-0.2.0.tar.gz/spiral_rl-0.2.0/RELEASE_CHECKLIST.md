# Release Checklist for spiral-rl

Use this checklist when releasing a new version of spiral-rl to PyPI and GitHub Packages.

## Pre-Release

- [ ] All tests pass: `pytest tests/`
- [ ] Code is formatted: `black spiral/ && isort spiral/`
- [ ] Documentation is up to date (README.md, CLAUDE.md)
- [ ] CHANGELOG updated with new version changes
- [ ] All API keys removed from code (check with `git grep -i "api.*key.*=.*[a-z0-9]"`)

## Version Update

- [ ] Update version in `pyproject.toml`:
  ```toml
  version = "0.X.Y"
  ```
- [ ] Commit version bump:
  ```bash
  git add pyproject.toml
  git commit -m "Bump version to 0.X.Y"
  git push
  ```

## Build Package

- [ ] Clean previous builds:
  ```bash
  rm -rf build/ dist/ *.egg-info
  ```
- [ ] Build package:
  ```bash
  bash scripts/build_package.sh
  ```
- [ ] Verify build output in `dist/` directory
- [ ] Test installation locally:
  ```bash
  pip install dist/spiral_rl-*.whl
  python -c "import spiral; print(spiral.__version__)"
  ```

## Release to PyPI

- [ ] Set PyPI token:
  ```bash
  export PYPI_TOKEN=your_pypi_token
  ```
- [ ] Upload to PyPI:
  ```bash
  bash scripts/release_pypi.sh
  ```
- [ ] Verify on PyPI: https://pypi.org/project/spiral-rl/
- [ ] Test installation from PyPI:
  ```bash
  pip install spiral-rl[tinker]
  ```

## Release to GitHub Packages

- [ ] Set GitHub token:
  ```bash
  export GITHUB_TOKEN=your_github_token
  ```
- [ ] Upload to GitHub Packages:
  ```bash
  bash scripts/release_github.sh
  ```
- [ ] Verify on GitHub Packages

## Create GitHub Release

- [ ] Go to https://github.com/spiral-rl/spiral-on-tinker/releases/new
- [ ] Create tag: `v0.X.Y`
- [ ] Release title: `spiral-rl v0.X.Y`
- [ ] Add release notes (copy from CHANGELOG)
- [ ] Attach `dist/` files to release
- [ ] Publish release

## Post-Release

- [ ] Verify installation works:
  ```bash
  pip install spiral-rl[tinker]
  python -c "import spiral; print(spiral.__version__)"
  ```
- [ ] Update documentation if needed
- [ ] Announce release (if applicable)
- [ ] Start development on next version:
  ```bash
  # Update version to next dev version
  # e.g., 0.2.1 -> 0.3.0-dev
  ```

## Troubleshooting

### Build fails
- Check `pyproject.toml` syntax
- Ensure all required files are in MANIFEST.in
- Clean build artifacts and try again

### Upload to PyPI fails
- Verify PyPI token is correct
- Check if version already exists on PyPI
- Ensure package name is available

### GitHub Packages upload fails
- Verify GitHub token has `write:packages` scope
- Check repository permissions
- Ensure `.pypirc` is configured correctly
