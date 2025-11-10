# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.40] - 2025-01-12
### Added
- **Offline Prompt Evaluation**: New `PromptEvaluator` class for immediate local evaluation during development
- **Template-Based Evaluation**: Comprehensive evaluation of prompt templates with variable substitution
- **Evidently Integration**: Updated to Evidently 0.7.9 for advanced text metrics and reporting
- **Evaluation Configuration**: `EvaluationConfig` and `EvaluationReport` dataclasses for flexible evaluation setup
- **HTML/JSON Reports**: Automatic generation of evaluation reports with custom styling
- **Graceful Degradation**: Optional evaluation module that works when evidently is not installed
- **Manual Release Process**: GitHub release-based deployment instead of automatic releases
- **Release Process Documentation**: Comprehensive guide for manual releases

### Changed
- **Enhanced Security**: All MLflow operations now route through secure BFF gateway
- **Google Cloud Storage Support**: Native GCS integration for datasets and artifacts
- **Prompt Management Documentation**: Corrected to reflect MongoDB-based storage (not MLflow registry)
- **README Documentation**: Added comprehensive offline vs online evaluation guide
- **Release Workflow**: Switched from automatic to manual GitHub release-triggered deployment
- **Version Verification**: Added validation that GitHub tags match pyproject.toml versions

### Fixed
- **MLflow Token Expiration**: Simplified approach for handling expired tokens
- **Evidently API Compatibility**: Resolved issues with Evidently 0.7.x API changes
- **Documentation Accuracy**: Corrected prompt management implementation details

### Deprecated
- **Automatic Releases**: Auto-version-bump workflow disabled in favor of manual control

## [1.1.39] - 2024-12-20
### Added
- Enhanced security architecture with MLflow no longer directly exposed
- Complete audit logging for MLflow operations
- Network isolation for MLflow in internal-only network
- Centralized authentication and authorization through BFF gateway

### Changed
- All MLflow traffic now proxied through secure BFF gateway
- Automatic secure MLflow tracking URI configuration
- Backward compatible with existing workflows

### Security
- MLflow endpoints never exposed publicly
- All requests authenticated at the gateway
- Enhanced protection against security vulnerabilities

## [1.1.38] - 2024-12-15
### Added
- Google Cloud Storage integration for datasets and artifacts
- Multi-cloud support (Azure + GCS)
- Service account support for GCS authentication

### Changed
- Improved dataset client with GCS support
- Enhanced artifact storage capabilities

## [1.1.37] - 2024-12-10
### Added
- Enhanced prompt management with version control
- Prompt aliases for production deployment
- MongoDB-based prompt storage with versioning

### Changed
- Improved prompt client API
- Better integration with LLM workflows

## [1.1.36] - 2024-12-01
### Added
- Foundation integration with autonomize-core v0.1.7
- Enhanced authentication with ModelhubCredential
- Improved HTTP client management
- Comprehensive exception handling
- Better SSL certificate support

### Changed
- Migrated from custom HTTP client to autonomize-core BaseClient
- Standardized authentication across all clients
- Improved error handling and logging

### Fixed
- Various authentication and connection issues
- SSL/TLS certificate validation problems

## [1.1.35] - 2024-11-20
### Added
- Initial prompt management capabilities
- Basic MLflow integration improvements

### Changed
- Enhanced MLflow client functionality
- Improved dataset management

### Fixed
- Various minor bugs and improvements

---

## Release Notes

### v1.1.40 Highlights

This release introduces **offline prompt evaluation** capabilities, allowing developers to get immediate feedback during prompt development without requiring backend services. Key features include:

- **Instant Evaluation**: Local evaluation using Evidently for comprehensive text metrics
- **Template Testing**: Evaluate prompt templates with multiple variable combinations
- **Development Workflow**: Perfect for rapid iteration during prompt engineering
- **Dual Evaluation**: Both online (dashboard) and offline (local) evaluation options
- **Manual Releases**: Full control over release timing via GitHub releases

### Migration Guide

#### Upgrading to v1.1.40

1. **Install with evaluation support**:
   ```bash
   pip install "autonomize-model-sdk[monitoring]"
   ```

2. **New offline evaluation usage**:
   ```python
   from modelhub.evaluation import PromptEvaluator
   evaluator = PromptEvaluator()
   report = evaluator.evaluate_offline(data)
   ```

3. **Manual release process**:
   - Update version in pyproject.toml
   - Create GitHub release draft
   - Publish release to trigger PyPI deployment

#### Security Updates (v1.1.39+)

- No code changes required
- MLflow operations automatically secured
- All existing code continues to work unchanged
- Enhanced security with no performance impact

### Support

For questions about releases or new features:
- Check the [documentation](https://docs.autonomize.ai/modelhub-sdk)
- Review [examples](./examples/)
- Open issues on GitHub
- Contact support via #modelhub-support
