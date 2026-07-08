# Release Runbook

This runbook describes how to cut a GAL release without publishing or tagging
from automation by accident. The default `0.1.0` path is a GitHub source
release. PyPI publishing is optional and should only happen after confirming the
distribution name and package ownership.

## Release Choices

Before cutting a release, decide:

- Whether this is a GitHub-only source release or also a PyPI package release.
- Whether the Python distribution name remains `gal-netlist`.
- Whether the README draft-status language is still accurate.
- Whether the dialect vocabulary is stable enough for the release notes.

## Local Gate

Start from a clean worktree on `main`:

```bash
git status --short
git pull --ff-only
```

Run the local release gate:

```bash
python3 scripts/release_check.py
```

The release gate checks version consistency across `pyproject.toml`,
`src/gal_netlist/_version.py`, `CHANGELOG.md`, and the requested tag. It then
runs tests, builds the source distribution and wheel, checks the distribution
artifacts with Twine, smoke-tests the wheel from a temporary virtual
environment, smoke-tests checkout CLI commands, and prints the manual tag and
publish commands. It does not tag, push a tag, create a GitHub release, or
upload to PyPI.

During release-gate development only, use:

```bash
python3 scripts/release_check.py --allow-dirty
```

To run only the version consistency check:

```bash
python3 scripts/release_check.py --version-only
```

## GitHub Source Release

After the local gate passes, create and push an annotated tag:

```bash
git tag -a v0.1.0 -m "GAL 0.1.0"
git push origin v0.1.0
```

Verify that CI and Pages are green for the tagged commit:

```bash
gh run list --branch main --limit 5
gh run list --limit 10
```

Create the GitHub release from the built artifacts:

```bash
gh release create v0.1.0 \
  dist/gal_netlist-0.1.0.tar.gz \
  dist/gal_netlist-0.1.0-py3-none-any.whl \
  --title "GAL 0.1.0" \
  --notes-file dist/release-notes-v0.1.0.md \
  --draft
```

`scripts/release_check.py` generates the release notes file from the matching
`CHANGELOG.md` version section. Review the draft release in GitHub before
publishing it.

## Optional PyPI Release

Only publish to PyPI after confirming package ownership and release scope. The
local gate leaves verified artifacts in `dist/`.

Install upload tooling if needed:

```bash
python3 -m pip install --upgrade twine
```

Check the artifacts:

```bash
python3 -m twine check \
  dist/gal_netlist-0.1.0.tar.gz \
  dist/gal_netlist-0.1.0-py3-none-any.whl
```

Upload only after final approval:

```bash
python3 -m twine upload \
  dist/gal_netlist-0.1.0.tar.gz \
  dist/gal_netlist-0.1.0-py3-none-any.whl
```

## Post-Release Checks

After publishing the GitHub release, verify:

- The GitHub release points at the intended commit.
- CI is green for the release commit.
- GitHub Pages is deployed and reachable.
- `CHANGELOG.md` contains the released version and date.
- The next unreleased work starts in a new changelog section.

For a PyPI release, also verify installation from a clean environment:

```bash
tmpdir="$(mktemp -d)"
python3 -m venv "$tmpdir/venv"
"$tmpdir/venv/bin/python" -m pip install gal-netlist==0.1.0
"$tmpdir/venv/bin/gal" --version
```
