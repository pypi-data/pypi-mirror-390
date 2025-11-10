## [1.0.1](https://github.com/marcszy91/elli-charge-api/compare/v1.0.0...v1.0.1) (2025-11-07)


### Bug Fixes

* enable Docker build and add PyPI publishing to release workflow ([004424b](https://github.com/marcszy91/elli-charge-api/commit/004424b9b6eb351674360e699f6257577fd34123))
* exclude API and infrastructure files from PyPI package ([d3ef5c0](https://github.com/marcszy91/elli-charge-api/commit/d3ef5c0cabe8a0bb3378069020be25603c4e0d9d))

## 1.0.0 (2025-11-07)


### ⚠ BREAKING CHANGES

* Switch to Semantic Release for automated versioning

- Remove Release Please workflows and configuration
- Add Semantic Release with .releaserc.json configuration
- Create new release.yml workflow for automatic releases
- Update CONTRIBUTING.md with new release process
- No more PRs for releases - fully automated on push to main
- Semantic Release will analyze commits and create releases automatically

Versioning rules:
- feat: → minor version bump (0.x.0)
- fix: → patch version bump (0.0.x)
- feat!: or BREAKING CHANGE → major version bump (x.0.0)

### Features

* initial implementation of Elli API client and FastAPI server ([a28787c](https://github.com/marcszy91/elli-charge-api/commit/a28787c29137ce1c90640ce3ad372a08365cde5d))
* migrate from Release Please to Semantic Release ([da118b6](https://github.com/marcszy91/elli-charge-api/commit/da118b65048b0db3eddd6122b316b9c75774ab77))


### Bug Fixes

* disable GitHub Actions cache and release-client auto-trigger ([8fd517b](https://github.com/marcszy91/elli-charge-api/commit/8fd517b28070e1308ea597530fb6831d042dedc4))
* resolve GitHub Actions workflow issues and linting errors ([227866a](https://github.com/marcszy91/elli-charge-api/commit/227866ac4f3da8575d7956a3d03478ff69961cb4))

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of Elli Charging API
- OAuth2 PKCE authentication
- FastAPI endpoints for charging stations and sessions
- Docker support with multi-stage builds
- CI/CD pipeline with GitHub Actions
- Conventional commits enforcement
- Automatic changelog generation
- Pre-commit hooks for code quality
