# Contributing to SIEM Dashboard

Thank you for your interest in contributing to this project! This repository is designed to showcase a SIEM dashboard demo with a complete ELK stack, Flask UI, log generation, and alerting features.

## How to contribute

1. Fork the repository.
2. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. Make your changes.
4. Run tests and linting:
   ```bash
   make install
   make test
   make lint
   ```
5. Submit a pull request with a clear description of your changes.

## Code standards

- Python code should be formatted with `black` where possible.
- Keep dependencies in `requirements.txt` up to date.
- Add tests for bug fixes and new features.

## Reporting issues

Use the issue templates in `.github/ISSUE_TEMPLATE/` for bug reports and feature requests.

## Branching and commits

- Use descriptive branch names like `fix/login-error` or `feature/kibana-dashboard`.
- Write clear commit messages. Include the motivation and what changed.

## Running locally

Use the included `Makefile` for common commands.

```bash
make up
make app
make generate
```

## Thank you

Contributions are welcome! If you want help getting started, open an issue and we can help define a contribution.
