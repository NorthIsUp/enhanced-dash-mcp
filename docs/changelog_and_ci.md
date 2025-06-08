# Changelog and Continuous Integration

This project uses an automated workflow to keep the `CHANGELOG.md` up to date. Any push to the `main` branch triggers a GitHub Action that regenerates the changelog using recent commit history.

## How It Works

1. The workflow runs on every push to `main`.
2. It installs dependencies and executes the changelog generator.
3. If the changelog is updated, the workflow commits the new file back to the repository.

Developers should not manually edit `CHANGELOG.md`; instead, write Conventional Commit messages so the generator can produce clear release notes.
