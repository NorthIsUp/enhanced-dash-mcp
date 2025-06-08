# Changelog and Continuous Integration

This project uses an automated workflow to keep the `CHANGELOG.md` up to date. Any push to the `main` branch triggers a GitHub Action that regenerates the changelog using recent commit history.

## How It Works

1. The workflow runs on every push to `main`.
2. It installs dependencies and executes the changelog generator.
3. If the changelog is updated, the workflow commits the new file back to the repository.

Developers should not manually edit `CHANGELOG.md`; instead, write Conventional Commit messages so the generator can produce clear release notes.

## Changelog Format

Each version header should follow this pattern so automated tests can verify links:

```
## [1.2.3](https://github.com/joshuadanpeterson/enhanced-dash-mcp/releases/tag/v1.2.3) - YYYY-MM-DD
```

The `tests/test_changelog_links.py` file checks that every entry in `CHANGELOG.md` conforms to this format.

## Release Workflow

When a new Git tag matching `v[0-9]+\.[0-9]+\.[0-9]+` is pushed to `main`, a separate workflow
creates a GitHub release with notes derived from the changelog. This keeps
published versions in sync with the changelog and provides a convenient
download link for each release.
